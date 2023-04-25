from dash import dcc
import dash_bootstrap_components as dbc
from dash import html, dash_table


tab5_content = html.Div(
    [
        html.Br(),
        html.Br(),
        
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3("Training parameters"),
                        dbc.Col(
                            dash_table.DataTable(id='pl-parameters'),
                        ),
                        
                        html.Br(),
                        html.Br(),
                        
                        html.H3("Raw data"),
                        dbc.Col(
                            dash_table.DataTable(id='pl-table'),
                        )
                    ],
                    width=12
                )
            ]
        ),
        
        html.Br(),
        html.Br(),
        
        dbc.Button("Download raw data", 
                    color="download_raw_data_button", 
                    id='pl-download_raw_data_button',
                    className="me-1",
                    n_clicks=0
                    ),
        dcc.Download(id="pl-download_raw_data"),
        
        html.Br(),
        
        dbc.Button("Download execution time data", 
            color="download_exec_time_button", 
            id='pl-download_exec_time_button',
            className="me-1",
            n_clicks=0
            ),
        dcc.Download(id="pl-download_exec_time"),
        
        html.Br(),
        html.Br(),
    ]

)
