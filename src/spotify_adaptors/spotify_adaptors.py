#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-06-16 13:11:10
# @Author  : Joshua Litven (jlitven@gmail.com)
# @Link    : https://github.com/jlitven
# @Version : $Id$

"""
Spotify Adaptors.

Wrappers for the Spotify API spotipy.
"""
import os
import sys
import spotipy
import spotipy.util as util
import pdb

SPOTIFY = spotipy.Spotify()
MY_USERNAME = '1212629687'

def get_results(spotify_func, limit, num_results, **vargs):
    """
    Return results from the spotify function.

    Args:
        spotify_func: The spotify function
        limit: The request limit for the spotify function
        num_results: The number of results to return
        **vargs: Other keyword arguments for the spotify function

        Output:
            result: A list of results.
    """
    results = []
    # TODO: Parallelize
    for i in range(0, num_results, limit):
        try:
            result = spotify_func(limit=limit, offset=i, **vargs)
            results.append(result)
        except:
            result = None
        if not result:
            break
    results = results[:num_results]
    return results

def query_spotify(query, type='track', num_results=10):
    """Return a list of spotify wrappers corresponding to a query."""
    results = get_results(SPOTIFY.search,
                          limit=10,
                          num_results=num_results,
                          q=query,
                          type=type)

    # Transform list of results to list of items
    items = [i for r in results for i in r[type + 's']['items']]

    if type == 'track':
            wrapper = Track
    elif type == 'artist':
        wrapper = Artist
    wrapped_results = [wrapper(i) for i in items]
    return wrapped_results

def unique_decorator(func):
    """
    Given a list of tracks from a func return uniquely named tracks.

    If multiple tracks have the same name, the track
    with the highest popularity is chosen.
    """
    def unique_func(*args, **kwargs):
        tracks = func(*args, **kwargs)
        unique_tracks = {}
        for track in tracks:
            if track.name in tracks:
                if track.popularity > tracks['name'].popularity:
                    unique_tracks['name'] = track
            else:
                unique_tracks[track.name] = track

        return sorted(unique_tracks.values(),
                      key=lambda track: track.popularity,
                      reverse=True)
    return unique_func

class User:
    """A Spotify user."""

    def __init__(self, token):
        """Create a user with the desired scope."""
        global SPOTIFY
        SPOTIFY = spotipy.Spotify(auth=token)
        self.profile = SPOTIFY.current_user()
        self.name = self.profile['display_name']
        self.uri = self.profile['uri']
        self.username = self.uri.split(':')[-1]

    @staticmethod
    def create_from_scope(scope, username=MY_USERNAME):
        """Create a user with the desired scope."""
        token = User.get_token(username, scope)
        return User(token)

    @staticmethod
    def get_token(username, scope):
        """Obtain an access token for the user."""
        token = util.prompt_for_user_token(
            username=username,
            scope=scope,
            client_id=os.environ['SPOTIPY_CLIENT_ID'],
            client_secret=os.environ['SPOTIPY_CLIENT_SECRET'],
            redirect_uri=os.environ['SPOTIPY_REDIRECT_URI'])
        return token

    def get_top_artists(self, num_results=20, time_range='medium_term'):
        """Get the user's top artists over a time range.

        Args:
            limit: Number of artists returned
            offset: Index of the first artist to return
            time_range: Over what time period the artists are computed
            Valid-values: short_term, medium_term, long_term
        Output:
            result: A list of artists.
        """
        results = get_results(SPOTIFY.current_user_top_artists,
                              limit=20,
                              num_results=num_results,
                              time_range=time_range)
        return [Artist(a) for r in results for a in r['items']]

    def create_playlist(self, tracks, playlist_name):
        """Create a playlist with the given tracks

        Args:
            tracks: A list of Spotify tracks
            playlist_name: Name of the playlist
        Output:
            results: A playlist is created.
        """
        playlist = SPOTIFY.user_playlist_create(self.username, playlist_name)
        playlist_id = playlist['uri']
        track_ids = [track.uri for track in tracks]
        SPOTIFY.user_playlist_add_tracks(self.username,
                                         playlist_id,
                                         track_ids)


