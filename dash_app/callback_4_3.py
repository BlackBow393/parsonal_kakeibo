from dash import Input, Output, State
from dash_app.tabs.tab_4_1.layout_4_1 import layout_4_1
from dash_app.tabs.tab_4_2.layout_4_2 import layout_4_2
from dash_app.tabs.tab_4_3.layout_4_3 import layout_4_3

def register_tab_callbacks(dash_app):
    
    @dash_app.callback(
        Output("expense-tab-content", "children"),
        Input("expense-tabs", "value")
    )
    def render_tab(tab):
        if tab == "all":
            return layout_4_1()
        elif tab == "lifecost":
            return layout_4_2()
        elif tab == "car":
            return layout_4_3()
        else:
            return layout_4_1()
        
    @dash_app.callback(
        Output("sidebar", "className"),
        Output("overlay", "className"),
        Input("menu-toggle", "n_clicks"),
        Input("overlay", "n_clicks"),
        State("sidebar", "className"),
        prevent_initial_call=True
    )
    def toggle_sidebar(menu_clicks, overlay_clicks, current_class):
        if current_class and "active" in current_class:
            return "sidebar", "overlay"
        else:
            return "sidebar active", "overlay active"
