import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
from .toasts import create_toast


tab1_content = html.Div(
    [
        html.Br(),
        html.Br(),
        html.Br(),
        
        dbc.Card(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.CardImg(
                                src="",
                                className="img-fluid",
                                id='pl-image',
                                style={
                                    "maxWidth": "250px",
                                    'margin-left': 'auto',
                                    'display': 'block',
                                    # 'margin-right': 'auto',
                                    }
                            ),
                            className="col-md-6",
                        ),
                        dbc.Col(
                            dbc.CardBody(
                                [
                                    html.H3(id= 'pl-name', children= '', className="card-title"),
                                    html.Br(),
                                    html.H6(id= 'pl-owner', children= '', className="card-text"),
                                    html.H6(id= 'pl-followers', children= '', className="card-text"),
                                    html.H6(id= 'pl-total_n_tracks', children= '', className="card-text"),
                                    html.H6(id= 'pl-description', children= '', className="card-text text-muted"),
                                ]
                            ),
                            className="col-md-6",
                        ),
                    ],
                    className="g-0 d-flex align-items-center",
                )
            ],
            className="mb-3",
            style={
                'background-color': 'transparent',
                'border': 'none'
                },
        ),
        html.Br(),
        html.Br(),
        dbc.Row( 
            [
               # primeira coluna
               dbc.Col(
                   [
                       html.H4("Matched songs"),
                       create_toast(comp_id='pl-md_text_playlist', header_text='', loading_n=1),  
                   ]
               ),
               
               dbc.Col(
                   [
                       html.H4("Recommended songs"),
                       create_toast(comp_id='pl-md_text_recomendation', header_text='', loading_n=2)   
                   ]
               ),

               # segunda coluna
            ]
        ),
        
        # html.Br(),
        # html.Br(),
        
        # dbc.Row(
        #     [
        #         dbc.Col(
        #             [
        #                 # html.H3(id='pl-alg_name'),
        #                 # html.H5(id='pl-execution_time')
        #             ],
        #         )
        #     ]
        # ),
        
        html.Br(),
        html.Br(),
        
        # dbc.Row(
        #     [
        #         html.H3("Average metrics"),
        #         dbc.Col(
        #             dcc.Graph(id='pl-radar_plot', figure={}),
        #         )
        #     ]
        # ),
        dbc.Button(
                "Export playlist to Spotify", 
                color="success", 
                id='pl-export',
                className="me-1",
                n_clicks=0,
                disabled=True,
                ),
        
        html.Br(),
        html.Br(),
        
        html.P(id='auth_manager',),
        
        html.Br(),
        html.Br(),
        html.Br(),
    ]
)