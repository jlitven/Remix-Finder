#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-06-09 14:04:36
# @Author  : Joshua Litven (jlitven@gmail.com)
# @Link    : https://github.com/jlitven
# @Version : $Id$

"""
Find remixes for a Spotify user.

remix_finder searches a user's favorite artists to find remixes
they will enjoy.
"""
import sys
from spotify_adaptors import User, Artist, Track

def get_recommended_remixes(user):
    """
    Find recommended remixes for the given user.

    The remixes are found by searching the network of user's
    favorite artists and their similar artists. Two lists are
    computed: remixes by the artists, and artist tracks other
    artists have remixed. If a track appears on both lists,
    then both the remixer and remixee are in the network, and
    we recommend it to the user.

    Args:
        user: A Spotify user.

    Output:
        remixes: A list of tracks.
    """
    artists = user.get_top_artists()  # TODO: Add similar artists

    artist_remixes = []
    artist_tracks_others_remixed = []

    for artist in artists:
        remixes = artist.get_remixes()
        other_artists_remixed = artist.get_tracks_others_remixed()
        artist_remixes.extend(remixes)
        artist_tracks_others_remixed.extend(other_artists_remixed)

    remix_uris = set([r.uri for r in artist_remixes])
    other_remixed_uris = set([r.uri for r in artist_tracks_others_remixed])

    recommended_uris = remix_uris & other_remixed_uris

    return [r for r in artist_remixes if r.uri in recommended_uris]

def main():
    """Display recommended remixes to user."""
    if not sys.argv[1]:
        print 'usage: {} user_id'.format(sys.argv[0])
        sys.exit()
    else:
        user = get_user(user_id=sys.argv[1])

    print 'Finding remixes...'
    remixes = get_recommended_remixes(user)

    print 'Recommended Remixes:'
    for remix in remixes:
        print remix

def get_user(user_id):
    """Get the Spotify user given the user_id.

    Args:
        user_id: A Spotify user id.

    Output:
        result: A Spotify user.
    """

if __name__ == '__main__':
    main()
