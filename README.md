# music-recommender-system

This project is an ongoing submition for the [Spotify Million Playlist Dataset Challenge](https://www.aicrowd.com/challenges/spotify-million-playlist-dataset-challenge). It creates an interactive Plotly Dash web interface to test different recommender systems.

By default, it is a recommender system for playlist continuation that allows you to:  
    1. Log in with your Spotify account;  
    2. Upload a public playlist url;  
    3. Customize the hyperparameter of a playlist recommender system;  
    4. Explore the ouputs of different recommendations;  
    5. Export the final mixed playlist to Spotify.  
   

---

## How to use:

There are a few steps you need to do before you can use the inferface to test a recommender system:  
1. Create Spotify credentials
2. Get and process the challenge's raw data
3. Run the application

### 0. Before starting

Please install the required libraries by running the following command:

```
pip install -r requirements.txt
```

Note that your terminal need to be placed at the root folder.

### 1. Creating Spotify credentials

To use this project, you need to have a [Spotify for Developer](https://developer.spotify.com/dashboard/) account to acess the dashboard page.


Once logged in, you need to create a new app and update the `spotify_codes.json` file with your information:
```json
{
    "client_id" :  "yourClientId",
    "client_secret" : "yourClientSecret",
    "user": "yourUser"
}
```

### 2. Getting raw data

As stated before, this project is an ongoing submission for the [Spotify Million Playlist Dataset Challenge](https://www.aicrowd.com/challenges/spotify-million-playlist-dataset-challenge). Hence, this application uses the challenge's raw data to produce recommendations.

If you are applying for the challenge as well and want to test your algorithm, please note that the dataset need to be exacly like this for the processing scripts to work:

```
- million-playlist-dataset/
    |
    |__ million_playlist_dataset.zip
```

#### Proocessing raw data

Once you have placed the `.zip` file in the `million-playlist-dataset/` folder, you can run the data processing scripts that are inside de `scripts/` folder. Note that you need to execute in the following order:

1. 1_modify_json.py
2. 2_song_infos.py
3. 3_mappings.py
4. 4_final_jsons.py

### 3. Run the application

To run the application, execute the file `dash/index.py`.


---
