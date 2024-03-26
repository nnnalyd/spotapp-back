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
def search_for(token, type, name):
    url = f"{API_URL}search"
    headers = get_auth_header(token)
    query  = f"?q={name}&type={type}&limit=5"
    #type is what we are looking for, basically filters

    query_url = url + query
    result = get(query_url, headers=headers)
    
    if type == 'artist':
        json_result = json.loads(result.content)['artists']['items']
    else:
        json_result = json.loads(result.content)['tracks']['items']

    dict = []
    
    length = int(len(json_result))
    i = 0
    
    while i < length:
        dict.append({
            'name' : json_result[i]['name'],
            'id' : json_result[i]['id']
        })
        i += 1
        
    return dict

#getting specified artist from api
def getArtist(token):
    url = f"{API_URL}artists/2h93pZq0e7k5yf4dywlkpM"
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

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
    url = f'{API_URL}me/playlists?limit=1'
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
    type = 'artist'
    name = input("Name: ")
    id = search_for(token,type,name)
    print(id)
    