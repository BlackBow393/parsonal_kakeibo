from dash import Dash, dcc, html, dash_table
from dash_app.callbak_5 import register_callbacks  # コールバックをインポート

# サイドバー
def sidebar():
    return html.Div(
        id="sidebar",
        className="sidebar",
        children=[
            html.A("メインメニュー", href="/"),
            html.A("資産分析", href="/asset/"),
            html.A("収入分析", href="/income/"),
            html.A("支出分析", href="/expense/"),
            html.A("設定", href="/setting/")
        ]
    )

# オーバーレイ
def overlay():
    return html.Div(
        id="overlay",
        className="overlay"
    )

# メニュートグルボタン
def menu_button():
    return html.Button(
        "☰",
        id="menu-toggle",
        className="menu-btn",
        n_clicks=0
    )

# フッター
def footer():
    return html.Footer([
        html.P("最終更新日", className="footer_item"),
        html.P("Ver.1.0.0", className="footer_item"),
    ])

def create_dash_app5(flask_app):
    dash_app = Dash(
        __name__,
        server=flask_app,
        #url_base_pathname='/dash5/',   #iframe利用時
        url_base_pathname='/setting/',   #iframe非利用時
        suppress_callback_exceptions=True,
        assets_folder="assets",
        title="個人家計簿アプリ"
    )

    # 保存先が設定されている場合は、レイアウトを作成（コールバックで最新設定を参照）
    dash_app.layout = html.Div([
        
        # === 共通UI ===
        sidebar(),
        overlay(),
        menu_button(),
        
        # === ヘッダー ===
        html.Header(
            className="headder-setting",children=[
            html.H1("個人家計簿"),
            html.H2("設定"),
            html.Button("↻", id="refresh-btn", className="refresh-btn")
        ]),
        
        # === メイン ===
        html.Main([
            html.H2("取り込みフォルダ"),
            
            html.Div(className='setting-area',children=[
                html.Button("📁", id="folder-Btn"),
                html.Input(
                    id="folder-Path",
                    value="",
                    readOnly=True
                )
            ]),
            
            # Loadingを有効化するためにラップ
            dcc.Loading(
                id="loading-graphs",
                type="circle",
                children=html.Div([
                    dash_table.DataTable(
                        id='folder-table',
                        columns=[],
                        data=[],
                        page_action='none',
                        fixed_rows={'headers': True}
                    )
                ])
            )
        ]),
        footer()
    ])

    # コールバック登録（コールバック側で最新の config.json を参照）
    register_callbacks(dash_app)
    
    return dash_app
