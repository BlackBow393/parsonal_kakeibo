from dash import Dash
from dash_app.tab_4 import create_layout
from dash_app.callback_4_3 import register_tab_callbacks
from dash_app.tabs.tab_4_1.callback_4_1 import register_callbacks_4_1
from dash_app.tabs.tab_4_2.callback_4_2 import register_callbacks_4_2
from dash_app.tabs.tab_4_3.callback_4_3 import register_callbacks_4_3

def create_dash_app4_3(flask_app):
    dash_app = Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dash4-3/',   #iframe利用時
        #url_base_pathname='/asset/',   #iframe非利用時
        title="個人家計簿アプリ",
        suppress_callback_exceptions=True
    )
    
    dash_app.layout = create_layout()
    
    register_tab_callbacks(dash_app)
    register_callbacks_4_1(dash_app)
    register_callbacks_4_2(dash_app)
    register_callbacks_4_3(dash_app)
        
    return dash_app