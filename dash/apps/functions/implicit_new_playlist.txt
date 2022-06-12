import os
import pandas as pd
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def get_tracks_ids(user, playlist_id):
    ids = []
    playlist = sp.user_playlist(user, playlist_id)
    
    for item in playlist['tracks']['items']:
        track = item['track']
        ids.append(track['id'])
    
    return ids

def get_track_features(id):
    global new_tracks
    
    meta = sp.track(id)

    new_tracks[str(id)] = {
        "album_name": meta['album']['name'],
        "album_uri": meta['album']['uri'],
        "artist_name": meta['artists'][0]['name'],
        "artist_uri": meta['artists'][0]['uri'],
        "track_name": meta['name'],
        "track_uri": meta['uri']
        }

# def adds_song_info(track_info,song_info):

def maps_playlist(playlist):
    mapped_playlist = []

    for song in playlist:
        try:
            mapped_playlist.append(int(maps[song]))
        except KeyError:
            get_track_features(song)

    return mapped_playlist


## CONEXÃO COM O SPOTIFY

# Abrindo códigos do spotify
with open('spotify_codes.json') as f:
    sptfy_codes = json.load(f)

client_id = sptfy_codes['client_id']
client_secret = sptfy_codes['client_secret']
client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


# Buscando playlist
# Importando dados

with open('C:\\Users\\rafaela.pinter_dp6\\Documents\\playlists-recsys\\data\\song_infos.json', encoding="utf8") as json_file:
    song_infos = json.load(json_file)

data = pd.read_csv("C:\\Users\\rafaela.pinter_dp6\\Documents\\playlists-recsys\\data\\final_json_numeric_ids.csv")
data['plays'] = 1

with open('C:\\Users\\rafaela.pinter_dp6\\Documents\\playlists-recsys\\data\\map_song_numeric_ids_inv.json') as json_file:
    maps_inv = json.load(json_file)
    

