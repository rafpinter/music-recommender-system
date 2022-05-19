from dash import dcc
import dash_bootstrap_components as dbc
from dash import html


tab3_content = html.Div(
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
                         dbc.Select(
                            id="pl-x",
                            options=[
                                {"label": "Factors", "value": "factors"},
                                {"label": "Iterations", "value": "iterations"},
                                {"label": "Regularization", "value": "regularization"},
                                {"label": "Database Percentage", "value": "db_fraction"},
                                {"label": "Alpha", "value": "alpha"},
                            ],
                        ),
                         
                        html.Br(),
                        html.Br(),
                        
                        html.H3("Color"),
                        dbc.Select(
                            id="pl-color",
                            options=[
                                        {"label": "Factors", "value": "factors"},
                                        {"label": "Iterations", "value": "iterations"},
                                        {"label": "Regularization", "value": "regularization"},
                                        {"label": "Database Percentage", "value": "db_fraction"},
                                        {"label": "Alpha", "value": "alpha"},
                                    ],
                                ),
                        
                        html.Br(),
                        html.Br(),
                        
                        dbc.Button(
                            "Update graph", 
                            color="success", 
                            id='pl-df_exec_button',
                            className="me-1",
                            n_clicks=0
                        ),
                    ],
                    width={"size": 2}
                ),
                dbc.Col(
                    [
                        dcc.Graph(id='pl-line_plot', figure={}),
                    ],
                ),
            ],
        ),        

        
        html.Br(),
        html.Br(),
        
    ]

)
