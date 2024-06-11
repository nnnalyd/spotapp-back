#this whole module is needed to access the spotify api

from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import random

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

#standard urls for api interaction
API_URL = 'https://api.spotify.com/v1/'

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization" : "Bearer " + token}

#searching for artist
def search_for(token, name):
    url = f"{API_URL}search"
    headers = get_auth_header(token)
    query  = f"?q={name}&type=track%2Cartist&limit=5"
    query_url = url + query
    result = get(query_url, headers=headers)

    artists = json.loads(result.content)['artists']['items']
    tracks = json.loads(result.content)['tracks']['items']

    dictTracks = [
        {
            'artist_name' : item['album']['artists'][0]['name'],
            'track_name' : item['name'],
            'img_url' : item['album']['images'][0]['url'],
            'id' : item['id'],
            'type' : item['type'],
            'preview_url': getTrack(token, item['id'])
        }
        for item in tracks
    ]
    
    dictArtists = [
        {
            'artist_name' : item['name'],
            'img_url' : item['images'][0]['url'],
            'id' : item['id'],
            'type' : item['type']
        }
        for item in artists
        if item['images'] #if the images item is found then we can create the key and value, if not then we just skip it and add everything else
    ]

    return dictTracks, dictArtists

#getting track preview url (do not change until later, called in app.py, be careful)
def getTrack(token,id):
    url = f"{API_URL}tracks/{id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    preview_url = json.loads(result.content)['preview_url']

    return preview_url

def getRecommendations(token,seed,id):
    url = f"{API_URL}recommendations?limit=50&seed_{seed}={id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)['tracks']
    dict = [
        {
            'track_name' : item['name'],
            'artist_name' : item['artists'][0]['name'],
            'track_cover' : item['album']['images'][0]['url'],
            'track_id' : item['id']
        }
        for item in json_result
    ]
    return dict

#getting newReleases from api
def newReleases(token):
    url = f"{API_URL}browse/new-releases?limit=4"
    headers = get_auth_header(token)
    
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    data = json_result['albums']['items']
    
    dict = [
        {
            'artist' : item['artists'][0]['name'],
            'album' : item['name'],
            'albumC' : item['images'][0]['url']
        }
        for item in data
    ]
    
    return dict

def userPlaylists(token):
    url = f'{API_URL}me/playlists?limit=5'
    headers = get_auth_header(token)
    
    result = get(url, headers=headers)
    json_result = json.loads(result.content)['items']

    dict = [
        {
            'playlist_name' : item['name'],
            'playlist_img' : item['images'][0]['url']
        }
        for item in json_result
    ]
    
    return dict
    
def userFollowedArtists(token):
    url = f'{API_URL}me/following?type=artist&limit=50'
    headers = get_auth_header(token)
    result = get(url, headers=headers)

    json_result = json.loads(result.content)['artists']['items']
    
    dict = [
        {
            'artist_name': item['name']
        }
        for item in json_result
    ]
    
    return dict

def getUserid(token):
    url = f'{API_URL}me'
    headers = get_auth_header(token)

    result = get(url, headers=headers)

    id = json.loads(result.content)['id']
    return id

def createPlaylist(token,id, playlist_name,item):
    url = f'{API_URL}users/{id}/playlists'
    headers = {
        "Authorization" : "Bearer " + token,
        "Content-Type" : 'application/json'
        }
    data = {
        "name": f"{playlist_name}",
        "description" : f"Playlist based on {item}",
        "public" : False
    }

    result = post(url, headers=headers, json=data)
    results = json.loads(result.content)

    return results

def addPlaylist(token, id, dict):
    url = f'{API_URL}playlists/{id}/tracks'
    headers = {
        "Authorization" : "Bearer " + token,
        "Content-Type" : 'application/json'
        }
    trackIds = []
    for item in dict:
        trackIds.append(f'spotify:track:{item['track_id']}')

    data = {
        'uris': trackIds
    }

    result = json.loads(post(url, headers=headers, json=data))
    return result

def topTracks(token, limit):
    url = f'{API_URL}me/top/tracks?limit={limit}'
    headers = get_auth_header(token)

    result = get(url, headers=headers)

    tracks = [
        {
            'artist_name' : item['artists'][0]['name'],
            'track_name': item['name'],
            'url' : item['album']['images'][0]['url']
        }
        for item in json.loads(result.content)['items']
    ]

    return tracks

def getDiscovery(token):
    #getting discovery channel playlist, should make an automated playlist that gathers different genre music based on user listening.
    pass

