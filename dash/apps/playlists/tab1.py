from dash import dcc
import dash_bootstrap_components as dbc
from dash import html


# introdução

tab1_content = dbc.Card(
    dbc.CardBody(
        [
            html.P("Aqui virão as informações do modelo e do projeto!", className="card-text"),
            
        ]
    ),
    className="mt-3",
)
