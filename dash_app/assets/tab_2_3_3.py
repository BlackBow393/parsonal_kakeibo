from dash import html, dcc

def layout():
    return html.Div([
        html.H3("負債"),
        dcc.Graph(id="debt-graph")
    ])
