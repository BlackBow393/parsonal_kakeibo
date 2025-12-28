from dash import Dash
from dash_app.assets.tab_2_3_0 import create_layout
from dash_app.assets.callback_2_3 import register_tab_callbacks
from dash_app.assets.tab_2_3_1.callback_2_3_1 import register_callbacks_2_3_1
from dash_app.assets.tab_2_3_2.callback_2_3_2 import register_callbacks_2_3_2
from dash_app.assets.tab_2_3_3.callback_2_3_3 import register_callbacks_2_3_3

def create_dash_app2_3(flask_app):
    dash_app = Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dash2-3/',
        assets_folder="assets",
        suppress_callback_exceptions=True
    )
    
    dash_app.layout = create_layout()
    
    register_tab_callbacks(dash_app)
    register_callbacks_2_3_1(dash_app)
    register_callbacks_2_3_2(dash_app)
    register_callbacks_2_3_3(dash_app)
    
    return dash_app