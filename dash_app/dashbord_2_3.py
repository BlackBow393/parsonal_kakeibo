from dash import Dash, dcc, html
from dash_app.assets.tab_2_3_0 import create_layout
from dash_app.assets.callback_2_3 import register_callbacks

def create_dash_app2_3(flask_app):
    dash_app = Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dash2-3/',
        assets_folder="assets"
    )
    
    dash_app.layout = create_layout()
    
    register_callbacks(dash_app)
    
    return dash_app