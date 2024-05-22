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
        if item['images']
    ]

    return dictTracks, dictArtists

#getting specified artist from api
def getArtist(token):
    url = f"{API_URL}artists/2h93pZq0e7k5yf4dywlkpM"
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

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

def topTracks(token):
    url = f'{API_URL}me/top/tracks'
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    print(json.loads(result.content)['items'])

    tracks = [
        {
            'track_name': item['name'],
            'url' : item['album']['images'][0]['url']
        }
        for item in json.loads(result.content)['items']
    ]

    return tracks

if __name__ == "__main__":
    token = get_token()
    name = input("Name: ")
    id = search_for(token, name)
    print(id)
    