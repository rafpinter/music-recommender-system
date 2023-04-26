from dash import html
import dash_bootstrap_components as dbc

# components
from src.screen.inputs import url_input, submit_button, db_fraction, n_recs_input
from src.functions.specific_inputs_implicit import implicit_specific_input

# tabs
from .tabs import tabs

layout = html.Div(
    [
        # segunda linha
        dbc.Row(
            [
                # primeira coluna
                url_input(),

                # segunda coluna
                # algorithm_input(),
                
                # terceira coluna
                db_fraction(),
                
                n_recs_input(),
                
                # specific_input
                implicit_specific_input,
            ]
        ),
        
        dbc.Row(
            [
                # terceira coluna
                submit_button()
            ]
        ),
        
        html.Br(),
        
        # quinta linha
        tabs
    ]
)