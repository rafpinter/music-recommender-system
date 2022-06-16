import json
import os
from zipfile import ZipFile
    
def loads_json(path):
    f = open(path)
    js = f.read()
    f.close()
    data = json.loads(js)
    data = data['playlists']
    return data

def extract_songs(data):
    
    pl = {}

    for i in range(len(data)):
        
        tracks = []
        
        for j in range(data[i]['num_tracks']):
            tracks.append(data[i]['tracks'][j]['track_uri'].split(':')[2])
            
        pl[data[i]['pid']] = tracks

    return pl


root_directory = r'million-playlist-dataset'
zipped_file = root_directory + '\spotify_million_playlist_dataset.zip'
jsons_directory = root_directory + '\data'

list_of_files = os.listdir(jsons_directory)

myfile = open('data\\all_jsons.json', 'a')

pl = {}

for f in list_of_files:
    
    data = loads_json(jsons_directory + '\\' + f)
    tmp_pl = extract_songs(data)
    pl = pl | tmp_pl
    
myfile.write(json.dumps(pl, sort_keys=True, indent=4))

myfile.close()