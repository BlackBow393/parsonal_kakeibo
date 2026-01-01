from dash import html, dcc

def layout_2_2():
    return html.Main([
        html.H2("貯蓄分析ダッシュボード"),
        
        html.Div(className='dd-bord',children=[
            html.Div(className='dd-frame',children=[
                html.H3("年"),
                dcc.Dropdown(id='year-dropdown2', className='dropdown', options=[], value=None, clearable=False)
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
                html.H3("資産分類"),
                dcc.Dropdown(id='assets-category-dropdown2', className='dropdown', options=[], value='all', clearable=False)
            ])
        ]),
        
        # Loadingを有効化するためにラップ
        dcc.Loading(
            id="loading-graphs2",
            type="circle",
            children=html.Div([
                html.Div(
                    className='card1',
                    children=[
                        html.Div("総資産",className='card-title'),
                        html.Div(id="total-assets-value",className='card-font')
                    ]
                ),
                html.Div(
                    className='card1',
                    children=[
                        html.Div("資産成長率",className='card-title'),
                        html.Div(id="total-assets-rate",className='card-font')
                    ]
                ),
                html.Div(
                    className='card1',
                    children=[
                        html.Div("対前年比 資産成長率",className='card-title'),
                        html.Div(id="year-assets-rate",className='card-font')
                    ]
                ),
                dcc.Graph(id='savings-graph', style={'width': '100%', 'height': '900px'})
            ])
        )
    ])
