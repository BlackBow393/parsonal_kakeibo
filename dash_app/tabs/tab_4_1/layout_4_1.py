from dash import dcc, html

def layout_4_1():
    return html.Main([
        html.H2("支出分析ダッシュボード"),
        
        html.Div(className='dd-bord',children=[
            html.Div(className='dd-frame',children=[
                html.H3("年"),
                dcc.Dropdown(id='year-dropdown1', className='dropdown', options=[], value='all', clearable=False)
            ]),
            
            html.Div(className='dd-frame',children=[
                html.H3("月"),
                dcc.Dropdown(
                    id='month-dropdown1',
                    className='dropdown',
                    options=[{'label': "すべて", 'value': 'all'}] + [
                        {'label': f"{m}月", 'value': m} for m in range(1, 13)
                    ],
                    value='all',
                    clearable=False
                )
            ]),
            
            html.Div(className='dd-frame',children=[
                html.H3("支出分類"),
                dcc.Dropdown(id='expense-category-dropdown1', className='dropdown', options=[], value='all', clearable=False)
            ]),
            
            html.Div(className='dd-frame',children=[
                html.H3("支出小分類"),
                dcc.Dropdown(id='expense-subcategory-dropdown1', className='dropdown', options=[], value='all', clearable=False)
            ])
        ]),
        
        # Loadingを有効化するためにラップ
        dcc.Loading(
            id="loading-graphs1",
            type="circle",
            children=html.Div([
                dcc.Graph(id='expense-graph1'),
                html.Div([
                    dcc.Graph(id='expense-category-graph', style={'width': '70%'}),
                    dcc.Graph(id='pie-ex-chart', style={'width': '30%'})
                ], style={'display': 'flex'}),
                dcc.Graph(id='expense-frequency-graph')
            ])
        )
    ])