def createDiscovery(token): #token must be session['access-token']
    url = f'{API_URL}users/{id}/playlists'
    playlist_name = "Discovery Channel"
    headers = {
        "Authorization" : "Bearer " + token,
        "Content-Type" : 'application/json'
        }
    data = {
        "name": f"{playlist_name}",
        "description" : f"Your weekly discovery channel",
        "public" : False
    }

    topTracks = topTracks(token, 20) #think i was grabbing different genres here
    genreCount = {}
    for item in topTracks:
        if item in genreCount:
            genreCount[f'{item}'] += 1
        else:
            genreCount.append(f'{item}')
            genreCount[f'{item}'] = 0

    print(genreCount)

    return genreCount

#getting user liked songs
def getLikedSongsIDs(token,offset):
    url = f'{API_URL}me/tracks?limit=50&{offset}'
    headers=get_auth_header(token)
    result = get(url, headers=headers)

    items = [
        {
            'id': item['track']['id']
        }
        for item in json.loads(result.content)['items']
    ]
    return items

def checkSaved(token,id):
    url = f'{API_URL}me/tracks/contains?ids={id}'
    headers=get_auth_header(token)
    result = get(url, headers=headers)

    boolean = json.loads(result.content)

    return boolean

#big algo for getting average audio feature values
def getAudioFeatures(token, list):
    listIDs=[]
    i=0
    '''
    try:
        for item in list:
            listIDs.append(item['id'])
    except Exception:
    '''
    while i < len(list):
        a = 0
        for item in list[i]:
            print(checkSaved(token,item['id']))
            listIDs.append(item['id'])
            print(f'appended {a}')
            a +=1
        i +=1

    i = 0
    dict = []
    while i <= 4:
        id = listIDs[random.randint(0,len(listIDs))]
        dict.append(id)
        i +=1
    ids = '%2C'.join(dict)

    url = f'{API_URL}audio-features?ids={ids}'
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    features = json.loads(result.content)['audio_features']
    totalFeatures = {
        "target_acousticness=": 0,
        "target_danceability=": 0,
        "target_energy=": 0,
        "target_instrumentalness=": 0,
        "target_liveness=": 0,
        "target_loudness=": 0,
        "target_speechiness=": 0,
        "target_tempo=": 0,
        "target_valence=": 0
    }
    
    for item in features:
        totalFeatures['target_acousticness='] += item['acousticness']
        totalFeatures['target_danceability='] += item['danceability']
        totalFeatures['target_energy='] += item['energy']
        totalFeatures['target_instrumentalness='] += item['instrumentalness']
        totalFeatures['target_liveness='] += item['liveness']
        totalFeatures['target_loudness='] += item['loudness']
        totalFeatures['target_speechiness='] += item['speechiness']
        totalFeatures['target_tempo='] += item['tempo']
        totalFeatures['target_valence='] += item['valence']
    featuresList = []
    for item in totalFeatures:
        totalFeatures[item] = totalFeatures[item]/10
        featuresList.append(item+str(totalFeatures[item]))

    '''
    totalFeatures['acousticness'] = totalFeatures['acousticness']/10
    totalFeatures['danceability'] = totalFeatures['danceability']/10
    totalFeatures['energy'] = totalFeatures['energy']/10
    totalFeatures['instrumentalness'] = totalFeatures['instrumentalness']/10
    totalFeatures['liveness'] = totalFeatures['danceability']/10
    totalFeatures['loudness'] = totalFeatures['loudness']/10
    totalFeatures['speechiness'] = totalFeatures['speechiness']/10
    totalFeatures['tempo'] = totalFeatures['tempo']/10
    totalFeatures['valence'] = totalFeatures['valence']/10
    '''
        
    return featuresList, ids

def getRecommendationsAudioFeatures(token, featuresList,ids):
    string = '&'.join(featuresList)
    '''
    f'target_acousticness={totalFeatures['acousticness']}\
        &target_danceability={totalFeatures['danceability']}\
            &target_energy={totalFeatures['energy']}\
            &target_instrumentalness={totalFeatures['instrumentalness']}\
            &target_liveness={totalFeatures['liveness']}\
            &target_loudness={totalFeatures['loudness']}\
            &target_speechiness={totalFeatures['speechiness']}\
            &target_tempo={totalFeatures['tempo']}\
            &target_valence={totalFeatures['valence']}'
    '''
    url = f'{API_URL}recommendations?limit=50&seed_tracks={ids}&{string}'
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    response = json.loads(result.content)['tracks']
    dict = [
        {
            'track_name' : item['name'],
            'artist_name' : item['artists'][0]['name'],
            'track_cover' : item['album']['images'][0]['url'],
            'track_id' : item['id']
        }
        for item in response
    ]
    return dict

if __name__ == "__main__":
    token = get_token()
    name = input("Name: ")
    id = search_for(token, name)
    print(id)
    