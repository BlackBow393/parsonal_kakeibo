from dash import Input, Output, html
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
        #print("TAB CHANGED:", tab)
        #return html.H1(f"現在のタブ: {tab}")