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

SPOTIFY = spotipy.Spotify()
MY_USERNAME = '1212629687'

class User:
    """A Spotify user."""

    def __init__(self, username=MY_USERNAME, scope=None):
        """Create a user with the desired scope."""
        self.username = username
        self.token = self.get_token(username, scope)
        global SPOTIFY
        SPOTIFY = spotipy.Spotify(auth=self.token)
        self.profile = SPOTIFY.current_user()
        self.name = self.profile['display_name']

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

    def get_top_artists(self, limit=20, offset=0, time_range='medium_term'):
        """Get the user's top artists over a time range.

        Args:
            limit: Number of artists returned
            offset: Index of the first artist to return
            time_range: Over what time period the artists are computed.
            Valid-values: short_term, medium_term, long_term
        Output:
            result: A list of artists.
        """
        results = SPOTIFY.current_user_top_artists(limit=limit,
                                                   offset=offset,
                                                   time_range=time_range)
        return [Artist(a) for a in results['items']]

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
        self._cached_query = None

    def get_related_artists(self):
        """Get a list of related artists.

        Output:
            result: A list of artists.
        """
        return [Artist(a)
                for a in SPOTIFY.artist_related_artists(self.uri)['artists']]

    def get_remixes(self):
        """
        Return the artists remixes.

        Query for remixes, and only return the tracks
        with the artist name in the track name.
        """
        remixes = [r for r in self.query_remixes() if self.name in r.name]
        return remixes

    def get_tracks_others_remixed(self):
        """
        Return the artist track's remixed by others.

        Query for remixes, and only return the tracks
        if the artist is the track's artist.
        """
        others_remixed = [r for r in self.query_remixes() if self.uri in r.artist.uri]
        return others_remixed

    def query_remixes(self, limit=10, offset=0):
        """Return the query searching for 'artist remix'."""
        if not self._cached_query:
            name = self.name
            query = '{} remix'.format(name)
            results = SPOTIFY.search(q=query,
                                     type='track',
                                     limit=limit,
                                     offset=offset)
            query_tracks = [Track(t) for t in results['tracks']['items']]
            self._cached_query = query_tracks
        else:
            query_tracks = self._cached_query
        return query_tracks

    def get_top_tracks(self):
        """Return the artist's top tracks."""
        return [Track(t)
                for t in SPOTIFY.artist_top_tracks(self.uri)['tracks']]


class Track(SpotipyDict):
    """A wrapper for spotipy tracks."""

    def __init__(self, spotipy_dict):
        """Create a Track from a dict."""
        SpotipyDict.__init__(self, spotipy_dict)
        self.artists = [Artist(a) for a in self['artists']]
        self.artist = self.artists[0]

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
    user = User(username, scope)

    def print_list(l):
        for element in l:
            print element.__str__()
        print

    top_artists = user.get_top_artists(limit=5)
    for artist in top_artists:
        print 'Remixes by', artist.name, ':'
        remixes = artist.get_remixes()
        print_list(remixes)
        print 'Tracks by', artist.name, 'remixed:'
        others_remixed = artist.get_tracks_others_remixed()
        print_list(others_remixed)

if __name__ == '__main__':
    main()
