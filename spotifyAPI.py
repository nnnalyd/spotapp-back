#this whole module is needed to access the spotify api

from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json

#this grabs my client_id and client_secret, should not be shared and is stored by server only
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# standard urls for api interaction
API_URL = 'https://api.spotify.com/v1/'

# Grabbing the access token so we can perform requests to and from spotify API with our credentials
def get_token(): #ipoed
    auth_string = client_id + ":" + client_secret # an authorisation string that is encoded
    auth_bytes = auth_string.encode("utf-8") # encoded to utf-8
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8") # encoded to base 64, essential for making sure all client data is secure

    url = "https://accounts.spotify.com/api/token" # url endpoint for our access token
    headers = { # headers of the request, auth based on our string, and the content type being data type of what we are asking for
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"} # what we are specifically asking for, auth based on our credentials
    result = post(url, headers=headers, data=data) # POST request
    json_result = json.loads(result.content) # response
    token = json_result["access_token"] # our access token stored in variable and returned
    return token

# getting our authorisation that we are allowed to make the request using our token.
def get_auth_header(token):
    return {"Authorization" : "Bearer " + token}

# searching for artist/track based on the user query and structuring response
def search_for(token, name):
    url = f"{API_URL}search" # url endpoint for request
    headers = get_auth_header(token) # headers with auth
    query  = f"?q={name}&type=track%2Cartist&limit=5" # our query string
    query_url = url + query # url and query string is joined so we have a full url to request from
    result = get(query_url, headers=headers) # GET request

    #if we get back no results we can just return a stub that says there is no results
    try: 
        artists = json.loads(result.content)['artists']['items'] # artists response to this dict
    except Exception:
        print("No results")
        return False
    try:
        tracks = json.loads(result.content)['tracks']['items'] # tracks response to this dict
    except Exception:
        print("No results")
        return False

    # appending all tracks into this dictionary
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
    
    # appending all artists to this dictionary
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

    return dictTracks, dictArtists # return the search results as a tuple

# getting track preview url (do not change until later, called in app.py, be careful)
def getTrack(token,id):
    url = f"{API_URL}tracks/{id}" # url endpoint with id of track selected
    headers = get_auth_header(token) # headers with auth
    result = get(url, headers=headers) # GET request
    preview_url = json.loads(result.content)['preview_url'] # get preview url from response

    return preview_url # return preview url

# would be called after the search results when the user picks what they want recommendations from,
# when called id and seed of the item will be passed
def getRecommendations(token,seed,ids): #ipoed
    url = f"{API_URL}recommendations?limit=50&seed_{seed}={ids}" # passed id and seed are placed into url endpoint
    headers = get_auth_header(token) # headers with auth
    result = get(url, headers=headers) # GET request
    json_result = json.loads(result.content)['tracks'] # response

    # structuring all items into this dictionary
    dict = [
        {
            'track_name' : item['name'],
            'artist_name' : item['artists'][0]['name'],
            'track_cover' : item['album']['images'][0]['url'],
            'track_id' : item['id']
        }
        for item in json_result
    ]
    items =[]
    # checking if item is already in users saved and then removing and adding not saved songs to the list.
    for item in dict:
        items.append(item['track_id'])
    trackIds = '%2C'.join(items)
    saved = checkSaved(token, trackIds) # returns a list of booleans
    print(saved)
    recommendations = [] # new list for the items that are not saved
    index = 0
    for i in saved: # for every item i in the saved list
        print(i) # stub to check what boolean
        if i == True: # true indicates if it has been saved
            print('already saved in user playlist')
            index += 1 # next boolean
        else: # whether a false is passed
            print('item not saved')
            for item in dict:
                if item['track_id'] == items[index]: # iterating through the track ids to append the unsaved item
                    recommendations.append(item)
            index += 1
    return recommendations

# getting the newest releases of songs from api
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

# creating playlist
def createPlaylist(token,id, playlist_name,item):
    url = f'{API_URL}users/{id}/playlists' # url endpoint of making playlist
    headers = {
        "Authorization" : "Bearer " + token,
        "Content-Type" : 'application/json'
        }
    data = { # data we want to give to api so we can specify the name and descripition and whether or not it should be public or not
        "name": f"{playlist_name}",
        "description" : f"Playlist based on {item}",
        "public" : False
    }

    result = post(url, headers=headers, json=data) # POST request to make playlist
    results = json.loads(result.content)

    return results # returning stub if been made so we can confirm success

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

# checking if a string of ids is saved within the users liked songs
# used in recommendations filtering
def checkSaved(token,id):
    url = f'{API_URL}me/tracks/contains?ids={id}'
    headers=get_auth_header(token)
    result = get(url, headers=headers)

    # the response from the request
    booleans = json.loads(result.content)

    return booleans # when called we get the array of booleans

# get the users id, so we can use it to post playlists and add to playlists
def getUserID(token):
    url = f'{API_URL}me'
    headers = get_auth_header(token)
    result = get(url, headers=headers)

    id = json.loads(result.content)['id'] # we want to return id and stuff

    return id

# gathers the users top tracks
def topTracks(token, limit):
    url = f'{API_URL}me/top/tracks?limit={limit}' # url as usual
    headers = get_auth_header(token) # usual

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

# testing any functions within here instead of the webpage, just for checking return statements/stubs
if __name__ == "__main__":
    token = get_token()
    name = input("Name: ")
    output = search_for(token, name)
    print(output)
    