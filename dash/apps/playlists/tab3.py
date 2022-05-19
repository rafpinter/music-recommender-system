from dash import dcc
import dash_bootstrap_components as dbc
from dash import html, dash_table


tab3_content = html.Div(
    [
        html.Br(),
        html.Br(),
        
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3("Average metrics"),
                        dbc.Col(
                            dcc.Graph(id='pl-radar_plot', figure={}),
                        )
                    ],
                    width=12
                )
            ]
        ),
        
        html.Br(),
        html.Br(),
        
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3("Release year"),
                        dbc.Col(
                            dcc.Graph(id='pl-year_plot', figure={}),
                        )
                    ],
                    width=12
                )
            ]
        ),
        html.Br(),
        html.Br(),
        
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3("Keys"),
                        dbc.Col(
                            dcc.Graph(id='pl-key_mode_plot', figure={}),
                        )
                    ],
                    width=12
                ),
            ],
        ),
                
        html.Br(),
        html.Br(),
        
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3("Tempo"),
                        dbc.Col(
                            dcc.Graph(id='pl-tempo_plot', figure={}),
                        )
                    ],
                    width=12
                ),
            ]
        ),
        html.Br(),
        html.Br(),
    ]

)
