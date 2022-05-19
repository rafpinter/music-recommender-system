import json
import pandas as pd

def loads_json(path):
    f = open(path)
    js = f.read()
    f.close()
    data = json.loads(js)
    return data

data_directory = r'data'
all_jsons_path = data_directory + r'\all_jsons.json'

data_dict = loads_json(all_jsons_path)
id_to_num = loads_json(data_directory + r'\id_to_num.json')
tups = []

for key, value in data_dict.items():
    for id in value:
        tups.append((key, id))

df = pd.DataFrame(tups, columns=['playlist_id', 'song_id'])

df['song_id'] = df['song_id'].apply(lambda x: id_to_num[x])

df.to_csv(data_directory+ r"\df_playlist_and_songs.csv", index=False)