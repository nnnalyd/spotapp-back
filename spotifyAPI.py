#this whole module is needed to access the spotify api

from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json

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
    query  = f"?q={name}&type=track%2Cartist&limit=20"

    query_url = url + query
    result = get(query_url, headers=headers)
    artists = json.loads(result.content)['artists']['items']
    tracks = json.loads(result.content)['tracks']['items']
    lenArtists = int(len(artists))
    lenTracks = int(len(tracks))
    i = 0

    dictArtists = []
    dictTracks = []

    dictTest = [
        {
            'artist_name' : item[i]['name'],
            'img_url' : item[i]['images'][0]['url'],
            'id' : item[i]['id'],
            'type' : item[i]['type']
        }
        for item in artists
    ]

    while i < lenArtists:
        dictArtists.append({
            'artist_name' : artists[i]['name'],
            'img_url' : artists[i]['images'][0]['url'],
            'id' : artists[i]['id'],
            'type' : artists[i]['type']
        })
        i += 1

    while i < lenTracks:
        dictTracks.append({
            'artist_name' : tracks[i]['album']['artists'][0]['name'],
            'track_name' : tracks[i]['name'],
            'img_url' : tracks[i]['album']['images'][0]['url'],
            'id' : tracks[i]['id'],
            'type' : tracks[i]['type'],
            'preview_url': getTrack(token, tracks[i]['id'], i)
        })
        i += 1
    '''
    if type == 'artist':
        json_result = json.loads(result.content)['artists']['items']
    else:
        json_result = json.loads(result.content)['tracks']['items']

    dict = []
    
    
    
    
    '''
    return dictTracks, dictTest

#getting specified artist from api
def getArtist(token):
    url = f"{API_URL}artists/2h93pZq0e7k5yf4dywlkpM"
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

def getTrack(token,id, i):
    url = f"{API_URL}tracks/{id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    preview_url = json.loads(result.content)['preview_url']
    print(preview_url)
    return preview_url

def getRecommendations(token,seed,id):
    url = f"{API_URL}recommendations?limit=50&seed_{seed}={id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)['tracks']
    dict = []
    
    length = int(len(json_result))
    i = 0
    
    while i < length:
        dict.append({
            'track_name' : json_result[i]['name'],
            'artist_name' : json_result[i]['artists'][0]['name'],
            'track_cover' : json_result[i]['album']['images'][0]['url']
        })
        i += 1
    print(dict)
    return dict

#getting newReleases from api
def newReleases(token):
    url = f"{API_URL}browse/new-releases?limit=3"
    headers = get_auth_header(token)
    
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    data = json_result['albums']['items']
    
    dict = []
    
    length = int(len(data))
    i = 0
    
    while i < length:
        dict.append({
            'artist' : data[i]['artists'][0]['name'],
            'album' : data[i]['name'],
            'albumC' : data[i]['images'][0]['url']
        })
        i += 1
        
    return dict

def userPlaylists(token):
    url = f'{API_URL}me/playlists?limit=5'
    headers = get_auth_header(token)
    
    result = get(url, headers=headers)
    json_result = json.loads(result.content)['items']

    dict = []
    
    length = int(len(json_result))
    i = 0
    
    while i < length:
        dict.append({
            'playlist_name' : json_result[i]['name'],
            'playlist_img' : json_result[i]['images'][0]['url']
        })
        i += 1
    print(dict)
    return dict
    
def userFollowedArtists(token):
    url = f'{API_URL}me/following?type=artist&limit=50'
    headers = get_auth_header(token)
    
    result = get(url, headers=headers)
    json_result = json.loads(result.content)['artists']['items']
    
    dict = []
    
    length = int(len(json_result))
    i = 0
    
    while i < length:
        dict.append({
            'artist name' : json_result[i]['name'],
        })
        i += 1
        
    return dict

if __name__ == "__main__":
    token = get_token()
    name = input("Name: ")
    id = search_for(token, name)
    print(id)
    