from flask import Flask, render_template, redirect, request, jsonify
import spotifyAPI as s
import os
import urllib.parse
import requests
from datetime import *
import json

app = Flask(__name__)

# standard urls and end points so i don't have to rewrite all the time
API_URL = 'https://api.spotify.com/v1/'
REDIRECT_URI = "http://127.0.0.1:5000/callback"
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = "https://accounts.spotify.com/api/token"

client_id = os.getenv("CLIENT_ID") # getting client id (global)
client_secret = os.getenv("CLIENT_SECRET") # getting client secret (global)

token = s.get_token() # global token

newRelease = s.newReleases(token) # getting all new releases

session = {} # session dictionary (outside since it is global)

# is this even being used? lol
def get_auth_header(token):
   return {"Authorization" : "Bearer " + token}

# landing page for first time use
@app.route('/')
def index():
   return render_template("Home_Page.html")

# just a route to log user out and remove the access token
@app.route('/logout')
def logout():
   session['access_token'] = 'None'
   return redirect('/')

#----------------------------------SPOTIFY ESSENTIALS DO NOT TOUCH-------------------------------------------------#

# our login route allows to get authentication and permissions from user, spotify handles login redirect and gives us
# access tokens for the program
@app.route('/login')
def login():
   # scope defines the permissions our user can give us, they have the option to decline auth
   scope = "user-read-private user-read-email user-library-read user-top-read user-follow-read playlist-modify-public playlist-modify-private"
   
   # set of parameters that are placed into login route to ask the user what we want
   params = {
      'client_id' : client_id,
      'response_type' : 'code',
      'scope' : scope,
      'redirect_uri' : REDIRECT_URI,
      'show_dialog': True # set to true if we want to always show dialog, set as false for testing
   }

   auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
   
   return redirect(auth_url)

# callback occurs after login route, we assign our access tokens into our session 
@app.route('/callback')
def callback():
   if 'error' in request.args: # if an error is encountered we reroute and display error
      return jsonify({'error' : request.args['error']})
   
   # a set of request arguments, defining what we want, and giving auth to prove we are allowed to have it
   if 'code' in request.args:
      req_body = {
         'code': request.args['code'],
         'grant_type': "authorization_code",
         'redirect_uri': REDIRECT_URI,
         'client_id': client_id,
         'client_secret': client_secret
      }
   # we now ask for token info using our request body as its data, we are then given the current login sessions info
   response = requests.post(TOKEN_URL, data=req_body)
   token_info = response.json()
   
   # assigning our session and the tokens we got from our request above
   session['access_token'] = token_info['access_token'] #access tokens given to us by spotify are stored in a session
   session['refresh_token'] = token_info['refresh_token'] #refresh token required when checking if we still have an access token
   session['expires_at'] = datetime.now().timestamp() + token_info['expires_in'] #our tokens have expiration times set by spotify
   id = s.getUserID(session['access_token'])
   session['id'] = id
   
   return redirect('/home') 

# refresh route refreshes our auth with the user, giving us our tokens again
@app.route('/refresh-token')
def refresh_token():
   if 'refresh_token' not in session: #if our refresh token isnt found, we reroute to login so we can restart token process
      return redirect('/login')
   
   # if the expiration time has been met we request another token.
   if datetime.now().timestamp() > session['expires_at']:
      req_body = {
         'grant_type': 'refresh_token',
         'refresh_token': session['refresh_token'],
         'client_id': client_id,
         'client_secret': client_secret
      }
   
   # requesting the token info again
   response = requests.post(TOKEN_URL, data=req_body)
   new_token_info = response.json()

   # assigning our info into our session as done before in /callback
   session['access_token'] = new_token_info['access_token']
   session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']     
   
   return redirect('/home')

#-------------------------------------------------------------------------------------------------------------#

