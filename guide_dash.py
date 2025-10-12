# this is the main file to run the app

###########################   IMPORTS   #########################################

import dash
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
from csiro_api import get_latest_intensity
from utils.rag_helpers import get_rag_color_label, rag_display




##############################   API REQUESTS   ###############################

# get_latest_intensity is imported from csiro_api.py)



############################   LAYOUT   #########################################

app = Dash(__name__)


app.layout = html.Div([
    # Header
    html.Div([
        html.H1("GUIDE Dashboard"),
        html.P("Grid Use Insights for Decarbonisation and Engagement")
    ], className="header"),

    # Device/Load Section
    html.Div([
        html.H4("Select Appliance and Duration")
    ], className="device-load"),

    # Main 2×3 Grid (79%)
    html.Div([
        html.Div([
        html.H5("Current Grid Carbon Intensity (NSW)"),
        dcc.Loading(  # spinner while fetching
        html.Div(id="rag_indicator", className="rag-box")
        )
    ], className="feature-box"),


        html.Div([html.H4("Weather Conditions")], className="feature-box"),
        html.Div([html.H4("Recommendation")], className="feature-box"),
        html.Div([html.H4("Current Grid Mix")], className="feature-box"),
        html.Div([html.H4("Carbon Intensity Trends")], className="feature-box"),
        html.Div([html.H4("User Impact Summary")], className="feature-box")
    ], className="grid-container"),

    # 🔁 Auto-refresh every 5 minutes
    dcc.Interval(id="refresh", interval=5*60*1000, n_intervals=0)
], className="main-container")




###################   CALLBACKS   #########################################

@app.callback(
    Output("rag_indicator", "children"),
    Input("refresh", "n_intervals")
)
def update_intensity(_):
    try:
        print("↻ Refresh triggered")
        ts, val = get_latest_intensity()
        #print("✅ API returned:", ts, val)
        color, label = get_rag_color_label(val)
        #print("🎨 Color/label:", color, label)
        return rag_display(val, ts, color, label)
    except Exception as e:
        print("⚠️ API error:", e)
        return html.P("Data unavailable — retrying in 5 min", style={"color": "gray"})




######################   Run the APP     ############################################################

if __name__ == "__main__":
    app.run(debug=True)



