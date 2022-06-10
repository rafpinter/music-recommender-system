# spotify-recommendation-system

This is a project that creates a playlist continuation tool based on the *Plotly Dash* and the *implicit* libraries.

It is a recommender system for playlist continuation that allows you to:  
    1. Log in with your Spotify account;  
    2. Upload a public playlist url;  
    3. Customize the hyperparameter of a playlist recommender system;  
    4. Explore the ouputs of different recommendations;  
    5. Export the final mixed playlist to Spotify.  


---

## How to use:

### Creating Spotify credentials

To use this project, you need to have a [Spotify for Developer](https://developer.spotify.com/dashboard/) account to acess the dashboard page.


Once logged in, you need to create a new app and update the `spotify_codes.json` file with your information:
```json
{
    "client_id" :  "yourClientId",
    "client_secret" : "yourClientSecret",
    "user": "yourUser"
}
```

### Getting training data

