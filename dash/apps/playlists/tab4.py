from dash import dcc
import dash_bootstrap_components as dbc
from dash import html


tab4_content = html.Div(
    [
        html.Br(),
        html.Br(),
        
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        
                         html.H3("X-Axis"),
                         dbc.RadioItems(
                            id="pl-x_strip",
                            options=[
                                {"label": "Popularity", "value": "popularity"},
                                {"label": "Length", "value": "length"},
                                {"label": "Acousticness", "value": "acousticness"},
                                {"label": "Danceability", "value": "danceability"},
                                {"label": "Energy", "value": "energy"},
                                {"label": "Instrumentalness", "value": "instrumentalness"},
                                {"label": "Liveness", "value": "liveness"},
                                {"label": "Loudness", "value": "loudness"},
                                {"label": "Speechiness", "value": "speechiness"},
                                {"label": "Valence", "value": "valence"},
                                {"label": "Tempo", "value": "tempo"},
                                {"label": "Time signature", "value": "time_signature"},    
                            ],
                            value='popularity'
                        ),
                         
                        html.Br(),
                        html.Br(),
                        
                    ],
                    width={"size": 2}
                ),
                dbc.Col(
                    [
                        dcc.Graph(id='pl-strip_plot', figure={}),
                    ],
                ),
            ],
        ),        

        html.Br(),
        html.Br(),
        
    ]

)
