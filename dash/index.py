import os
import time
import json
import string
import secrets
import requests
from base64 import b64encode
from datetime import datetime
from flask import (
    abort,
    make_response,
    redirect,
    request,
    session,
)
import da3sh_bootstrap_components as dbc
from urllib.parse import urlencode
from dash import html, dcc, Dash
from dash.dependencies import Output, Input, State
from apps.screen import playlist_continuation
from apps.screen import main_page
from apps.functions.class_playlists import PLAYLISTRECSYS
from apps.functions.graphs import *
from apps.functions.callbacks import *
from apps.functions.spotify_functions import (
    load_json, 
    load_data, 
    connect_to_spotify, 
    get_playlist_metadata
    )
from header import header

# Global variables

path_to_credentials = 'spotify_codes.json'
CREDENTIALS = load_json(path_to_credentials)    

song_infos, dataframe, num_to_id, id_to_num = load_data()

playlistrecsys =  PLAYLISTRECSYS()
playlistrecsys.sp = connect_to_spotify()
playlistrecsys.client_id = CREDENTIALS['client_id']
playlistrecsys.client_secret = CREDENTIALS['client_secret']


#  ----------------------


# Bootstrap themes by Ann: https://hellodash.pythonanywhere.com/theme_explorer
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server
server.secret_key = os.urandom(16)
app.config.suppress_callback_exceptions = True

app.layout = dbc.Container(
    [
        # primeira linha
        header(),
        
        html.Br(),
              
        dcc.Location(id='url', refresh=False, pathname='/'),
        dcc.Location(id='url_refresh', refresh=True),
        
        html.Br(),
        
        html.Div(
            children=[main_page.layout],
            id='page-content'
        ),
        
        html.Div(
            children=[''],
            id='pl-exported_completed'
        ),
    ]
)

def refresh():
    """Refreshing the access token"""
    return refresh_acess_token(session, playlistrecsys)


@server.route('/login')
def login():
    """Login or logout user.

    Note:
        Login and logout process are essentially the same. Logout forces
        re-login to appear, even if their token hasn't expired.
    """
    return login_user(playlistrecsys)


@server.route('/callback')
def callback():
    return callback_route(playlistrecsys)



@app.callback(
    Output("page-content", "children"), 
    [
        Input("url", "pathname"),
        Input('url_refresh', 'pathname')
    ],
    )
def render_page_content(pathname,url_refresh):
    """render_page_content
    Callback that creates the multi-page dash. Switches from page to page.

    Args:
        pathname (str): name of the page to view

    """
    if url_refresh == "/":
        return main_page.layout

    elif url_refresh == "/playlist-continuation":        
        return playlist_continuation.layout

    return


@app.callback(
    Output('url_refresh', 'pathname'),
    [
        Input('pl-login_button', 'n_clicks')
    ],
    prevent_initia_callback=True,    
)
def user_login(n):
    """Redirect to user login"""
    if n > 0:
        return '\login'


# playlist_continuation

@app.callback(
    [
        Output('pl-image', 'src'),
        Output('pl-name', 'children'),
        Output('pl-owner', 'children'),
        Output('pl-followers', 'children'),
        Output('pl-description', 'children'),
        Output('pl-total_n_tracks', 'children'),
    ],
    [
        Input('pl-trigger_button', 'n_clicks')
    ],
    [
        State('pl-url_input', 'value'),
    ],
    prevent_initial_call=True
)
def pl_metadata(n, url):
    """pl_metadata
    Makes a Spotify API request to retrieve playlist's metadata

    Args:
        n (int): number of clicks
        url (str): playlist url

    Returns:
        playlist's image, name, owner, followers, description, total tracks
    """
    
    if n > 0:
        (img, name, owner, followers, description, total_n_tracks) = get_playlist_metadata(playlistrecsys.sp, url)
        
        playlistrecsys.fill_pl_metadata(img, name, owner, followers, description, total_n_tracks)
        
        return img, name, owner, followers, description, total_n_tracks


