import dash_bootstrap_components as dbc
from dash import html
from dash import dcc

from .tab1 import tab1_content
from .tab2 import tab2_content
from .tab3 import tab3_content
from .tab4 import tab4_content
from .tab5 import tab5_content
from .tab6 import tab6_content


tabs = dbc.Tabs(
    [
        # dbc.Tab(tab1_content, label="Intro"),
        dbc.Tab(tab2_content, label="Recommender"),
        dbc.Tab(tab3_content, label="Playlists metrics"),
        dbc.Tab(tab4_content, label="Explore"),
        dbc.Tab(tab5_content, label="Distribution"),
        dbc.Tab(tab6_content, label="Raw data"),
    ]
)