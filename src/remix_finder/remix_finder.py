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

def get_recommended_remixes(user):
    """
    Find recommended remixes for the given user.

    The remixes are found by searching the network of user's
    favorite artists and their similar artists. If the remixer
    and the remixee are in the network, the track

    Args:
        user: A Spotify user.

    Output:
        remixes: A list of tracks.
    """
    user_artists = get_top_artists(user)
    similar_artists = [get_similar_artists(a) for a in user_artists]
    artists = user_artists | similar_artists

    remixes = []
    for artist in artists:
        artist_remixes = get_tracks_remixed_by(artist)
        for remix in artist_remixes:

            if (remix.original_artist in artists and
                    remix.remix_artist in artists):
                remixes.append(remix)

    return remixes

def get_top_artists(user):
    """Get the top artists of a given user.

    Args:
        user: A Spotify user.

    Output:
        result: A list of top artists.
    """
    pass

def get_similar_artists(artist):
    """Get similar artists to the given artist.

    Args:
        artist: A Spotify artist.

    Output:
        result: A list of spotify artists.
    """
    pass

def get_tracks_remixed_by(artist):
    """Get all tracks that are remixed by the given artist.

    Args:
        artist: A Spotify artist.

    Output:
        result: A list of Spotify tracks.
    """
    pass

def get_tracks_others_remixed(artist):
    """Get all tracks of the artist that are remixed by other artists.

    Args:
        artist: A Spotify artist.

    Output:
        result: A list of Spotify tracks.
    """


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
