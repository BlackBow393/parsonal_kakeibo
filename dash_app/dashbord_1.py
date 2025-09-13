import os
from dash import Dash, dcc, html
from dash import dash_table
from dash_app.callback_1 import register_callbacks  # ← コールバックをインポート

def create_dash_app(flask_app):
    dash_app = Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dash/',
        assets_folder="assets"
    )

    DATA_DIR = "data"
    excel_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.xlsx')]

    dash_app.layout = html.Div([
        html.H2("収支の月別推移"),
        
        html.Div([
            html.Div([
                html.H3("年"),
                # ▼ 年選択プルダウンを追加
                dcc.Dropdown(
                    id='year-dropdown',
                    options=[],  # 後でコールバックで埋める
                    value=None,
                    clearable=False,
                    style={'width': '200px', 'margin-bottom': '20px'}
                )
            ],style={'margin-right': '20px'}),
            
            html.Div([
                html.H3("月"),
                # ▼ 月プルダウン
                dcc.Dropdown(
                    id='month-dropdown',
                    options=[{'label': "すべて", 'value': 'all'}] + [
                        {'label': f"{m}月", 'value': m} for m in range(1, 13)
                    ],
                    value='all',  # デフォルトは「すべて」
                    clearable=False,
                    style={'width': '200px', 'margin-bottom': '20px'}
                )
            ],style={'margin-right': '20px'}),
            
            html.Div([
                html.H3("収入分類"),
                # ▼ 収入分類プルダウン
                dcc.Dropdown(
                    id='income-category-dropdown',
                    options=[],  # データから動的に作る
                    value='all',
                    clearable=False,
                    style={'width': '200px', 'margin-bottom': '20px'}
                )
            ],style={'margin-right': '20px'}),
            
            html.Div([
                html.H3("支出分類"),
                # ▼ 支出分類プルダウン
                dcc.Dropdown(
                    id='expense-category-dropdown',
                    options=[],  # データから動的に作る
                    value='all',
                    clearable=False,
                    style={'width': '200px', 'margin-bottom': '20px'}
                )
            ],style={'margin-right': '20px'})
        ], style={'display': 'flex', 'align-items': 'center', 'gap': '20px'}),
        
        dcc.Graph(id='excel-graph'), # 棒グラフ
        html.Div([
            dcc.Graph(id='pie-in-chart', style={'width': '50%'}),  # 収入の円グラフ
            dcc.Graph(id='pie-out-chart', style={'width': '50%'})  # 支出の円グラフ
        ], style={'display': 'flex'}),
        html.Div([
            # 収入テーブル
            html.Div([
                dash_table.DataTable(
                    id='income-table',
                    columns=[],
                    data=[],
                    page_action='none',
                    fixed_rows={'headers': True},  # ← ヘッダー固定
                    style_table={
                        'height': '500px',
                        'overflowY': 'auto',
                        'overflowX': 'auto',
                        'width': '100%'   # 子Divに合わせて幅100%
                    },
                    style_cell={
                        'textAlign': 'left',
                        'minWidth': '100px',
                        'width': 'auto'
                    },
                    style_header_conditional=[
                        {'if': {'column_id': '金額'}, 'backgroundColor': 'cornflowerblue', 'color': 'white'},
                        {'if': {'column_id': '期間_table'}, 'backgroundColor': 'cornflowerblue', 'color': 'white'},
                        {'if': {'column_id': '資産'}, 'backgroundColor': 'cornflowerblue', 'color': 'white'},
                        {'if': {'column_id': '分類'}, 'backgroundColor': 'cornflowerblue', 'color': 'white'},
                        {'if': {'column_id': '小分類'}, 'backgroundColor': 'cornflowerblue', 'color': 'white'},
                        {'if': {'column_id': '内容'}, 'backgroundColor': 'cornflowerblue', 'color': 'white'},
                        {'if': {'column_id': 'メモ'}, 'backgroundColor': 'cornflowerblue', 'color': 'white'}
                    ]
                )
            ], style={'width': '50%', 'padding-right': '5px'}),  # 画面半分

            # 支出テーブル
            html.Div([
                dash_table.DataTable(
                    id='expenses-table',
                    columns=[],
                    data=[],
                    page_action='none',
                    fixed_rows={'headers': True},  # ← ヘッダー固定
                    style_table={
                        'height': '500px',
                        'overflowY': 'auto',
                        'overflowX': 'auto',
                        'width': '100%'   # 子Divに合わせて幅100%
                    },
                    style_cell={
                        'textAlign': 'left',
                        'minWidth': '100px',
                        'width': 'auto'
                    },
                    style_header_conditional=[
                        {'if': {'column_id': '金額'}, 'backgroundColor': 'tomato', 'color': 'white'},
                        {'if': {'column_id': '期間_table'}, 'backgroundColor': 'tomato', 'color': 'white'},
                        {'if': {'column_id': '資産'}, 'backgroundColor': 'tomato', 'color': 'white'},
                        {'if': {'column_id': '分類'}, 'backgroundColor': 'tomato', 'color': 'white'},
                        {'if': {'column_id': '小分類'}, 'backgroundColor': 'tomato', 'color': 'white'},
                        {'if': {'column_id': '内容'}, 'backgroundColor': 'tomato', 'color': 'white'},
                        {'if': {'column_id': 'メモ'}, 'backgroundColor': 'tomato', 'color': 'white'}
                    ]
                )
            ], style={'width': '50%', 'padding-left': '5px'})   # 画面半分
        ], style={'display': 'flex', 'gap': '0px'})  # 横並び
    ])
    
    register_callbacks(dash_app, excel_files, DATA_DIR)
    
    return dash_app