# ----completed---- this first route gets a user query and displays related content
# route for displaying the user search option. The posted search terms are then sent to the next route (below)
@app.route('/user-recommendations', methods=["GET", "POST"])
def userRecommendations():
   if 'access_token' not in session:
      return redirect('/login')
   
   if datetime.now().timestamp() > session['expires_at']:
      return redirect('/refresh-token')
   
   if request.method == "POST": # if we recieve a post request from the submit button in the website we continue
      name = '' 
      name = str(request.form.get("name")) # locating the name tag we placed for our form in html, assign input into variable name
      try:
         dictTracks, dictArtists = s.search_for(token, name) # from the name we inputted, we search for anything that has this name
      except None:
         return render_template("noresults.html")
      return render_template("user_searchresults.html", tracks=dictTracks,artists=dictArtists) #rendering the template with the dictionarys we got from search
   return render_template("user_recommendations.html") # default to rendering the blank recommendations screen

# ----completed---- reroute after post request from above and this one gets the actual recommendations
# this route uses the search results we got from the previous route and then calls recommendations based on them.
@app.route('/user-recommendations/results', methods=["GET", "POST"])
def userRecommendations_results():
   if 'access_token' not in session:
      return redirect('/login')
   
   if datetime.now().timestamp() > session['expires_at']:
      return redirect('/refresh-token')
   
   # when we recieve the post request from whatever option the user wanted we continue
   if request.method == "POST":
      id ='' 
      seed=''
      id = str(request.form.get('id')) # assigning id
      seed = str(request.form.get('seed')) # assigning seed (whether its a track/artist)

      session['name'] = str(request.form.get('name')) # placing the name of the item the user placed into our session

      recommendations = s.getRecommendations(session['access_token'],seed,id) #get recommendations from the users input

      session['recommendations'] = json.dumps(recommendations) # placing the recommendations into our session so we can access it later

      return render_template("recommendations.html", data=recommendations) # render the recommendations
   return render_template("recommendations.html")

# ----- creating the playlist route ------
# route that creates playlists if the user chooses to create one, redirects to a playlist made prompt
@app.route('/create-playlist', methods=["GET", "POST"])
def create_Playlist():
   if 'access_token' not in session:
      return redirect('/login')
   
   if datetime.now().timestamp() > session['expires_at']:
      return redirect('/refresh-token')
   
   # post requests from user inputs
   if request.method == "POST":
      # getting the id of the user from the session
      id = session['id']
 
      # create a playlist using the users id and name from the recommendations
      idPlaylist = s.createPlaylist(session['access_token'], id, 'playlist', session['name'])['id']
      
      # we get the recommendations list from our previous route and load it into our current route
      recommendations_json = session.get('recommendations', '{}')
      recommendations = json.loads(recommendations_json)
      
      # using this list we then add the items into our playlist that we made before
      try:
         s.addPlaylist(session['access_token'], idPlaylist, recommendations)
      except TypeError: # at some point we get a typeerror (not sure why lol), but all items do get loaded
         return render_template("playlistsmade.html") # render that the playlist got made
      return render_template("playlistsmade.html")
   return render_template("playlistsmade.html")

# -----the home page after the login route------
# home page of the website, nothing too fancy, we just display everything the website holds, and also just some new music
@app.route('/home')
def home():
   if 'access_token' not in session:
      return redirect('/login')
   
   if datetime.now().timestamp() > session['expires_at']:
      return redirect('/refresh-token')
   
   # just grabbing new releases and the users top tracks
   newReleases = s.newReleases(token)
   toptracks = s.topTracks(session['access_token'], 4)
   
   # they get displayed here for the user to see new music that got released
   return render_template('home.html', newrelease=newReleases, toptracks=toptracks)

# ------testing functions route-----
# a test route for testing any html and python passing, helps when debugging and seeing what is gathered
@app.route('/test')
def test():
   if 'access_token' not in session:
      return redirect('/login')
   
   if datetime.now().timestamp() > session['expires_at']:
      return redirect('/refresh-token')
   
   return jsonify(s.getDiscovery(session['access_token']))

# this is the main initialise of the program, we run the app on the local host server
if __name__ == '__main__':
   app.run(host='0.0.0.0', debug=True) # set to false once on publish
