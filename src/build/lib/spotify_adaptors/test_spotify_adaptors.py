#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-06-17 12:31:37
# @Author  : Joshua Litven (jlitven@gmail.com)
# @Link    : https://github.com/jlitven
# @Version : $Id$
"""
Unit tests for spotify_adaptors module.
"""

import unittest
import pickle
import spotify_adaptors
from spotify_adaptors import Track, Artist, User, SPOTIFY, MY_USERNAME

class TestUser(unittest.TestCase):
    """Unit tests for class User."""

    def setUp(self):
        """Create a user."""
        self.user = User(MY_USERNAME)

    def test_create_user(self):
        """Create a user and verify user details."""
        self.assertEqual(self.user.name, 'Alexander Litven')

    def test_get_top_artists(self):
        """Verify a user's top artists."""
        my_top_artist = 'Pretty Lights'
        top_artists = self.user.get_top_artists(time_range='long_term')
        top_artists = [a.name for a in top_artists]

        self.assertTrue(my_top_artist in top_artists)

class TestTrack(unittest.TestCase):
    """Unit tests for class Track."""

    def test_create_track(self):
        """Create a track and check properties."""
        track_uri = 'spotify:track:5SYYfoHNkDBgBWawXbYc4H'
        track_name = 'Entoptica'
        artist_name = 'Starcadian'
        spotify_track = SPOTIFY.track(track_uri)
        track = Track(spotify_track)

        self.assertEqual(track.uri, track_uri)
        self.assertEqual(track.name, track_name)
        self.assertEqual(track.artist.name, artist_name)

class TestArtist(unittest.TestCase):
    """Unit tests for class Artist."""

    ONLINE = True

    def setUp(self):
        """Create an artist."""
        self.artist_uri = 'spotify:artist:3I0ceM8qfqhCKGepaswmVg'
        self.artist_name = 'Starcadian'
        if TestArtist.ONLINE:
            self.spotify_artist = SPOTIFY.artist(self.artist_uri)
        else:
            with open('./test_data/spotify_data', 'rb') as handle:
                self.spotify_artist = pickle.load(handle)
        self.artist = Artist(self.spotify_artist)

    def test_artist_properties(self):
        """Test properties."""
        self.assertEqual(self.artist.uri, self.artist_uri)
        self.assertEqual(self.artist.name, self.artist_name)

    def test_get_related_artists(self):
        """Test related artists."""
        artist_related_artists = ['Lazerhawk', 'Le Matos', 'Magic Sword']
        related_artists = self.artist.get_related_artists()
        related_artists = [a.name for a in related_artists]

        for artist in artist_related_artists:
            self.assertTrue(artist in related_artists)

    def test_get_top_tracks(self):
        """Test top tracks."""
        artist_top_tracks = ['Chinatown', 'Ultralove', 'Lovetop']
        top_tracks = self.artist.get_top_tracks()
        top_tracks = [t.name for t in top_tracks]

        for track in artist_top_tracks:
            self.assertTrue(track in top_tracks)

    def test_query_remixes(self):
        """
        Test the remix queries.

        Verify each track has the word remix in it.
        """
        queried_tracks = self.artist.query_remixes()

        for track in queried_tracks:
            self.assertTrue('remix' in track.name.lower())

    def test_get_remixes(self):
        """Test remixes."""
        artist_remix_uris = [
        u'spotify:track:4NxpLNIYAuaNh2UG7TDVDe',
        u'spotify:track:2gXpaR1PdlweqdTotouuuq',
        u'spotify:track:6VJ3JsM8dos0Rw8BHGp8QX']
        remixes = self.artist.get_remixes()
        remix_uris = [r.uri for r in remixes]

        for uri in remix_uris:
            self.assertTrue(uri in artist_remix_uris)

    def test_get_tracks_others_remixed(self):
        """Test getting artist tracks remixed by others."""
        artist_remixed_tracks_uris = [
        u'spotify:track:4NxpLNIYAuaNh2UG7TDVDe']
        remixed_tracks = self.artist.get_tracks_others_remixed()
        remixed_track_uris = [r.uri for r in remixed_tracks]

        for uri in remixed_track_uris:
            self.assertTrue(uri in artist_remixed_tracks_uris)

if __name__ == '__main__':
    unittest.main()
