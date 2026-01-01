from dash import html, dcc

def layout_2_1():
    return html.Main([
        html.H2("資産の月別推移"),
        
        html.Div(className='dd-bord',children=[
            html.Div(className='dd-frame',children=[
                html.H3("年"),
                dcc.Dropdown(id='year-dropdown', className='dropdown', options=[], value=None, clearable=False)
            ]),
            
            html.Div(className='dd-frame',children=[
                html.H3("月"),
                dcc.Dropdown(
                    id='month-dropdown',
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
                dcc.Dropdown(id='assets-category-dropdown', className='dropdown', options=[], value='all', clearable=False)
            ])
        ]),
        
        # Loadingを有効化するためにラップ
        dcc.Loading(
            id="loading-graphs",
            type="circle",
            children=html.Div([
                dcc.Graph(id='cash-graph', className='asset-graph-1', style={'width': '100%', 'height': '450px'}),
                dcc.Graph(id='cashles-graph', style={'width': '100%', 'height': '450px'}),
                dcc.Graph(id='bank-graph', style={'width': '100%', 'height': '450px'}),
                dcc.Graph(id='card-graph', style={'width': '100%', 'height': '450px'}),
                dcc.Graph(id='loan-graph', style={'width': '100%', 'height': '450px'})
            ])
        )
    ])