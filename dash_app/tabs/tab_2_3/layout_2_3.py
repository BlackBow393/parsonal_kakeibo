from dash import html, dcc

def layout_2_3():
    return html.Main([
        html.H2("負債分析ダッシュボード"),
        html.Div(className='dd-bord',children=[
            html.Div(className='dd-frame',children=[
                html.H3("年"),
                dcc.Dropdown(id='year-dropdown3', className='dropdown', options=[], value=None, clearable=False)
            ]),
            
            html.Div(className='dd-frame',children=[
                html.H3("月"),
                dcc.Dropdown(
                    id='month-dropdown3',
                    className='dropdown',
                    options=[{'label': "すべて", 'value': 'all'}] + [
                        {'label': f"{m}月", 'value': m} for m in range(1, 13)
                    ],
                    value='all',
                    clearable=False
                )
            ]),
            
            html.Div(className='dd-frame',children=[
                html.H3("資産分類"),
                dcc.Dropdown(id='assets-category-dropdown3', className='dropdown', options=[], value='all', clearable=False)
            ])
        ]),
        
        # Loadingを有効化するためにラップ
        dcc.Loading(
            id="loading-graphs3",
            type="circle",
            children=html.Div([
                html.Div(
                    className='card1',
                    children=[
                        html.Div("総負債",className='card-title'),
                        html.Div(id="total-debt-value",className='card-font')
                    ]
                ),
                html.Div(
                    className='card1',
                    children=[
                        html.Div("返済率",className='card-title'),
                        html.Div(id="total-debt-rate",className='card-font')
                    ]
                ),
                dcc.Graph(id='loan-graph3', style={'width': '100%', 'height': '600px'}),
                dcc.Graph(id='loan-pie', style={'width': '100%', 'height': '600px'})
            ])
        )
    ])
