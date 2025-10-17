# this is the main file to run the app

###########################   IMPORTS   #########################################

import dash
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
from csiro_api import get_latest_intensity
from utils.rag_helpers import get_rag_color_label, rag_display
from datetime import datetime





##############################   API REQUESTS   ###############################

# get_latest_intensity is imported from csiro_api.py)



############################   LAYOUT   #########################################

app = Dash(__name__, suppress_callback_exceptions=True)


app.layout = html.Div([
     # ===== HEADER BAR =====
    html.Div([
        # Left section – title + subtitle
        html.Div([
            html.H1("GUIDE Dashboard",
                    style={"margin": "0", "fontWeight": "bold"}),
            html.P("Grid Use Insights for Decarbonisation and Engagement",
                   style={"margin": "0", "fontWeight": "400", "fontSize": "15px"})
        ], style={"flex": "2"}),

        # Middle section – state and flag
        html.Div([
            html.P([
                "State: ",
                html.Span("NSW", style={"fontWeight": "bold", "marginRight": "6px"}),
                html.Img(
                    src="/assets/flag_nsw.png",  # <-- put flag in /assets/
                    style={"height": "18px", "verticalAlign": "middle"}
                )
            ], style={"margin": "0", "fontSize": "15px"})
        ], style={"flex": "1", "textAlign": "center"}),

        # Right section – date and live time
        html.Div([
            html.P(id="current_date", style={
                "margin": "0",
                "fontSize": "14px",
                "textAlign": "right"
            }),
            html.H3(id="current_time", style={
                "margin": "0",
                "fontWeight": "bold",
                "textAlign": "right"
            })
        ], style={"flex": "1"})
    ], className="header-bar"),


    # 🔁 Add this interval for the live clock ⏱️
    dcc.Interval(id="clock", interval=1000, n_intervals=0),


    # Device/Load Section
    html.Div([
        html.H4("Select Appliance and Duration")
    ], className="device-load"),

    # Main 2×3 Grid (79%)
    html.Div([
        html.Div([
        #html.H5("Current Grid Carbon Intensity (NSW)"),
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



############################################################################
###################   CALLBACKS   #########################################
#############################################################################

#################### Callback for Date and Time in Header section #####################

@app.callback(
    [Output("current_date", "children"),
    Output("current_time", "children")],
    Input("clock", "n_intervals")
)
def update_clock(_):
    now = datetime.now()
    date_str = now.strftime("%d/%m/%Y")
    time_str = now.strftime("%H:%M:%S")
    return date_str, time_str

######################### RAG Indicator and current Carbon Intensity ##########################
@app.callback(
    Output("rag_indicator", "children"),
    Input("refresh", "n_intervals")
)
def update_intensity(_):
    try:
        ts, val = get_latest_intensity()
        color, label = get_rag_color_label(val)

        image_map = {
            "green": "green.png",
            "amber": "amber.png",
            "red": "red.png"
        }
        if color not in image_map:
            raise ValueError(f"Unexpected color label: {color}")

        image_src = f"/assets/{image_map[color]}"

        return html.Div([
            # Top title
            html.H5(
                "Current Carbon Intensity of Grid",
                style={
                    "textAlign": "center",
                    "marginBottom": "20px",    # ↓ tighter
                    "marginTop": "5px",        # ↓ tighter
                    "fontWeight": "bold",
                    "fontSize": "19px"
                }
            ),

            # Main value + image row
            html.Div([
                html.Div([
                    html.P(
                        f"{val:.1f}",
                        style={
                            "fontSize": "65px",
                            "fontWeight": "bold",
                            "margin": "0",
                            "textAlign": "right",
                            "color": "black",
                            "lineHeight": "1.0"
                        }
                    ),
                    html.P(
                        "gCO₂/kWh",
                        style={
                            "fontSize": "18px",
                            "color": "gray",
                            "margin": "0",
                            "textAlign": "right",
                            "lineHeight": "1.0"
                        }
                    )
                ], style={"flex": "1", "marginRight": "10px"}),

                html.Div([
                    html.Img(
                        src=image_src,
                        style={
                            "height": "120px",     # ↓ slightly reduced height
                            "display": "block",
                            "margin": "0 auto"
                        }
                    )
                ], style={"flex": "1"})
            ], style={
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "marginBottom": "5px",        # ↓ reduced bottom gap
            }),

            # Label + timestamp
            html.P(
                f"{label}",
                style={
                    "textAlign": "center",
                    "marginTop": "5px",         # ↓ tighter
                    "marginBottom": "7px",
                    "fontWeight": "500"
                }
            ),
            html.P(
                f"Last updated: {ts}",
                style={
                    "textAlign": "center",
                    "fontSize": "11px",
                    "color": "gray",
                    "marginTop": "0"
                }
            )
        ], style={"margin": "0", "padding": "0"})   # ↓ ensures box doesn’t stretch

    except Exception as e:
        print("⚠️ API error:", e)
        return html.P(
            "Data unavailable — retrying in 5 min",
            style={"color": "gray"}
        )




######################   Run the APP     ############################################################

if __name__ == "__main__":
    app.run(debug=True)



