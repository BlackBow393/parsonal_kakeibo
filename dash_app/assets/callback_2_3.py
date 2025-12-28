from dash import Input, Output
from dash_app.assets import tab_2_3_1, tab_2_3_2, tab_2_3_3
import os, json

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def register_callbacks(dash_app):
    
    @dash_app.callback(
        Output("asset-tab-content", "children"),
        Input("asset-tabs", "value")
    )
    def render_tab(tab):
        if tab == "all":
            return tab_2_3_1.layout()
        elif tab == "saving":
            return tab_2_3_2.layout()
        elif tab == "debt":
            return tab_2_3_3.layout()