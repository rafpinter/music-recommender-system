from re import findall
import scipy.sparse as sparse
import implicit
from .implicit_functions import implicit_recommend
import random

import pathlib
PATH = pathlib.Path(__file__).parent
PATH = PATH.joinpath("../").resolve()
PATH = PATH.joinpath("../").resolve()
from spotify_functions import (top_recs_to_string, get_track_ids, maps_playlist, get_song_info, adds_new_playlist_to_df, new_playlist_id)

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
    
    model = implicit.als.AlternatingLeastSquares(**args)
    
    data_conf = (sparse_item_user * alpha).astype('double')
    
    model.fit(data_conf)  
    
    print('\nYour recommendations:\n')

    recs = model.recommend(new_playlist_id(data), sparse_user_item, N=N_RECOMMENDATIONS, filter_already_liked_items=True)
    recs_ids = [i[0] for i in recs]
    recs_str = ''

    for idx in recs_ids:
        recs_str = recs_str + '  ' + get_song_info(idx, song_infos, num_to_id, is_id = False)
    
    return recs_str, recs_ids
