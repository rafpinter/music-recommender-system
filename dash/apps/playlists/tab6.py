from dash import dcc
import dash_bootstrap_components as dbc
from dash import html, dash_table


tab6_content = html.Div(
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
        
    ]

)
