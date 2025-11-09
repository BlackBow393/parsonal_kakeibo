from dash import Dash, dcc, html
from dash import dash_table
from dash_app.callback_3 import register_callbacks  # コールバックをインポート

def create_dash_app3(flask_app):
    dash_app = Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dash3/',
        assets_folder="assets"
    )

    # 保存先が設定されている場合は、レイアウトを作成（コールバックで最新設定を参照）
    dash_app.layout = html.Div([
        html.H2("収入分析ダッシュボード"),
        
        html.Div([
            html.Div([
                html.H3("年"),
                dcc.Dropdown(id='year-dropdown', options=[], value='all', clearable=False,
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
                html.H3("収入分類"),
                dcc.Dropdown(id='income-category-dropdown', options=[], value='all', clearable=False,
                             style={'width': '200px', 'margin-bottom': '20px'})
            ], style={'margin-right': '20px'}),
            
            html.Div([
                html.H3("収入小分類"),
                dcc.Dropdown(id='income-subcategory-dropdown', options=[], value='all', clearable=False,
                             style={'width': '200px', 'margin-bottom': '20px'})
            ], style={'margin-right': '20px'})
        ], style={'display': 'flex', 'align-items': 'center', 'gap': '20px'}),
        
        dcc.Graph(id='year-graph'),
        dcc.Graph(id='line-graph'),
        html.Div([
            dcc.Graph(id='pie-in-chart', style={'width': '50%'}),
            dcc.Graph(id='pie-in-subchart', style={'width': '50%'})
            ], style={'display': 'flex'}),
        dcc.Graph(id='income-graph')
    ])

    # コールバック登録（コールバック側で最新の config.json を参照）
    register_callbacks(dash_app)
    
    return dash_app
