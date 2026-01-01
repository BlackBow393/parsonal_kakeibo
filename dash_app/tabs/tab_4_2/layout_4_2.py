from dash import dcc, html

def layout_4_2():
    return html.Main([
        html.H2("食費と生活用品の分析ダッシュボード"),
        
        html.Div(className='dd-bord',children=[
            html.Div(className='dd-frame',children=[
                html.H3("年"),
                dcc.Dropdown(id='year-dropdown2', className='dropdown', options=[], value='all', clearable=False)
            ]),
            
            html.Div(className='dd-frame',children=[
                html.H3("月"),
                dcc.Dropdown(
                    id='month-dropdown2',
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
                dcc.Dropdown(id='expense-category-dropdown2', className='dropdown', options=[], value='all', clearable=False)
            ]),
            
            html.Div(className='dd-frame',children=[
                html.H3("支出小分類"),
                dcc.Dropdown(id='expense-subcategory-dropdown2', className='dropdown', options=[], value='all', clearable=False)
            ])
        ]),
        
        # Loadingを有効化するためにラップ
        dcc.Loading(
            id="loading-graphs2",
            type="circle",
            children=html.Div([
                dcc.Graph(id='expense-graph2'),
                dcc.Graph(id='expense-subcategory-graph2'),
                html.Div([
                    dcc.Graph(id='expense-pareto-graph', style={'width': '70%'}),
                    dcc.Graph(id='count-pareto-graph2', style={'width': '70%'})
                ], style={'display': 'flex'})
            ])
        )
    ])