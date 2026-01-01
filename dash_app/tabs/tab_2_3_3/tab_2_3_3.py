from dash import html, dcc

def layout_2_3_3():
    return html.Div([
        html.H2("負債分析ダッシュボード"),
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
                        html.Div("総負債",style={
                            "fontSize": "24px",
                            "color": "#666",
                            "marginBottom": "8px"
                        }),
                        html.Div(id="total-debt-value",style={
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
                        html.Div("返済率",style={
                            "fontSize": "24px",
                            "color": "#666",
                            "marginBottom": "8px"
                        }),
                        html.Div(id="total-debt-rate",style={
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
                dcc.Graph(id='loan-graph', style={'width': '100%', 'height': '900px'}),
                dcc.Graph(id='loan-pie', style={'width': '100%', 'height': '900px'})
            ])
        )
    ])
