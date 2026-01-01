from dash import html, dcc

def layout_2_1():
    return html.Div([
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
                dcc.Graph(id='cash-graph', style={'width': '100%', 'height': '450px'}),
                dcc.Graph(id='cashles-graph', style={'width': '100%', 'height': '450px'}),
                dcc.Graph(id='bank-graph', style={'width': '100%', 'height': '450px'}),
                dcc.Graph(id='card-graph', style={'width': '100%', 'height': '450px'}),
                dcc.Graph(id='loan-graph', style={'width': '100%', 'height': '450px'})
            ])
        )
    ])