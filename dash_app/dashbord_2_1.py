from dash import Dash, dcc, html
from dash import dash_table
from dash_app.callback_2_1 import register_callbacks  # コールバックをインポート

def create_dash_app2_1(flask_app):
    dash_app = Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dash2-1/',
        assets_folder="assets"
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
                html.Div(
                    children=[
                        html.Div("総資産",style={
                            "fontSize": "24px",
                            "color": "#666",
                            "marginBottom": "8px"
                        }),
                        html.Div(id="total-assets-value",style={
                            "fontSize": "48px",
                            "fontWeight": "bold"
                        })
                    ],
                    style={
                        "textAlign": "center",
                        "padding": "20px",
                        "borderRadius": "12px",
                        "background": "#b4b6b8",
                        "boxShadow": "0 2px 8px rgba(0,0,0,.1)",
                        "marginTop": "20px"
                    }
                ),
                html.Div(
                    children=[
                        html.Div("資産成長率",style={
                            "fontSize": "24px",
                            "color": "#666",
                            "marginBottom": "8px"
                        }),
                        html.Div(id="total-assets-rate",style={
                            "fontSize": "48px",
                            "fontWeight": "bold"
                        })
                    ],
                    style={
                        "textAlign": "center",
                        "padding": "20px",
                        "borderRadius": "12px",
                        "background": "#b4b6b8",
                        "boxShadow": "0 2px 8px rgba(0,0,0,.1)",
                        "marginTop": "20px"
                    }
                ),
                html.Div(
                    children=[
                        html.Div("対前年比 資産成長率",style={
                            "fontSize": "24px",
                            "color": "#666",
                            "marginBottom": "8px"
                        }),
                        html.Div(id="year-assets-rate",style={
                            "fontSize": "48px",
                            "fontWeight": "bold"
                        })
                    ],
                    style={
                        "textAlign": "center",
                        "padding": "20px",
                        "borderRadius": "12px",
                        "background": "#b4b6b8",
                        "boxShadow": "0 2px 8px rgba(0,0,0,.1)",
                        "marginTop": "20px"
                    }
                ),
                dcc.Graph(id='savings-graph', style={'width': '100%', 'height': '900px'})
            ])
        )
    ])

    # コールバック登録（コールバック側で最新の config.json を参照）
    register_callbacks(dash_app)
    
    return dash_app