@app.callback(
    Output('pl-md_text_playlist', 'children'),
    [
        Input('pl-trigger_button', 'n_clicks')
    ],
    [
        State('pl-url_input', 'value'),
        State('pl-n_recs_input', 'value'),
    ],
    prevent_initial_call=True
)
def user_playlist_info(n, url, n_recs):
    """user_playlist_info
    gets the playlist url, searches for matches in the training 
    database and returns a string containg the matched results.

    Args:
        n (int): number of times the submit button has been pressed
        url (str): playlist url
        alg (str): selected algorithm

    Returns:
        str: a string containing all the matched songs between the
        user's playlist and our database
    """
    if n > 0:

        # Definindo atributo de url da playlist
        playlistrecsys.usr_playlist_url = url
        playlistrecsys.algorithm = 'als'
        playlistrecsys.N_RECOMMENDATIONS = int(n_recs)

        # Buscando dados da playlist
        playlist_str, playlist_ids = playlistrecsys.get_playlist(CREDENTIALS,
                                                                 playlistrecsys.sp,
                                                                 id_to_num,
                                                                 song_infos,
                                                                 num_to_id)

        # Populando demais atributos
        playlistrecsys.usr_playlist_song_ids = playlist_ids

        return playlist_str


@app.callback(
    [
        Output('pl-md_text_recomendation', 'children'),
        Output("pl-loading-output-2", "children"),
        Output("pl-export", "disabled"),
    ],
    [
        Input('pl-trigger_button', 'n_clicks')
    ],
    [
        State('pl-url_input', 'value'), 
        State('pl-db_fraction', 'value'),
        State('pl-n_recs_input', 'value'),
        State('pl-implicit_factors', 'value'),
        State('pl-implicit_regularization', 'value'),
        State('pl-implicit_iterations', 'value'),
        State('pl-implicit_alpha', 'value'),
    ],
    prevent_initial_call=True
)
def recommended_playlist_info(n, 
                             url, 
                             db_fraction,
                             nrecs,
                             implicit_factors, 
                             implicit_regularization, 
                             implicit_iterations, 
                             implicit_alpha,
                             ):
    """recommended_playlist_info
    creates recommendations for the user's playlist using the input settings

    Args:
        n (int): number of times the submit button is pressed
        url (str): user's playlist url
        implicit_factors (int): number os factors to use in the implicit algorithm
        implicit_regularization (float): regularization factor for the implicit algorithm
        implicit_iterations (int): number of iteractions for the implicit algorithm

    Returns:
        str: recomended songs for the playlist
    """
    
    if n > 0:
    
        start = time.time()
        
        args = {
            'factors': int(implicit_factors),
            'regularization': float(implicit_regularization),
            'iterations': int(implicit_iterations),
        }
        
        playlistrecsys.N_RECOMMENDATIONS = nrecs
                
        print("args:", args)
        print("db_fraction:", db_fraction)
        print('n recs:', playlistrecsys.N_RECOMMENDATIONS)
        
        recs_str, recs_ids_playlist = implicit_recsys(url=url,
                                                      alg='als',
                                                      alpha=implicit_alpha,
                                                      id_to_num=id_to_num,
                                                      song_infos=song_infos,
                                                      num_to_id=num_to_id,
                                                      dataframe=dataframe,
                                                      CREDENTIALS=CREDENTIALS,
                                                      sp=playlistrecsys.sp,
                                                      N_RECOMMENDATIONS=playlistrecsys.N_RECOMMENDATIONS,
                                                      db_fraction=db_fraction,
                                                      **args)
        
        end = time.time()
        
        exec_time = f"Training time: {round((end - start), 2)} s"
        
        print(exec_time)
        
        playlistrecsys.append_df_exec_time(factors=args['factors'],
                                           iterations=args['iterations'],
                                           regularization=args['regularization'],
                                           n=n,
                                           db_fraction=db_fraction,
                                           alpha=implicit_alpha,
                                           exec_time=(end - start))
        
        print('recs list:', recs_str)
        
        playlistrecsys.creating_dfs(recs_ids_playlist, n, playlistrecsys.sp, num_to_id)
                    
        return recs_str, "", False #, "Alternating Least Squares", exec_time
        
              
        
@app.callback(
 [
        Output('pl-radar_plot', 'figure'),
        Output('pl-year_plot', 'figure'),
        Output('pl-key_mode_plot', 'figure'),
        Output('pl-tempo_plot', 'figure'),
    ],
    [
        Input('pl-md_text_recomendation', 'children')
    ],
    prevent_initial_call=True    
)
def creating_plots(recs):
    
        radar_fig = create_radar_plot(playlistrecsys.df)
        violin_fig = create_year_plot(playlistrecsys.df)
        key_mode_fig = create_key_mode_plot(playlistrecsys.df)
        tempo_fig = create_tempo_plot(playlistrecsys.df)
        
        return radar_fig, violin_fig, key_mode_fig, tempo_fig



