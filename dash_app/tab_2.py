from dash import html, dcc

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
            html.A("設定", href="/setting")
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

def create_layout():
    return html.Div([

        # === 共通UI ===
        sidebar(),
        overlay(),
        menu_button(),
        
        # === ヘッダー ===
        html.Header(
            className="headder-asset",children=[
            html.H1("個人家計簿"),
            html.H2("資産分析"),
            html.Button("↻", id="refresh-btn", className="refresh-btn")
        ]),
        
        # === メイン ===
        dcc.Tabs(
            id="asset-tabs",
            value="all",
            children=[
                dcc.Tab(label="資産全体", value="all"),
                dcc.Tab(label="貯蓄", value="saving"),
                dcc.Tab(label="負債", value="debt"),
            ]
        ),

        html.Div(id="asset-tab-content"),
        footer()
    ])
