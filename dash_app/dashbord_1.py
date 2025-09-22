from dash import Dash, dcc, html
from dash import dash_table
from dash_app.callback_1 import register_callbacks  # コールバックをインポート

def create_dash_app(flask_app):
    dash_app = Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dash/',
        assets_folder="assets"
    )

    # 保存先が設定されている場合は、レイアウトを作成（コールバックで最新設定を参照）
    dash_app.layout = html.Div([
        html.H2("収支の月別推移"),
        
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
                html.H3("収入分類"),
                dcc.Dropdown(id='income-category-dropdown', options=[], value='all', clearable=False,
                             style={'width': '200px', 'margin-bottom': '20px'})
            ], style={'margin-right': '20px'}),
            
            html.Div([
                html.H3("支出分類"),
                dcc.Dropdown(id='expense-category-dropdown', options=[], value='all', clearable=False,
                             style={'width': '200px', 'margin-bottom': '20px'})
            ], style={'margin-right': '20px'})
        ], style={'display': 'flex', 'align-items': 'center', 'gap': '20px'}),
        
        dcc.Graph(id='excel-graph'),
        html.Div([
            dcc.Graph(id='pie-in-chart', style={'width': '50%'}),
            dcc.Graph(id='pie-out-chart', style={'width': '50%'})
        ], style={'display': 'flex'}),
        
        html.Div([
            # 収入テーブル
            html.Div([
                dash_table.DataTable(
                    id='income-table', columns=[], data=[],
                    page_action='none', fixed_rows={'headers': True},
                    style_table={'height': '500px', 'overflowY': 'auto', 'overflowX': 'auto', 'width': '100%'},
                    style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': 'auto'},
                    style_header_conditional=[
                        {'if': {'column_id': c}, 'backgroundColor': 'cornflowerblue', 'color': 'white'}
                        for c in ['金額','期間_table','資産','分類','小分類','内容','メモ']
                    ]
                )
            ], style={'width': '50%', 'padding-right': '5px'}),

            # 支出テーブル
            html.Div([
                dash_table.DataTable(
                    id='expenses-table', columns=[], data=[],
                    page_action='none', fixed_rows={'headers': True},
                    style_table={'height': '500px', 'overflowY': 'auto', 'overflowX': 'auto', 'width': '100%'},
                    style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': 'auto'},
                    style_header_conditional=[
                        {'if': {'column_id': c}, 'backgroundColor': 'tomato', 'color': 'white'}
                        for c in ['金額','期間_table','資産','分類','小分類','内容','メモ']
                    ]
                )
            ], style={'width': '50%', 'padding-left': '5px'})
        ], style={'display': 'flex', 'gap': '0px'})
    ])

    # コールバック登録（コールバック側で最新の config.json を参照）
    register_callbacks(dash_app)
    
    return dash_app
