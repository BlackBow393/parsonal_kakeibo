from dash import Input, Output, State
from dash_app.folder_selecter import choose_folder
import os, json
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def register_callbacks(dash_app):
    # 初期読み込み
    @dash_app.callback(
        Output('folder-Path', 'value'),
        Input('folder-Path', 'id') # ダミーInput
    )
    def load_initial_folder():
        config = load_config()
        return config.get('folder-Path', '')
    
    # フォルダー選択
    @dash_app.callback(
        Output('folder-Path', 'value'),
        Output('folder-table', 'columns'),
        Output('folder-table', 'data'),
        Input('folder-Btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def select_folder(n_clicks):
        
        folder_path = choose_folder()
        
        if not folder_path:
            return '', [], []
        
        files = []
        for name in os.listdir(folder_path):
            full_path = os.path.join(folder_path, name)
            files.append({
                "name": name,
                "type": "フォルダ" if os.path.isdir(full_path) else "フォルダ"
            })
        
        columns = [
            {"name":"名前", "id":"name"},
            {"name":"種別", "id":"type"}
        ]
        
        return folder_path, columns, files
    
    @dash_app.callback(
        Output("sidebar", "className"),
        Output("overlay", "className"),
        Input("menu-toggle", "n_clicks"),
        Input("overlay", "n_clicks"),
        State("sidebar", "className"),
        prevent_initial_call=True
    )
    def toggle_sidebar(menu_clicks, overlay_clicks, current_class):
        if current_class and "active" in current_class:
            return "sidebar", "overlay"
        else:
            return "sidebar active", "overlay active"