@app.callback(
    [
        Output('pl-exported_completed', 'children'),
    ],
    [
        Input('pl-export', 'n_clicks')
    ],
    prevent_initial_call=True
)
def recommended_playlist_info(n):
    
    if n > 0:
        
        print(playlistrecsys.sp.current_user())
        
        new_playlist = playlistrecsys.sp.user_playlist_create(user=playlistrecsys.sp.current_user(),
                                                              name='test_playlist',
                                                              public=True,
                                                              description='created with app',
                                                              )
        
        last_items = playlistrecsys.get_track_ids_last_train()
        
        playlistrecsys.sp.playlist_add_items(new_playlist['id'], items=last_items)
        
        return ["playlist loaded"]

    return ['']


@app.callback(
    [
        Output("pl-line_plot", 'figure')
    ],
    [
        Input("pl-df_exec_button", 'n_clicks')  
    ],
    [
        State("pl-color", "value"),
        State("pl-x", "value"),
    ],
    prevent_initial_callback=True
)
def update_graph(n, color, x):
    if n > 0:
        figure = create_line_plot_df_exec(playlistrecsys, x, color)
        return [figure]
    
    
@app.callback(
    [
        Output("pl-strip_plot", 'figure')
    ],
    [
        Input("pl-x_strip", "value"),
    ],
    prevent_initial_callback=True
)
def dispersion_plot(x):
    
        figure = create_dispersion_plot(playlistrecsys.df,x)
        return [figure]
    
    
@app.callback(
    [
        Output('pl-table', 'columns'),
        Output('pl-table', 'data'),
        Output('pl-table', 'page_size'),
    ],
    [
        Input('pl-md_text_recomendation', 'children')
    ],
)
def update_datatable(n):
    
    df = playlistrecsys.df
    df = df[df['type'] == 'recommended songs']
    cols = ['label', 'artist', 'name', 'album']
    df_sel = df[cols]
    
    columns = [{"name": i, "id": i} for i in df_sel.columns]
    data = df_sel.to_dict('records')
    page_size = playlistrecsys.N_RECOMMENDATIONS
    
    return  columns, data, page_size

    
@app.callback(
    [
        Output('pl-parameters', 'columns'),
        Output('pl-parameters', 'data'),
    ],
    [
        Input('pl-md_text_recomendation', 'children')
    ]
)
def update_datatable_parameters(n):

    df_sel = playlistrecsys.df_exec
    
    columns = [{"name": i, "id": i} for i in df_sel.columns]
    data = df_sel.to_dict('records')

    return  columns, data


@app.callback(
    Output('auth_manager', 'children'),
    [
        Input("pl-export", "n_clicks")
    ]
)
def export_playlist(n):    
    if n > 0:
        
        export_playlist_to_spotify(session, playlistrecsys)
        
        return 'Done!'

@app.callback(
    Output("pl-download_raw_data", 'data'),
    Input("pl-download_raw_data_button", 'n_clicks'),
    prevent_initial_callback=True
)
def download_raw_data(n):
    """Download dos dados crus das recomendações

    Args:
        n (int): número de vezes que o botão é pressionado

    Returns:
        csv: dataframe
    """
    if n:
        return dcc.send_data_frame(playlistrecsys.df.to_csv, 
                                   "raw_data_{:%Y%m%d_%H%M%S}.csv".format(datetime.now()))

@app.callback(
    Output("pl-download_exec_time", 'data'),
    Input("pl-download_exec_time_button", 'n_clicks'),
    prevent_initial_callback=True
)
def download_exec_time(n):
    """Download dos dados crus de execução dos modelos

    Args:
        n (int): número de vezes que o botão é pressionado

    Returns:
        csv: dataframe
    """
    if n:
        return dcc.send_data_frame(playlistrecsys.df_exec.to_csv,
                                   "execution_data_{:%Y%m%d_%H%M%S}.csv".format(datetime.now()))

# ## -----------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=False, use_reloader=False)