from dash import Dash, dcc, html
from dash import dash_table
from dash_app.callback_2_1 import register_callbacks  # コールバックをインポート

def create_dash_app2_1(flask_app):
    dash_app = Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dash2-1/',
        include_assets_files=False   # ★ Dash の assets を完全に無効化
    )

    # 保存先が設定されている場合は、レイアウトを作成（コールバックで最新設定を参照）
    dash_app.layout = html.Div([
        html.H2("資産の月別推移"),
        
        html.Div([
            html.Div([
                html.H3("年"),
                dcc.Dropdown(id='year-dropdown', options=[], value=None, clearable=False,
                             style={'width': '200px', 'margin-bottom': '20px'})
            ], style={'margin-right': '20px'}),
            
            html.Div([
                html.H3("月"),
                dcc.Dropdown(
                    id='month-dropdown',
                    options=[{'label': "すべて", 'value': 'all'}] + [
                        {'label': f"{m}月", 'value': m} for m in range(1, 13)
                    ],
                    value='all',
                    clearable=False,
                    style={'width': '200px', 'margin-bottom': '20px'}
                )
            ], style={'margin-right': '20px'}),
            
            html.Div([
                html.H3("資産分類"),
                dcc.Dropdown(id='assets-category-dropdown', options=[], value='all', clearable=False,
                             style={'width': '200px', 'margin-bottom': '20px'})
            ], style={'margin-right': '20px'})
        ], style={'display': 'flex', 'align-items': 'center', 'gap': '20px'}),
        
        # Loadingを有効化するためにラップ
        dcc.Loading(
            id="loading-graphs",
            type="circle",
            children=html.Div([
                dcc.Graph(id='savings-graph', style={'width': '100%', 'height': '450px'}),
                html.Div( className="kpi-card",children=[ html.Div("総資産", className="kpi-title"),html.Div(id="total-assets-value", className="kpi-value") ])
            ])
        )
    ])

    # コールバック登録（コールバック側で最新の config.json を参照）
    register_callbacks(dash_app)
    
    return dash_app
