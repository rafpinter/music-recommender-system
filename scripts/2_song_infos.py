import json
import os

def loads_json(path):
    f = open(path)
    js = f.read()
    f.close()
    
    data = json.loads(js)
    data = data['playlists']
    
    return data


def extract_playlist(playlists):
    """extract_playlist
    """
    
    global set_of_songs
    global song_infos
    
    for playlist in playlists:
        tracks = playlist['tracks']
        
        for track in tracks:
            track_id = track['track_uri'].split(':')[2]
            try:
                song_infos[track_id]
            except KeyError:
                song_infos[track_id] = {'artist_name': track['artist_name'],
                                    'track_uri': track['track_uri'],
                                    'artist_uri': track['artist_uri'],
                                    'track_name': track['track_name'],
                                    'album_uri': track['album_uri'],
                                    'album_name': track['album_name']
                                    }
                set_of_songs.add(track['track_uri'].split(':')[2])
            else:
                continue
    
    
    return


set_of_songs = set()
song_infos = dict()
directory = r'million-playlist-dataset/data/'
data_directory = r'data'

# list of files
list_of_files = os.listdir(directory)

i=0
# populating file
for f in list_of_files:
    print(f"Loading {i}")
    playlists = loads_json(directory + f)
    extract_playlist(playlists)
    i+=1

# creating file
myfile = open(data_directory + r'\songs_infos.json', 'w')
# creating file
myfile.write(json.dumps(song_infos, sort_keys=True, indent=4))
myfile.close()