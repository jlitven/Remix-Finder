"""
Remix Finder Website.

Find remixes of artists using the Spotify Web API.

Joshua Litven June 2016.
"""
import base64
import urllib
import json
import requests
from flask import Flask, request, redirect, g, render_template, url_for
from spotify_adaptors import Artist, User


app = Flask(__name__)

#  Client Keys
CLIENT_ID = "e74c52988f6d4bcebb36970a423d348d"
CLIENT_SECRET = "0edc87deae1a4611a97b6cebef262136"

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)


# Server-side Parameters
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 8080
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "user-follow-modify user-read-email"

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    "client_id": CLIENT_ID
}

# Server data
ARTIST = None
USER = None
PLAYLIST_TRACKS = None
PLAYLIST_NAME = ""
CREATED_1 = False
CREATED_2 = False

@app.route("/login")
def login():
    """Authorize the Spotify user."""
    url_args = "&".join(["{}={}".format(key, urllib.quote(val))
                        for key, val in auth_query_parameters.iteritems()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)

@app.route("/callback/q")
def callback():
    """Obtain the authorization token and create the remix playlist."""
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI
    }
    base64encoded = base64.b64encode("{}:{}".format(CLIENT_ID, CLIENT_SECRET))
    headers = {"Authorization": "Basic {}".format(base64encoded)}
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=headers)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]

    if access_token:
        global USER
        USER = User(access_token)
        USER.create_playlist(PLAYLIST_TRACKS, PLAYLIST_NAME)
        return redirect(url_for('results'))
    else:
        return "Couldn't obtain access token!"

@app.route('/results/', methods=['GET', 'POST'])
def results():
    """Return the results page."""
    artist_remixed = ARTIST.get_remixes()
    others_remixed = ARTIST.get_tracks_others_remixed()
    #related_artists = ARTIST.get_related_artists()[:10]
    #related_remixes = []
    #for rel_artist in related_artists:
     #   remixes = rel_artist.get_remixes()
      #  related_remixes.extend(remixes)

    if request.method == 'GET':
        return render_template("results.html",
                               artist_name=ARTIST.name,
                               artist_image_url=ARTIST.image_url,
                               artist_remixed=artist_remixed,
                               others_remixed=others_remixed,
                               created_1=CREATED_1,
                               created_2=CREATED_2)
    else:
        # Create the playlist tracks and login the user
        global PLAYLIST_TRACKS, PLAYLIST_NAME, CREATED_1, CREATED_2
        if request.form['submit'] == 'artist_remixed':
            PLAYLIST_TRACKS = artist_remixed
            PLAYLIST_NAME = 'Remixed by ' + ARTIST.name
            CREATED_1 = True
        else:
            PLAYLIST_TRACKS = others_remixed
            PLAYLIST_NAME = ARTIST.name + ' Remixed'
            CREATED_2 = True
        return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def search():
    """The search page."""
    if request.method == 'POST':
        global ARTIST, CREATED_1, CREATED_2
        CREATED_1 = CREATED_2 = False
        artist_query = request.form['query']
        ARTIST = Artist.create_from_query(artist_query)
        return redirect(url_for('results'))

    return render_template('search.html')


if __name__ == "__main__":
    app.run(debug=True, port=PORT)
