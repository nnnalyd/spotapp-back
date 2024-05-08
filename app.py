from flask import Flask, render_template, redirect, request, jsonify
import spotifyAPI as s
import os
import urllib.parse
import requests
from datetime import *
import json

app = Flask(__name__)

REDIRECT_URI = "http://127.0.0.1:8000/callback"
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = "https://accounts.spotify.com/api/token"

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

token = s.get_token()

newRelease = s.newReleases(token)

session = {}


@app.route('/')
def index():
   return render_template("Home_Page.html")

   
@app.route('/login')
def login():
   scope = "user-read-private user-read-email user-follow-read"
   
   params = {
      'client_id' : client_id,
      'response_type' : 'code',
      'scope' : scope,
      'redirect_uri' : REDIRECT_URI,
      'show_dialog': True
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
   
   data = s.userPlaylists(session['access_token'])[0]
   print(data)
   return render_template('User_Playlists.html', data=data)

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
      name = str(request.form.get("name"))
      seed = str(request.form.get("seed"))
      id = s.search_for(token,seed,name)[0]['id']
      print(id)
      seed = f'{seed}s'
      data = s.getRecommendations(token,seed,id)
      return render_template("user_recommendations.html",data=data)
   return render_template("user_recommendations.html")

@app.route('/home')
def home():
   return render_template('home.html')

#def home():
   #return render_template('test.html', data=newRelease, dataS = search)
   
if __name__ == '__main__':
   app.run(host='0.0.0.0', debug=True)