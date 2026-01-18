from dash import Dash
from dash_app.layout_5 import serve_layout
from dash_app.callback_5 import register_callbacks  # コールバックをインポート
import json, os

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def create_dash_app5(flask_app):
    dash_app = Dash(
        __name__,
        server=flask_app,
        #url_base_pathname='/dash5/',   #iframe利用時
        url_base_pathname='/setting/',   #iframe非利用時
        suppress_callback_exceptions=True,
        assets_folder="assets",
        title="個人家計簿アプリ　～設定～"
    )
    
    dash_app.layout = lambda: serve_layout(load_config())

    # コールバック登録（コールバック側で最新の config.json を参照）
    register_callbacks(dash_app)
    
    return dash_app
