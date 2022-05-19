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
import secrets
import string
from urllib.parse import urlencode

from dash import html, dcc, Dash
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc

from apps.playlists import playlist_continuation
from apps.playlists import main_page


from apps.playlists.callbacks import *
from apps.playlists.graphs import *

from header import header

from apps.playlists.class_playlists import PLAYLISTRECSYS

from spotify_functions import (
    load_json, 
    load_data, 
    connect_to_spotify, 
    get_playlist_metadata
    )

path_to_credentials = 'spotify_codes.json'
    
CREDENTIALS = load_json(path_to_credentials)

song_infos, dataframe, num_to_id, id_to_num = load_data()

# Global variables
playlistrecsys =  PLAYLISTRECSYS()
playlistrecsys.sp = connect_to_spotify()

with open(path_to_credentials, 'r', encoding="utf8") as f:
    codes = json.load(f)

playlistrecsys.client_id = codes['client_id']
playlistrecsys.client_secret = codes['client_secret']


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
    '''Refresh access token.'''
    print('log | refresh | 1')
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': session.get('tokens').get('refresh_token'),
    }
    authorization = b64encode(f'{playlistrecsys.client_id}:{playlistrecsys.client_secret}'.encode()).decode()
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Authorization': f'Basic {authorization}'}
    print('log | refresh | 2')
    res = requests.post(
        playlistrecsys.TOKEN_URL, auth=(playlistrecsys.client_id, playlistrecsys.client_secret), data=payload, headers=headers
    )
    print('log | refresh | 3')
    res_data = res.json()
    print('log | refresh | 4')
    # Load new token into session
    session['tokens']['access_token'] = res_data.get('access_token')

    return session['tokens']['access_token']


@server.route('/login')
def login():
    '''Login or logout user.

    Note:
        Login and logout process are essentially the same. Logout forces
        re-login to appear, even if their token hasn't expired.
    '''
    print('ENTROU NO LOGIN')

    # redirect_uri can be guessed, so let's generate
    # a random `state` string to prevent csrf forgery.
    state = ''.join(
        secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16)
    )

    # Request authorization from user
    scope = 'user-read-private user-read-email'

    loginout = 'login'

    if loginout == 'logout':
        payload = {
            'client_id': playlistrecsys.client_id,
            'response_type': 'code',
            'redirect_uri': playlistrecsys.LOGIN_REDIRECT_URI,
            'state': state,
            'scope': playlistrecsys.scope,
            'show_dialog': True,
        }
    elif loginout == 'login':
        payload = {
            'client_id': playlistrecsys.client_id,
            'response_type': 'code',
            'redirect_uri': playlistrecsys.LOGIN_REDIRECT_URI,
            'state': state,
            'scope': playlistrecsys.scope,
        }
    else:
        abort(404)

    res = make_response(redirect(f'{playlistrecsys.AUTH_URL}/?{urlencode(payload)}'))
    res.set_cookie('spotify_auth_state', state)

    print(type(res))
    print(res)


    print('SAINDO DO LOGIN')
    return res


@server.route('/callback')
def callback():
    print('ENTROU NO CALLBACK')
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

    # `auth=(playlistrecsys.client_id, SECRET)` basically wraps an 'Authorization'
    # header with value:
    # b'Basic ' + b64encode((playlistrecsys.client_id + ':' + SECRET).encode())
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

    print('user:', playlistrecsys.user)

    print('SAINDO DO CALLBACK')
    return redirect('http://127.0.0.1:8050/playlist-continuation')



@app.callback(
    Output("page-content", "children"), 
    [
        Input("url", "pathname"),
        Input('url_refresh', 'pathname')
    ],
    # prevent_initial_call=True
    )
def render_page_content(pathname,url_refresh):
    """render_page_content
    Callback that creates the multi-page dash. Switches from page to page.

    Args:
        pathname (str): name of the page to view

    """
    if url_refresh == "/":
        # return html.P("This is the content of the home page!")
        return main_page.layout

    elif url_refresh == "/playlist-continuation":
        
        return playlist_continuation.layout
    # If the user tries to reach a different page, return a 404 message
    # else:
    #     return html.P("Page not found")
    return


@app.callback(
    Output('url_refresh', 'pathname'),
    [
        Input('pl-login_button', 'n_clicks')
    ],
    prevent_initia_callback=True,    
)
def user_login(n):
    
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
        (img, 
         name, 
         owner, 
         followers, 
         description, 
         total_n_tracks) = get_playlist_metadata(playlistrecsys.sp, url)
        
        playlistrecsys.fill_pl_metadata(img, name, owner, followers, description, total_n_tracks)
        
        return img, name, owner, followers, description, total_n_tracks


@app.callback(
    Output('pl-md_text_playlist', 'children'),
    # [Input('url_input', 'value')],
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
        # Output('pl-alg_name', 'children'),
        # Output('pl-execution_time', 'children'),
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
        # print("getting oauth")
        # sp_oauth = SpotifyOAuth(scope=playlistrecsys.scope, 
        #                   client_id=playlistrecsys.client_id,
        #                   client_secret=playlistrecsys.client_secret,
        #                   redirect_uri=playlistrecsys.redirect_uri)

        
        print(playlistrecsys.sp.current_user())
        
        print("new_playlist:")
        new_playlist = playlistrecsys.sp.user_playlist_create(user=playlistrecsys.sp.current_user(),
                                                              name='test_playlist',
                                                              public=True,
                                                              description='created with app',
                                                              )
        print(new_playlist)
        
        print('last_items:')
        last_items = playlistrecsys.get_track_ids_last_train()
        print(last_items)
        
        playlistrecsys.sp.playlist_add_items(new_playlist['id'], items=last_items)
        print('songs added')
        
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
    # return ['']
    
    
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
    # return ['']
    
    
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

        # token = refresh()

        token = session['tokens']['access_token']

        print(f'token: {token}')

        headers = {'Authorization': f"Bearer {token}",
                   "Content-Type": "application/json"}
        res_me = requests.get(playlistrecsys.ME_URL, headers=headers)
        
        # print('res_me', res_me.text)
        
        user_id = playlistrecsys.user['id']
        
        # criando playlist 
        data = json.dumps({
            'name': 'Nova Playlist: SpotiRecs',
            'description': 'Playlist criada a partir do melhor software de recomendação de musicas',
            'public': True
        })
        
        url = f'{playlistrecsys.CREATE_PLAYLIST_URL}/{user_id}/playlists'
        # print('url', url)
        
        res_crpl = requests.post(url, data = data, headers=headers)
        # print('res_crpl', res_crpl.text)        
        # print('json res_crpl:', res_crpl)
        new_playlist_id = res_crpl.json()["id"]
        # print('new_playlist_id:', new_playlist_id)

        # adicionando músicas na playlist
        add_url = f'{playlistrecsys.ADD_SONGS_PLAYLIST_URL}/{new_playlist_id}/tracks'
        ids = list(playlistrecsys.get_track_ids_last_train())
        uris = [f'spotify:track:{x}' for x in ids]
        
        # print('add_url', add_url)
        # print('uris:', uris)
        body = json.dumps({
            'uris': uris
        })
        res_add = requests.post(add_url, data=body, headers=headers)
        # print('res_add:', res_add.text)        
        # print('res_add status:', res_add.status_code)
        
        return 'Done!'

# ## -----------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=False, use_reloader=False)