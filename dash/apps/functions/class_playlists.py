import time
from flask import session
from spotipy.oauth2 import SpotifyOAuth

from dataclasses import dataclass, field
import pandas as pd
from re import findall


import pathlib
PATH = pathlib.Path(__file__).parent
PATH = PATH.joinpath("../").resolve()
PATH = PATH.joinpath("../").resolve()

from spotify_functions import (
    get_all_track_features,
    get_track_ids,
    maps_playlist,
    get_song_info,
    )

@dataclass
class PLAYLISTRECSYS:
    
    # Conection
    auth_url: str = field(init=False)
    
    # Obrigatórios para criar a base
    N_RECOMMENDATIONS: int= field(default=15)
    
    # authorized user
    user: str = field(default=None)
    
    # Criados durante o código
    usr_playlist_url: str = field(default=None)
    usr_playlist_song_ids: list[int] = field(default_factory=list)
    rec_playlist_ids: list[int] = field(default_factory=dict)
    
    # pl info
    usr_playlist_img: str = field(init=False)
    usr_playlist_name: int = field(init=False)
    usr_playlist_owner: str = field(init=False)
    usr_playlist_followers: int = field(init=False)
    usr_playlist_description: str = field(init=False)
    usr_playlist_total_n_tracks: str = field(init=False)

    # dfs
    df_recs: str = field(default=None)
    df_playlist: str = field(default=None)
    df: str = field(default=None) # df concatenado
    df_exec: str = field(default=None) # df exec
    
    # dbs
    song_infos: str = field(init=False)
    dataframe: pd.DataFrame = field(init=False)
    num_to_id: str = field(init=False)
    id_to_num: str = field(init=False)
    
    # os and creds
    OS: str = field(default='win')
    CREDENTIALS: str = field(init=False)
    sp: str = field(init=False)
    sp_oauth: str = field(init=False)
    
    # algoritmo selecionado
    algorithm: str = field(init=False)
    
    # specific inputs do lightFM
    lfm_components: int = field(init=False)
    lfm_k: int = field(init=False)
    lfm_epochs: int = field(init=False)
    lfm_loss: str = field(init=False)
    
    # specific inputs do implict
    impl_factors: int = field(init=False)
    impl_reg: float = field(init=False)
    impl_iter: int = field(init=False)
    
    # Sp
    client_id: str = field(init=False)
    client_secret: str = field(init=False)
    scope: str = field(default='playlist-read-collaborative playlist-modify-public user-read-private user-read-email')
    redirect_uri: str = field(default='http://127.0.0.1:8050/playlist-recommendation')

    # Spotify API
    # Spotify API endpoints
    AUTH_URL: str = field(default='https://accounts.spotify.com/authorize')
    TOKEN_URL: str = field(default='https://accounts.spotify.com/api/token')
    ME_URL: str = field(default='https://api.spotify.com/v1/me')
    CREATE_PLAYLIST_URL: str = field(default='https://api.spotify.com/v1/users')
    ADD_SONGS_PLAYLIST_URL: str = field(default='https://api.spotify.com/v1/playlists')
    LOGIN_REDIRECT_URI: str = field(default='http://127.0.0.1:8050/callback')
    
    # def __post_init__(self):
        
    #     if self.OS == 'win':
            




        
    def __update_df_recs(self, df):
        self.df_recs = pd.concat([self.df_recs, df])
    
    def __update_df(self, df):
        self.df = df
        
    def __update_df_exec(self, df):
        self.df_exec = pd.concat([self.df_exec, df])
        
    def get_access_token(TOKEN_INFO, scope, client_id, client_secret, redirect_uri):
            
        token_info = session.get(TOKEN_INFO)
        now = int(time.time())
        
        is_expired = token_info['expires_at'] - now < 60
        
        if is_expired:
            sp_oauth = SpotifyOAuth(scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        
        return token_info
    
    
    def fill_pl_metadata(self,
                         usr_playlist_img,
                         usr_playlist_name,
                         usr_playlist_owner,
                         usr_playlist_followers,
                         usr_playlist_description,
                         usr_playlist_total_n_tracks):
    
        self.usr_playlist_img = usr_playlist_img
        self.usr_playlist_name = usr_playlist_name
        self.usr_playlist_owner = usr_playlist_owner
        self.usr_playlist_followers = usr_playlist_followers
        self.usr_playlist_description = usr_playlist_description
        self.usr_playlist_total_n_tracks = usr_playlist_total_n_tracks
    
    
    def fill_als_data(self, factors, regularization, iteractions):
        
        self.impl_factors = factors
        self.impl_reg = regularization
        self.impl_iter = iteractions
    
        
    def get_als_data(self):
        
        return {'Factors':self.impl_factors,
                'Regularization':self.impl_reg,
                'Iterations':self.impl_iter,}
    
        
    def fill_lightfm_data(self, components, k, epochs, loss):
        
        self.lfm_components = components
        self.lfm_k = k
        self.lfm_epochs = epochs
        self.lfm_loss = loss
    
    
    def get_lightfm_data(self):
        
        return {'Components' :self.lfm_components,
                'K' :self.lfm_k,
                'Epochs' :self.lfm_epochs,
                'Loss Function' :self.lfm_loss}
        
        
    def append_to_df_playlist(self, ids, n, sp, num_to_id):
        
        tracks = []
        for song in ids:
            track_info = get_all_track_features(num_to_id[f'{song}'], sp)
            tracks.append(track_info)

        df_cols = ['name', 'album', 'artist', 'release_date', 'length',
                   'popularity', 'acousticness', 'danceability', 'energy',
                   'instrumentalness', 'liveness', 'loudness', 'speechiness',
                   'valence', 'tempo', 'time_signature', 'key', 'mode']

        df = pd.DataFrame(data=tracks, columns=df_cols)

        df['track_id'] = [num_to_id[f'{song}'] for song in ids]
        df['type'] = 'your playlist'
        df['algorithm'] = self.algorithm
        df['train_no'] = f"Train #{n}"
        df['train_id'] = n
        df['playlist_name'] = self.usr_playlist_name
        df['label'] = self.usr_playlist_name
        
        self.df_playlist = df
        
        return self.df_playlist

    
    def append_to_df_recs(self, ids, n, sp, num_to_id):
    
        tracks = []
        for song in ids:
            track = get_all_track_features(num_to_id[f'{song}'], sp)
            tracks.append(track)

        df_cols = ['name', 'album', 'artist', 'release_date', 'length',
                   'popularity', 'acousticness', 'danceability', 'energy',
                   'instrumentalness', 'liveness', 'loudness', 'speechiness',
                   'valence', 'tempo', 'time_signature', 'key', 'mode']
        
        df = pd.DataFrame(data=tracks, columns=df_cols)
        df['track_id'] = [num_to_id[f'{song}'] for song in ids]
        df['type'] = 'recommended songs'
        df['algorithm'] = self.algorithm
        df['train_no'] = f"Train #{n}"
        df['train_id'] = n
        df['playlist_name'] = self.usr_playlist_name
        df['label'] = f"Recommended songs - #{n}"
        # df['specifications'] = 
        
        if self.df_recs is None:
            self.df_recs = df
        else:
            self.__update_df_recs(df)
        
        return self.df_recs

    
    def append_df_exec_time(self, n, factors, iterations, regularization, db_fraction, alpha, exec_time):
        
        cols = ['label', 'factors', 'iterations', 'regularization', 'db_fraction', 'alpha', 'exec_time']
        
        label = f"Recommended songs - #{n}"
        
        df = pd.DataFrame(data=[[label, factors, iterations, regularization, db_fraction, alpha, exec_time]],
                          columns=cols)
        
        if self.df_exec is None:
            self.df_exec = df
        else:
            self.__update_df_exec(df)
        
    
    
    def creating_dfs(self, recs_ids_playlist, n, sp, num_to_id):
        
        df_recs = self.append_to_df_recs(recs_ids_playlist, 
                                         n,
                                         sp, 
                                         num_to_id=num_to_id)
        
        df_playlist = self.append_to_df_playlist(self.usr_playlist_song_ids, 
                                                 n,
                                                 sp, 
                                                 num_to_id=num_to_id)

        self.__update_df(pd.concat([df_recs, df_playlist]))
    
    

    def get_playlist(self, CREDENTIALS, sp, id_to_num, song_infos, num_to_id):
        
        PLAYLIST_ID = findall('(?<=playlist\/)[\w\W\d]+(?=\?)', self.usr_playlist_url)[0]
        full_playlist = get_track_ids(CREDENTIALS['user'], PLAYLIST_ID, sp)
        mapped_playlist, _ = maps_playlist(full_playlist, id_to_num)
        string = ''
        
        for song_id in mapped_playlist: 
            string = string + '  ' + get_song_info(song_id, song_infos, num_to_id, is_id= False)
        
        return string, mapped_playlist
    
    
    def get_track_ids_last_train(self):
        
        tmp_df = self.df.copy()
        tmp_df['train_id'] = tmp_df['train_no'].apply(lambda x: x.split("#")[1])
        max_train_id = tmp_df['train_id'].max()
        
        return tmp_df[tmp_df['train_id'] == max_train_id]['track_id']