from flask import Flask, render_template, redirect, request, jsonify
import spotifyAPI as s
import os
import urllib.parse
import requests
from datetime import *
import json

app = Flask(__name__)

API_URL = 'https://api.spotify.com/v1/'
REDIRECT_URI = "http://127.0.0.1:5000/callback"
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = "https://accounts.spotify.com/api/token"

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

token = s.get_token()

newRelease = s.newReleases(token)

session = {}

def get_auth_header(token):
   return {"Authorization" : "Bearer " + token}

@app.route('/')
def index():
   return render_template("Home_Page.html")

@app.route('/logout')
def logout():
   session['access_token'] = 'None'
   return redirect('/')

@app.route('/login')
def login():
   scope = "user-read-private user-read-email user-library-read user-top-read user-follow-read playlist-modify-public playlist-modify-private"
   
   params = {
      'client_id' : client_id,
      'response_type' : 'code',
      'scope' : scope,
      'redirect_uri' : REDIRECT_URI,
      'show_dialog': False
   }
   
   auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
   
   return redirect(auth_url)

@app.route('/callback')
def callback():
   if 'error' in request.args:
      return jsonify({'error' : request.args['error']})
   
   if 'code' in request.args:
      req_body = {
         'code': request.args['code'],
         'grant_type': "authorization_code",
         'redirect_uri': REDIRECT_URI,
         'client_id': client_id,
         'client_secret': client_secret
      }
      
   response = requests.post(TOKEN_URL, data=req_body)
   token_info = response.json()
   
   session['access_token'] = token_info['access_token']
   session['refresh_token'] = token_info['refresh_token']
   session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']     
   
   return redirect('/home') 

@app.route('/playlists')
def get_playlists():
   if 'access_token' not in session:
      return redirect('/login')
   
   if datetime.now().timestamp() > session['expires_at']:
      return redirect('/refresh-token')
   
   data = s.userPlaylists(session['access_token'])

   return render_template('user_playlist.html', data=data)

@app.route('/followed-artists')
def followed_artists():
   if 'access_token' not in session:
      return redirect('/login')
   
   if datetime.now().timestamp() > session['expires_at']:
      return redirect('/refresh-token')
   
   artists = s.userFollowedArtists(session['access_token'])
   
   return jsonify(artists)

@app.route('/refresh-token')
def refresh_token():
   if 'refresh_token' not in session:
      return redirect('/login')
   
   if datetime.now().timestamp() > session['expires_at']:
      req_body = {
         'grant_type': 'refresh_token',
         'refresh_token': session['refresh_token'],
         'client_id': client_id,
         'client_secret': client_secret
      }
      
   response = requests.post(TOKEN_URL, data=req_body)
   new_token_info = response.json()
   
   session['access_token'] = new_token_info['access_token']
   session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']     
   
   return redirect('/home')

@app.route('/user-recommendations', methods=["GET", "POST"])
def userRecommendations():
   if 'access_token' not in session:
      return redirect('/login')
   
   if datetime.now().timestamp() > session['expires_at']:
      return redirect('/refresh-token')
   #recommended_tracks = s.getRecommendations(token,'artist', id)
   if request.method == "POST":
      name = ''
      name = str(request.form.get("name"))
      dictTracks, dictArtists = s.search_for(token, name)
      return render_template("user_searchresults.html", tracks=dictTracks,artists=dictArtists)
   return render_template("user_recommendations.html")

@app.route('/user-recommendations/results', methods=["GET", "POST"])
def userRecommendations_results():
   if 'access_token' not in session:
      return redirect('/login')
   
   if datetime.now().timestamp() > session['expires_at']:
      return redirect('/refresh-token')
   
   if request.method == "POST":
      id =''
      seed=''
      id = str(request.form.get('id'))
      seed = str(request.form.get('seed'))

      session['name'] = str(request.form.get('name'))

      recommendations = s.getRecommendations(token,seed,id)

      session['recommendations'] = json.dumps(recommendations)

      return render_template("recommendations.html", data=recommendations)
   return render_template("recommendations.html")

@app.route('/create-playlist', methods=["GET", "POST"])
def create_Playlist():
   if 'access_token' not in session:
      return redirect('/login')
   
   if datetime.now().timestamp() > session['expires_at']:
      return redirect('/refresh-token')
   if request.method == "POST":
      url = f'{API_URL}me'
      headers = get_auth_header(session['access_token'])

      result = requests.get(url, headers=headers)
      id = json.loads(result.content)['id']

      idPlaylist = s.createPlaylist(session['access_token'], id, 'playlist', session['name'])['id']
      
      recommendations_json = session.get('recommendations', '{}')
      recommendations = json.loads(recommendations_json)

      try:
         s.addPlaylist(session['access_token'], idPlaylist, recommendations)
      except TypeError:
         return render_template("playlistsmade.html")
      return render_template("playlistsmade.html")
   return render_template("playlistsmade.html")

@app.route('/home')
def home():
   if 'access_token' not in session:
      return redirect('/login')
   
   if datetime.now().timestamp() > session['expires_at']:
      return redirect('/refresh-token')
   
   newReleases = s.newReleases(token)
   toptracks = s.topTracks(session['access_token'], 4)
   getDiscovery = None

   return render_template('home.html', newrelease=newReleases, toptracks=toptracks)

@app.route('/test')
def test():
   if 'access_token' not in session:
      return redirect('/login')
   
   if datetime.now().timestamp() > session['expires_at']:
      return redirect('/refresh-token')
   
   list = s.getLikedSongsIDs(session['access_token'])


   return jsonify(s.getAudioFeatures(session['access_token'], list))
   
if __name__ == '__main__':
   app.run(host='0.0.0.0', debug=True)