from dash import html, dcc

def create_layout():
    return html.Div([

        dcc.Tabs(
            id="asset-tabs",
            value="all",
            children=[
                dcc.Tab(label="資産全体", value="all"),
                dcc.Tab(label="貯蓄", value="saving"),
                dcc.Tab(label="負債", value="debt"),
            ]
        ),

        html.Div(id="asset-tab-content")
    ])
