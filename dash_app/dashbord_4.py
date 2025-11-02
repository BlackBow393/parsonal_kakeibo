from dash import Dash, dcc, html
from dash_app.callback_4 import register_callbacks  # コールバックをインポート

def create_dash_app4(flask_app):
    dash_app = Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dash4/',
        assets_folder="assets"
    )

    # 保存先が設定されている場合は、レイアウトを作成（コールバックで最新設定を参照）
    dash_app.layout = html.Div([
        html.H2("収支の月別推移"),
        
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
                html.H3("支出分類"),
                dcc.Dropdown(id='expense-category-dropdown', options=[], value='all', clearable=False,
                             style={'width': '200px', 'margin-bottom': '20px'})
            ], style={'margin-right': '20px'}),
            
            html.Div([
                html.H3("支出小分類"),
                dcc.Dropdown(id='expense-subcategory-dropdown', options=[], value='all', clearable=False,
                             style={'width': '200px', 'margin-bottom': '20px'})
            ], style={'margin-right': '20px'})
        ], style={'display': 'flex', 'align-items': 'center', 'gap': '20px'}),
        
        dcc.Graph(id='expense-graph'),
        html.Div([
            dcc.Graph(id='expense-category-graph', style={'width': '70%'}),
            dcc.Graph(id='pie-ex-chart', style={'width': '30%'})
        ], style={'display': 'flex'}),
        html.Div([
            dcc.Graph(id='pie-ex-subchart', style={'width': '25%'}),
            dcc.Graph(id='pie-ex-subchart2', style={'width': '25%'}),
            dcc.Graph(id='pie-ex-subchart3', style={'width': '25%'}),
            dcc.Graph(id='pie-ex-subchart4', style={'width': '25%'})
        ], style={'display': 'flex'}),
        html.Div([
            dcc.Graph(id='pie-ex-subchart5', style={'width': '25%'}),
            dcc.Graph(id='pie-ex-subchart6', style={'width': '25%'}),
            dcc.Graph(id='pie-ex-subchart7', style={'width': '25%'}),
            dcc.Graph(id='pie-ex-subchart8', style={'width': '25%'})
        ], style={'display': 'flex'}),
        html.Div([
            dcc.Graph(id='pie-ex-subchart9', style={'width': '25%'}),
            dcc.Graph(id='pie-ex-subchart10', style={'width': '25%'}),
            dcc.Graph(id='pie-ex-subchart11', style={'width': '25%'}),
            dcc.Graph(id='pie-ex-subchart12', style={'width': '25%'})
        ], style={'display': 'flex'})
    ])

    # コールバック登録（コールバック側で最新の config.json を参照）
    register_callbacks(dash_app)
    
    return dash_app
