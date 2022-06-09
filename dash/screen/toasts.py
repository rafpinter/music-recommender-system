from dash import dcc
import dash_bootstrap_components as dbc
from dash import html


def create_toast(comp_id = '', header_text = '', loading_n = ''):

        return dbc.Col(
                dbc.Toast(
                        [
                            dcc.Markdown(
                                id = comp_id,
                                children = ''
                            ),
                            html.Br(),
                            html.Br(),
                            html.Br(),
                            dcc.Loading(
                                id=f"pl-loading-{loading_n}",
                                type="default",
                                children=html.Div(id=f"pl-loading-output-{loading_n}"),
                                color='#01a077'
                            )
                            ],
                        header=header_text,
                        style={
                            'width': '100%',
                            'height': '700px',
                            'textAlign': 'center',
                            'margin': '10px',
                            'overflowY': 'scroll'
                        } 
                    ),
                width=12
        )