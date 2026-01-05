from dash import Dash, dcc, html, dash_table

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
            html.A("設定", href="/setting"),
            html.A("テスト", href="/setting/")
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

def serve_layout(config):
    folder_path = config.get('folder_path','')
    
    return html.Div([
        
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
            
            html.Div(className='setting_area',children=[
                html.Button("📁", id="selectFolderBtn"),
                dcc.Input(
                    id="folderPath",
                    value=folder_path,
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