import json
from collections import defaultdict
import pandas as pd

def loads_json(path):
    f = open(path)
    js = f.read()
    f.close()
    data = json.loads(js)
    return data

def build_dict(set_of_songs, data):
    
    pl_containing_song = dict()
    
    for song in list(set_of_songs):
        
        tmp_ls = []
        
        for key, val in data.items():
            try:
                val[key][song]
            except KeyError:
                continue
            else:
                tmp_ls.append(key)
        
        pl_containing_song[song] = tmp_ls
    
    return pl_containing_song

path = 'data'
all_jsons_path = path + r'\all_jsons.json'

data_dict = loads_json(all_jsons_path)
data = defaultdict()

for key, value in data_dict.items():
    data[key] = {val: True for val in value}

set_of_songs = set()

for key, value in data.items():
    [set_of_songs.add(song) for song in value]
    
    
i = 0 
map_song_id = dict()

for song in list(set_of_songs):
    map_song_id[song] = i
    i+=1
    
dict_num_ids = dict()

for key, value in data_dict.items():
    tmp = []
    for song in value:
        tmp.append(map_song_id[song])
    dict_num_ids[key] = tmp
    
myfile = open(path + r'\id_to_num.json', 'a')
myfile.write(json.dumps(map_song_id, sort_keys=True, indent=4))
myfile.close()

map_song_id_inv = {value:key for key,value in map_song_id.items()}

myfile = open(path + r'\num_to_id.json', 'a')
myfile.write(json.dumps(map_song_id_inv, sort_keys=True, indent=4))
myfile.close()