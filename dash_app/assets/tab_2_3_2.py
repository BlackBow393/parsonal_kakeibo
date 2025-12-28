from dash import html, dcc

def layout():
    return html.Div([
        html.H3("貯蓄"),
        dcc.Graph(id="saving-graph")
    ])
