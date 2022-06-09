from dash import html
import dash_bootstrap_components as dbc

implicit_inputs = [
    html.Br(),
    dbc.Row(
        [ 
            dbc.Col(
                [
                    html.P('Factors:'),
                    dbc.Input(
                        id='pl-implicit_factors',
                        type='number',
                        value=1,
                    ),  
                ]
            ),
            
            dbc.Col(
                [
                    html.P('Regularization:'),
                    dbc.Input(
                        id='pl-implicit_regularization',
                        type='number',
                        value=1,
                    ),
                ]
            ),
            
            dbc.Col(
                [
                    html.P('Iterations:'),
                    dbc.Input(
                        id='pl-implicit_iterations',
                        type='number',
                        min=1,
                        value=1,
                    ),
                ]
            ),
            
            dbc.Col(
                [
                    html.P('Alpha:'),
                    dbc.Input(
                        id='pl-implicit_alpha',
                        type='number',
                        min=1,
                        value=1,
                    ),
                ]
            ),
            
            html.Br(),
        ]
    )
]

implicit_specific_input = html.Div(
                        children=implicit_inputs,
                        id='pl-specific_input_implicit',
                        # hidden=False,
                    )
