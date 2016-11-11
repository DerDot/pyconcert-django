import urllib

import requests
from spotipy import Spotify

from eventowl.utils import config
from eventowl.utils.string_helpers import random_string, normalize

MIX_OF_THE_WEEK = 'spotifydiscover'

def spotify_auth_url():
    state = random_string()
    api_call = "https://accounts.spotify.com/authorize"
    args = [("client_id", config["SPOTIFY_ID"]),
            ("response_type", "code"),
            ("redirect_uri", config["SPOTIFY_URL"]),
            ("scope", "user-library-read user-follow-read playlist-read-private playlist-read-collaborative"),
            ("state", state)]
    auth_url = "%s?%s" % (api_call, urllib.parse.urlencode(args))
    return auth_url, state


def spotify_token_from_code(code):
    api_call = "https://accounts.spotify.com/api/token"
    response = requests.post(api_call, data={'code': code,
                                             'grant_type': 'authorization_code',
                                             'redirect_uri': config["SPOTIFY_URL"],
                                             'client_id': config["SPOTIFY_ID"],
                                             'client_secret': config["SPOTIFY_SECRET"]})
    token_info = response.json()
    return token_info


def spotify_artists(token):
    spotify_client = Spotify(auth=token)
    artists = set(playlist_artists(spotify_client))
    artists.update(saved_artists(spotify_client))
    artists.update(followed_artists(spotify_client))
    return (normalize(artist) for artist in artists)


def playlist_artists(client):
    print("Reading artists from playlists...")
    playlists = _all_playlists(client)
    for playlist in playlists:
        owner = playlist['owner']['id']
        if owner != MIX_OF_THE_WEEK:
            playlist_content = client.user_playlist(owner, playlist['id'], fields="tracks,next")
            yield from _artists_from_playlist(playlist_content, client)


def saved_artists(client):
    print("Reading artists from saved tracks...")
    tracks = client.current_user_saved_tracks()
    yield from _artists_from_tracks(tracks)
    while tracks['next']:
        tracks = client.next(tracks)
        yield from _artists_from_tracks(tracks)


def followed_artists(client):
    print("Reading followed artists...")
    artists = client.current_user_followed_artists()['artists']
    yield from (artist['name'] for artist in artists['items'])
    while artists['next']:
        artists = client.next(artists)['artists']
        yield from (artist['name'] for artist in artists['items'])


def _all_playlists(client):
    playlists = client.user_playlists(client.current_user()["id"])
    yield from playlists['items']
    while playlists['next']:
        playlists = client.next(playlists)
        yield from playlists['items']


def _artists_from_playlist(playlist_content, client):
    tracks = playlist_content['tracks']
    yield from _artists_from_tracks(tracks)
    while tracks['next']:
        tracks = client.next(tracks)
        yield from _artists_from_tracks(tracks)


def _artists_from_tracks(tracks):
    for track_item in tracks['items']:
        for artist in track_item['track']['artists']:
            yield artist['name']