import random
import pathlib
import implicit
from re import findall
import secrets
import string
import time
from base64 import b64encode
from flask import (
    abort,
    make_response,
    redirect,
    request,
    session,
)
import json
import os
import requests

from urllib.parse import urlencode
import scipy.sparse as sparse
from .implicit_functions import implicit_recommend
from .spotify_functions import (
    top_recs_to_string,
    get_track_ids,
    maps_playlist,
    get_song_info,
    adds_new_playlist_to_df,
    new_playlist_id
    )

def get_playlist(url, alg, id_to_num, song_infos, num_to_id, CREDENTIALS, sp):
    
    PLAYLIST_ID = findall('(?<=playlist\/)[\w\W\d]+(?=\?)', url)[0]
    full_playlist = get_track_ids(CREDENTIALS['user'], PLAYLIST_ID, sp)
    mapped_playlist, _ = maps_playlist(full_playlist, id_to_num)
    string = ''
    
    for song_id in mapped_playlist: 
        string = string + '  ' + get_song_info(song_id, song_infos, num_to_id, is_id= False)
    
    return string, mapped_playlist


def link_to_mapped_playlist(url, alg, id_to_num, CREDENTIALS, sp):
    
    PLAYLIST_ID = findall('(?<=playlist\/)[\w\W\d]+(?=\?)', url)[0]
    full_playlist = get_track_ids(CREDENTIALS['user'], PLAYLIST_ID, sp)
    mapped_playlist, _ = maps_playlist(full_playlist, id_to_num)
    
    return mapped_playlist


def get_random_sample(db_fraction, data):
    
    max_id = int(data['playlist_id'].max())
    db_fraction = float(db_fraction)
    
    random_index = [random.randint(0, max_id) for _ in range(int(db_fraction * max_id))]
    
    data = data[data['playlist_id'].isin(random_index)]
    
    return data


def implicit_recsys(url, 
                    alg, 
                    alpha,
                    id_to_num, 
                    song_infos, 
                    num_to_id, 
                    dataframe, 
                    CREDENTIALS, 
                    sp, 
                    N_RECOMMENDATIONS, 
                    db_fraction,
                    **args):
        
    # buscando dados
    mapped_playlist = link_to_mapped_playlist(url, alg, id_to_num, CREDENTIALS, sp)
    data = adds_new_playlist_to_df(dataframe, mapped_playlist)

    if db_fraction != "1":
        data = get_random_sample(float(db_fraction), data)

    # Treinando modelo
    sparse_item_user = sparse.csr_matrix((data['plays'].astype(float), (data['song_id'], data['playlist_id'])))
    sparse_user_item = sparse.csr_matrix((data['plays'].astype(float), (data['playlist_id'], data['song_id'])))
    
    model = implicit.als.AlternatingLeastSquares(random_state=42, **args)
    
    data_conf = (sparse_user_item * alpha).astype('double')
    
    model.fit(data_conf)  
    
    print('\nYour recommendations:\n')

    recs = model.recommend(new_playlist_id(data), data_conf[new_playlist_id(data)], N=N_RECOMMENDATIONS, filter_already_liked_items=True)
    recs_ids = recs[0]
    recs_str = ''

    for idx in recs_ids:
        recs_str = recs_str + '  ' + get_song_info(idx, song_infos, num_to_id, is_id = False)
    
    return recs_str, recs_ids


def refresh_acess_token(session, playlistrecsys):
    """Refreshing the access token"""
    
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': session.get('tokens').get('refresh_token'),
    }
    
    authorization = b64encode(f'{playlistrecsys.client_id}:{playlistrecsys.client_secret}'.encode()).decode()
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Authorization': f'Basic {authorization}'}
    
    res = requests.post(
        playlistrecsys.TOKEN_URL, 
        auth=(playlistrecsys.client_id, playlistrecsys.client_secret),
        data=payload, 
        headers=headers
    )
    
    res_data = res.json()
    
    # Load new token into session
    session['tokens']['access_token'] = res_data.get('access_token')
    
    return session['tokens']['access_token']


def login_user(playlistrecsys):
    
    state = ''.join(
        secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16)
    )

    # Request authorization from user
    scope = 'user-read-private user-read-email'

    payload = {
        'client_id': playlistrecsys.client_id,
        'response_type': 'code',
        'redirect_uri': playlistrecsys.LOGIN_REDIRECT_URI,
        'state': state,
        'scope': playlistrecsys.scope,
    }

    res = make_response(redirect(f'{playlistrecsys.AUTH_URL}/?{urlencode(payload)}'))
    res.set_cookie('spotify_auth_state', state)
    
    return res

def callback_route(playlistrecsys):
    error = request.args.get('error')
    code = request.args.get('code')
    state = request.args.get('state')
    stored_state = request.cookies.get('spotify_auth_state')

    # Check state
    if state is None or state != stored_state:
        app.logger.error('Error message: %s', repr(error))
        app.logger.error('State mismatch: %s != %s', stored_state, state)
        abort(400)

    # Request tokens with code we obtained
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': playlistrecsys.LOGIN_REDIRECT_URI,
    }

    res = requests.post(playlistrecsys.TOKEN_URL, 
                        auth=(playlistrecsys.client_id, playlistrecsys.client_secret), 
                        data=payload)
    
    res_data = res.json()

    if res_data.get('error') or res.status_code != 200:
        app.logger.error(
            'Failed to receive token: %s',
            res_data.get('error', 'No error information received.'),
        )
        abort(res.status_code)

    # Load tokens into session
    session['tokens'] = {
        'access_token': res_data.get('access_token'),
        'refresh_token': res_data.get('refresh_token'),
    }
    
    # saving user data
    headers = {'Authorization': f"Bearer {session['tokens'].get('access_token')}"}
    res = requests.get(playlistrecsys.ME_URL, headers=headers)
    res_data = res.json()
    playlistrecsys.user = res_data

    return redirect('http://127.0.0.1:8050/playlist-continuation')



def export_playlist_to_spotify(session, playlistrecsys):
    
    token = session['tokens']['access_token']

    headers = {'Authorization': f"Bearer {token}",
                "Content-Type": "application/json"}
    res_me = requests.get(playlistrecsys.ME_URL, headers=headers)
            
    user_id = playlistrecsys.user['id']
    
    # criando playlist 
    data = json.dumps({
        'name': 'Nova Playlist: SpotiRecs',
        'description': 'Playlist criada a partir do melhor software de recomendação de musicas',
        'public': True
    })
    
    url = f'{playlistrecsys.CREATE_PLAYLIST_URL}/{user_id}/playlists'
    
    res_crpl = requests.post(url, data = data, headers=headers)
    new_playlist_id = res_crpl.json()["id"]

    # adicionando músicas na playlist
    add_url = f'{playlistrecsys.ADD_SONGS_PLAYLIST_URL}/{new_playlist_id}/tracks'
    ids = list(playlistrecsys.get_track_ids_last_train())
    uris = [f'spotify:track:{x}' for x in ids]
    
    body = json.dumps({'uris': uris})
    
    res_add = requests.post(add_url, data=body, headers=headers)