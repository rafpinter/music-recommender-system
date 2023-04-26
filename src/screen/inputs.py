from dash import dcc
import dash_bootstrap_components as dbc
from dash import html


def url_input():    
    return dbc.Col(
                    [   
                        html.P('Playlist URL'),
                        dbc.Input(
                            id="pl-url_input", 
                            placeholder="Paste playlist url...", 
                            type="text"
                        ),
                    ],
                width=7
                )
    
    
def n_recs_input():
    return dbc.Col(
                    [   
                        html.P('Number of recommendations'),
                        dbc.Input(
                            id="pl-n_recs_input", 
                            # placeholder="Paste playlist url...", 
                            type="number",
                            min=1,
                            max=100,
                            value=20,
                        ),
                    ],
                width=3
                )

def submit_button():
    return dbc.Col(
                    [
                        html.P('\n'),
                        dbc.Button(
                            "Get recommendations", 
                            color="success", 
                            id='pl-trigger_button',
                            className="me-1",
                            n_clicks=0
                            ),
                    ],
                width=3
                )

def db_fraction():
    return dbc.Col(
                [   
                    html.P('Database percentage'),
                    dbc.Select(
                        id="pl-db_fraction", 
                        options=[
                            {"label": "100%", "value": 1},
                            {"label": "90%", "value": 0.9},
                            {"label": "75%", "value": 0.75},
                            {"label": "50%", "value": 0.5},
                            {"label": "25%", "value": 0.25},
                            {"label": "10%", "value": 0.1},
                            {"label": "1%", "value": 0.01},
                        ],
                        value=1,
                    ),
                ],
            width=2
            )