from dash import html, dcc

def layout():
    return html.Div([
        html.H3("資産全体"),
        dcc.Graph(id="asset-total-graph"),
        dcc.Graph(id="asset-trend-graph")
    ])