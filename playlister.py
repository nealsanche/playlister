import sys
import os
from gmusicapi import Mobileclient
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

if len(sys.argv) > 2:
    googleEmail = sys.argv[1]
    username = sys.argv[2]
else:
    print("Usage: %s googleEmail username" % (sys.argv[0],))
    sys.exit()


clientId = "<<YOUR SPOTIFY APP CLIENT ID>>"
clientSecret = "<<YOUR SPOTIFY APP CLIENT SECRET>>"

spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=clientId, client_secret=clientSecret))

mc = Mobileclient()
if os.path.exists(googleEmail) == False:
    mc.perform_oauth(storage_filepath=googleEmail, open_browser=True)
mc.oauth_login(Mobileclient.FROM_MAC_ADDRESS, oauth_credentials=googleEmail)

playlists = {}

for playlist in mc.get_all_user_playlist_contents():
    print(playlist['name'])
    playlists[playlist['name']] = []
    currentPlaylist = playlists[playlist['name']]
    for entry in playlist['tracks']:
        if 'track' in entry:
            title = entry['track']['title']
            artist = entry['track']['artist']
            album = entry['track']['album']

            spotifyResults = spotify.search(q=artist+', '+title, type='track')
            if len(spotifyResults['tracks']['items']) > 0:
                spotifyTrackUri = spotifyResults['tracks']['items'][0]['uri']
            else:
                spotifyTrackUri = "unknown"

            if spotifyTrackUri != 'unknown':
                currentPlaylist.append(spotifyTrackUri)
            else:
                print("Unable to find track "+title+" by "+artist+" on album "+album+"\n")

token = util.prompt_for_user_token(client_id=clientId, client_secret=clientSecret, username=username, redirect_uri='http://localhost:8888', scope='playlist-modify-private')
if token:
    sp = spotipy.Spotify(auth=token)

    for playListName in playlists:
        playlist = sp.user_playlist_create(user=username, name=playListName, public=False, description="Auto created playlist test.")
        if len(playlists[playListName]) > 0:
            tracks = playlists[playListName]
            tracks = [tracks[i:i+100] for i in range(0, len(tracks), 100)]
            for trackList in tracks:
                sp.user_playlist_add_tracks(user=username, playlist_id=playlist['id'], tracks=trackList)

