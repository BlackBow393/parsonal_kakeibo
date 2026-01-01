from dash import dcc, html

def layout_4_3():
    return html.Div([
        html.H2("交通/車の分析ダッシュボード"),
        
        html.Div([
            html.Div([
                html.H3("年"),
                dcc.Dropdown(id='year-dropdown3', options=[], value='all', clearable=False,
                             style={'width': '200px', 'margin-bottom': '20px'})
            ], style={'margin-right': '20px'}),
            
            html.Div([
                html.H3("月"),
                dcc.Dropdown(
                    id='month-dropdown3',
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
                dcc.Dropdown(id='expense-category-dropdown3', options=[], value='all', clearable=False,
                             style={'width': '200px', 'margin-bottom': '20px'})
            ], style={'margin-right': '20px'}),
            
            html.Div([
                html.H3("支出小分類"),
                dcc.Dropdown(id='expense-subcategory-dropdown3', options=[], value='all', clearable=False,
                             style={'width': '200px', 'margin-bottom': '20px'})
            ], style={'margin-right': '20px'})
        ], style={'display': 'flex', 'align-items': 'center', 'gap': '20px'}),
        
        # Loadingを有効化するためにラップ
        dcc.Loading(
            id="loading-graphs3",
            type="circle",
            children=html.Div([
                dcc.Graph(id='expense-subcategory-graph3'),
                dcc.Graph(id='refueling-graph1'),
                dcc.Graph(id='count-pareto-graph3')
            ])
        )
    ])