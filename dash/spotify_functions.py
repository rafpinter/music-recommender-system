# defs
from flask import url_for
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import json
import pandas as pd
from re import findall
# # Main page

# def get_token(scope,client_id,client_secret,redirect_uri):
    
#     token_info = session.get(TOKEN_INFO)
#     now = int(time.time())
    
#     is_expired = token_info['expires_at'] - now < 60
    
#     if is_expired:
#         sp_oauth = SpotifyOAuth(scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
#         token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    
#     return token_info


def load_json(path):
    with open(path, 'r', encoding="utf8") as f:
        return json.load(f)
    
def create_spotify_oauth():
    
    codes = load_json(r'C:\Users\rafaela.pinter_dp6\Documents\playlists-recsys\data\spotify_codes.json') 
    
    return SpotifyOAuth(
        client_id=codes['client_id'],
        client_secret=codes['client_secret='],
        redirect_uri=url_for('/', _external=True),
        scope='user_library_read'
    )
    
    
def new_playlist_id(data):
    return data.playlist_id.max()
 

def load_data():

    with open(r'data\songs_infos.json', encoding="utf8") as json_file:
        song_infos = json.load(json_file)

    data = pd.read_csv(r'data\df_playlist_and_songs.csv')
    data['plays'] = 1

    # Num to id
    num_to_id = load_json(r'data\num_to_id.json')

    # id to num
    id_to_num = load_json(r'data\id_to_num.json')
            
    return song_infos, data, num_to_id, id_to_num



def connect_to_spotify():
    """
    Connects to spotify API
    """

    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials

    path = 'spotify_codes.json'        
 
    with open(path, 'r', encoding="utf8") as f:
        codes = json.load(f)
     
    client_id = codes['client_id']
    client_secret = codes['client_secret']

    print(codes)

    client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    return sp



def get_track_ids(user, playlist_id, sp):
    """get_track_ids

    Args:
        user (int): spotify's user id
        playlist_id (list): playlist id
        sp (spotify): spotify's connector

    Returns:
        ids: list of song ids in the playlist
    """
    ids = []
    playlist = sp.user_playlist(user, playlist_id)
    
    for item in playlist['tracks']['items']:
        track = item['track']
        ids.append(track['id'])
    
    return ids



def get_all_track_features(id, sp):
    """get_all_track_features

    Args:
        id (string): song id
        sp (spotify): spotify's connector

    Returns:
        (track, meta)
    """
    
    meta = sp.track(id)
    features = sp.audio_features(id)

    # meta
    name = meta['name']
    album = meta['album']['name']
    artist = meta['album']['artists'][0]['name']
    release_date = meta['album']['release_date']
    length = meta['duration_ms']
    popularity = meta['popularity']

    # features
    acousticness = features[0]['acousticness']
    danceability = features[0]['danceability']
    energy = features[0]['energy']
    instrumentalness = features[0]['instrumentalness']
    liveness = features[0]['liveness']
    loudness = features[0]['loudness']
    speechiness = features[0]['speechiness']
    tempo = features[0]['tempo']
    time_signature = features[0]['time_signature']
    key = features[0]['key']
    mode = features[0]['mode']
    valence = features[0]['valence']

    track = [name, album, artist, release_date, length, 
             popularity, acousticness, danceability, energy,
             instrumentalness, liveness, loudness, speechiness, 
             valence, tempo, time_signature, key, mode]
    
    return track


def request_track_features(id, sp):
    """get_track_features: 

    Args:
        id (string): id of the song
        sp (spotify): spotify's connector

    Returns:
        [dict]: dictionary with song's info
    """
    new_tracks = dict()
    
    meta = sp.track(id)

    new_tracks[str(id)] = {
        "album_name": meta['album']['name'],
        "album_uri": meta['album']['uri'],
        "artist_name": meta['artists'][0]['name'],
        "artist_uri": meta['artists'][0]['uri'],
        "track_name": meta['name'],
        "track_uri": meta['uri']
        }
    
    return new_tracks


def maps_playlist(playlist, id_to_num):
    """maps_playlist
    
    For all songs in the playlist, the function tries to find the corresponding numeric id.
    If the song does not exist in any playlist, it is skipped (for now).

    Args:
        playlist (list): list spotify's song ids
        maps (dict): dictionary of ids to numeric

    Returns:
        list of numeric ids
    """
    
    mapped_playlist = []
    new_songs = dict()

    not_found = []

    for song in playlist:
        try:
            mapped_playlist.append(int(id_to_num[song]))
        except KeyError:
            # new_songs = new_songs | get_track_features(song)     
            not_found.append(song)

    return mapped_playlist, not_found


def get_song_info(song_id, song_infos, num_to_id, is_id):
    """get_song_info

    Prints the Artist, Song and Album from a numeric id.

    Args:
        numeric_id (int): numeric id from the song
    """
    
    if is_id:
        infos = song_infos[song_id]
        # print("Artist:", infos['artist_name'])
        # print("Song:", infos['track_name'])
        # print("Album:", infos['album_name'])
        # print('\n')
        return f'''
    Song: {infos['track_name']}  
    Artist: {infos['artist_name']}  
    Album: {infos['album_name']}  
    '''
    else:
        infos = song_infos[num_to_id[f"{song_id}"]]
        # print("Artist:", infos['artist_name'])
        # print("Song:", infos['track_name'])
        # print("Album:", infos['album_name'])
        # print('\n')
        return f'''
    Song: {infos['track_name']}  
    Artist: {infos['artist_name']}  
    Album: {infos['album_name']}  
    '''


def top_recs_to_string(top_recs, song_infos, num_to_id, is_id=False):
    
    string = ''
    for idx in top_recs:
        string = string + '  ' + get_song_info(idx, song_infos, num_to_id, is_id=is_id)
    return string


def adds_new_playlist_to_df(data, playlist):
    new_playlist_id = data.playlist_id.max() + 1
    ls = [(new_playlist_id, song_id, 1) for song_id in playlist]
    new_playlist_df = pd.DataFrame(ls, columns=['playlist_id', 'song_id', 'plays'])
    data = pd.concat([data, new_playlist_df])
    
    return data

def get_playlist_metadata(sp, playlistid):
    
    PLAYLIST_ID = findall('(?<=playlist\/)[\w\W\d]+(?=\?)', playlistid)[0]

    infos = sp.playlist(PLAYLIST_ID)
    
    img = infos['images'][0]['url']
    name = infos['name']
    owner = f"Created by {infos['owner']['id']}"
    followers = f"{infos['followers']['total']} followers"
    description = infos['description']
    total_n_tracks = f"{infos['tracks']['total']} tracks"
    
    return img, name, owner, followers, description, total_n_tracks