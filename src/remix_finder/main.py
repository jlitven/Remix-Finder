"""
Remix Finder Website.

Find remixes of artists using the Spotify Web API.

Joshua Litven June 2016.
"""
import base64
import urllib
import json
import requests
import time
import re
import os
from flask import Flask, request, redirect, g, render_template, url_for
from spotify_adaptors import Artist, User


app = Flask(__name__)

#  Client Keys
CLIENT_ID = os.environ['SPOTIPY_CLIENT_ID']
CLIENT_SECRET = os.environ['SPOTIPY_CLIENT_SECRET']

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
SCOPE = 'playlist-modify-public'

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    "client_id": CLIENT_ID
}

# Server data
ARTIST = None
USER = None
PLAYLISTS = None
USER_PLAYLIST_KEY = ''

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

    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]

    if access_token:
        global USER
        USER = User(access_token)
        playlist = [p for p in PLAYLISTS if p['key'] == USER_PLAYLIST_KEY][0]
        USER.create_playlist(playlist['tracks'], playlist['name'])
        playlist['created'] = True
        return redirect(url_for('results'))
    else:
        return "Couldn't obtain access token!"


@app.route('/results', methods=['GET', 'POST'])
def results():
    """Return the search results or create a playlist."""
    if request.method == 'GET':
        return render_template("results.html",
                               artist=ARTIST,
                               playlists=PLAYLISTS)
    else:
        global USER_PLAYLIST_KEY
        USER_PLAYLIST_KEY = request.form['key']
        return redirect(url_for('login'))

def wrap(name):
    """Wrap the artist name in a span for styling."""
    return "<span class='artist_name'>{}</span>".format(name)

def create_playlists(artist):
    """Create a dict of remix playlists."""

    num_remixes = 10
    num_artists = 1
    playlists = {}
    wrapped_name = wrap(artist.name)
    artist_name = artist.name

    # remixed_by_artist playlist
    remixed_by_artist = {
        'tracks': artist.get_remixes(num_remixes),
        'name': 'Remixed By ' + artist_name,
        'created': False,
        'key': 'remixed_by_artist'
    }

    # artist_remixed playlist
    artist_remixed = {
        'tracks': artist.get_tracks_others_remixed(num_remixes),
        'name': artist_name + ' Remixed',
        'created': False,
        'key': 'artist_remixed'
    }

    # related_remixes playlist
    related_artists = artist.get_related_artists()[:num_artists]
    tracks = sorted([r for a in related_artists for r in a.get_remixes()],
                    key=lambda track: track.popularity)

    related_remixes = {
        'tracks': tracks,
        'name': artist_name + ' Related Remixes',
        'created': False,
        'key': 'related_remixes'
    }

    playlists = [
        remixed_by_artist,
        artist_remixed,
        related_remixes
    ]

    # Add styled names for html
    for p in playlists:
        p['styled_name'] = re.sub(artist_name, wrapped_name, p['name'])

    return playlists

@app.route('/<query>')
def load_results():
    """Load the playlists from the artist query."""
    global ARTIST, PLAYLISTS
    artist_query = request.form['query']
    ARTIST = Artist.create_from_query(artist_query)
    PLAYLISTS = create_playlists(ARTIST)
    return redirect(url_for('results'))

@app.route('/', methods=['GET', 'POST'])
def search():
    """The search page."""
    if request.method == 'POST':
        global ARTIST, PLAYLISTS
        artist_query = request.form['query']
        ARTIST = Artist.create_from_query(artist_query)
        PLAYLISTS = create_playlists(ARTIST)
        return redirect(url_for('results'))

    return render_template('search.html')

if __name__ == "__main__":
    app.run(debug=True, port=PORT)
