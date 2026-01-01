from dash import Input, Output, State
from dash_app.tabs.tab_2_3_1.tab_2_3_1 import layout_2_3_1
from dash_app.tabs.tab_2_3_2.tab_2_3_2 import layout_2_3_2
from dash_app.tabs.tab_2_3_3.tab_2_3_3 import layout_2_3_3

def register_tab_callbacks(dash_app):
    
    @dash_app.callback(
        Output("asset-tab-content", "children"),
        Input("asset-tabs", "value")
    )
    def render_tab(tab):
        if tab == "all":
            return layout_2_3_1()
        elif tab == "saving":
            return layout_2_3_2()
        elif tab == "debt":
            return layout_2_3_3()
        else:
            return layout_2_3_1()
        
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