class SpotipyDict(dict):
    """A wrapper for spotipy dictionaries."""

    def __init__(self, spotipy_dict):
        """Create a SpotipyDict from a spotipy dict."""
        dict.__init__(self, spotipy_dict)
        self.name = self['name']
        self.uri = self['uri']

    def __str__(self):
        """Return the name."""
        return self.name

class Artist(SpotipyDict):
    """A wrapper for spotipy artists."""

    def __init__(self, spotipy_dict):
        """Create an Artist from a dict."""
        SpotipyDict.__init__(self, spotipy_dict)
        try:
            self.image_url = self['images'][0]['url']
        except:
            self.image_url = ''
        self._cached_query = None

    @staticmethod
    def create_from_query(query):
        """Create an artist from a spotify query."""
        try:
            queried_artists = query_spotify(query, type='artist')
            return queried_artists[0]
        except:
            print 'The query {} did not find any artist.'
            raise

    def get_top_tracks(self):
        """Return the artist's top tracks."""
        return [Track(t)
                for t in SPOTIFY.artist_top_tracks(self.uri)['tracks']]

    def get_related_artists(self):
        """Get a list of related artists.

        Output:
            result: A list of artists.
        """
        return [Artist(a)
                for a in SPOTIFY.artist_related_artists(self.uri)['artists']]

    def get_remixes(self, num_tracks=10):
        """
        Return the artists remixes.

        Query for remixes, and only return the tracks
        with the artist name in the track name.
        """
        # TODO: Make a smarter filter to avoid the wrong artist
        remixes = [r for r in self.query_remixes(num_tracks) if self.name in r.name]
        return remixes

    def get_tracks_others_remixed(self, num_tracks=10):
        """
        Return the artist track's remixed by others.

        Query for remixes, and only return the tracks
        if the artist is the track's artist.
        """
        others_remixed = [r for r in self.query_remixes(num_tracks) if self.uri in r.artist.uri]
        return others_remixed

    @unique_decorator
    def query_remixes(self, num_tracks=10):
        """Return the query searching for 'artist remix'."""
        if not self._cached_query or len(self._cached_query) < num_tracks:
            name = self.name
            query = '{} remix'.format(name)
            query_tracks = query_spotify(query,
                                         type='track',
                                         num_results=num_tracks)

            self._cached_query = query_tracks
        else:
            query_tracks = self._cached_query
        return query_tracks


class Track(SpotipyDict):
    """A wrapper for spotipy tracks."""

    def __init__(self, spotipy_dict):
        """Create a Track from a dict."""
        SpotipyDict.__init__(self, spotipy_dict)
        self.artists = [Artist(a) for a in self['artists']]
        self.artist = self.artists[0]
        self.popularity = self['popularity']

    @staticmethod
    def create_from_query(query):
        """Create a track from a spotify query."""
        queried_tracks = query_spotify(query)
        return queried_tracks[0]

    def __str__(self):
        """Return the artist and track name."""
        return u'{} - {}'.format(self.artist.name, self.name)

def main():
    """Quick example of how to use Spotify wrappers."""
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = MY_USERNAME
    scope = 'user-top-read'
    user = User.create_from_scope(scope, username)

    def print_list(l):
        for element in l:
            print element.__str__()
        print

    top_artists = user.get_top_artists()
    for artist in top_artists:
        print 'Remixes by', artist.name, ':'
        remixes = artist.get_remixes()
        print_list(remixes)
        print 'Tracks by', artist.name, 'remixed:'
        others_remixed = artist.get_tracks_others_remixed()
        print_list(others_remixed)

if __name__ == '__main__':
    main()
