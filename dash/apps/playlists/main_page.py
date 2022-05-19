from dash import html
import dash_bootstrap_components as dbc

layout = html.Div(
    [
      dbc.Col(
                    [
                        html.P('\n'),
                        dbc.Button(
                            "Login with Spotify", 
                            color="success", 
                            id='pl-login_button',
                            className="me-1",
                            n_clicks=0
                            ),
                    ],
                )
    ]
)