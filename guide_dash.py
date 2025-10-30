# this is the main file to run the app

###########################   IMPORTS   #########################################

import dash
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
from csiro_api import get_latest_intensity
from utils.rag_helpers import get_rag_color_label, rag_display
from openelectricity_api import get_electricity_mix
from datetime import datetime
import dash_bootstrap_components as dbc
import requests

##############################   API REQUESTS   ###############################

# get_latest_intensity is imported from csiro_api.py

############################   LAYOUT   #########################################

app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

def radio_buttons(_id, options, default):
    return html.Div(
        dbc.RadioItems(
            id=_id,
            options=[{"label": o.capitalize(), "value": o, "disabled": True} for o in options],
            value=default,
            inline=True,
            inputClassName="btn-check",
            inputCheckedClassName="btn-check",
            labelClassName="btn btn-outline-secondary me-0",
            labelCheckedClassName="btn btn-primary me-0",
            labelStyle={"width": "108px", "text-align": "center", "fontSize": "14px"}),
        className="btn-group", role="group")

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
        html.Div([
            html.Label("Run appliance:", style={"fontWeight": "bold", "marginBottom": "5px"}),
            dcc.Dropdown(
                id="device_dropdown",
                options=[
                    {"label": "Charge EV", "value": "Charge EV|7"},
                    {"label": "A/C", "value": "A/C|1.5"},
                    {"label": "Washing machine", "value": "Washing machine|0.8"},
                    {"label": "Clothes dryer", "value": "Clothes dryer|2"},
                    {"label": "Dish washer", "value": "Dish washer|1.2"},
                    {"label": "Oven", "value": "Oven|2"},
                    {"label": "Induction cooktop", "value": "Induction cooktop|2"},
                    {"label": "Hot water heat pump", "value": "Hot water heat pump|1"}
                ],
                value="Charge EV|7",
                clearable=False,
                style={"width": "200px"}
            )
        ], style={"display": "flex", "flexDirection": "column", "marginRight": "20px"}),
        
        html.Div([
            html.Label("Duration:", style={"fontWeight": "bold", "marginBottom": "5px"}),
            dcc.Dropdown(
                id="duration_dropdown",
                options=[
                    {"label": "0.5 hours", "value": 0.5},
                    {"label": "1 hour", "value": 1},
                    {"label": "2 hours", "value": 2},
                    {"label": "4 hours", "value": 4},
                    {"label": "6 hours", "value": 6},
                    {"label": "8 hours", "value": 8}
                ],
                value=1,
                clearable=False,
                style={"width": "150px"}
            )
        ], style={"display": "flex", "flexDirection": "column", "marginRight": "20px"}),
        
        html.Div([
            html.P(id="load_summary", style={
                "fontSize": "16px",
                "fontWeight": "500",
                "margin": "0",
                "padding": "10px 20px",
                "backgroundColor": "#e6f0fa",
                "borderRadius": "8px",
                "alignSelf": "center"
            })
        ], style={"display": "flex", "alignItems": "center"})
    ], className="device-load", style={"display": "flex", "alignItems": "flex-end", "justifyContent": "flex-start"}),

    # Main 2×3 Grid (79%)
    html.Div([

        # Grid intensity
        html.Div([
            #html.H5("Current Grid Carbon Intensity (NSW)"),
            dcc.Loading(  # spinner while fetching
                html.Div(id="rag_indicator", className="rag-box")
            )
        ], className="feature-box"),

        # Weather
        html.Div([html.H5("Current Weather Classification", style={"fontWeight": "bold", "fontFamily": "Arial"}),
                          html.Br(),
                          html.Div([radio_buttons("temperature", ["hot", "mild", "cold"], "hot")], style={"margin-bottom": "8px"}),
                          html.Div([radio_buttons("wind_speed", ["windy", "breezy", "calm"], "calm")], style={"margin-bottom": "8px"}),
                          html.Div([radio_buttons("cloudiness", ["clear", "partly cloudy", "overcast"], "partly cloudy")], style={"margin-bottom": "8px"}),
                          dcc.Interval(id="weather-refresh", interval=10*60*1000, n_intervals=0)
                  ], className="feature-box"),

        # Recommendation
        html.Div([
            html.H5("Recommendation", style={"fontWeight": "bold", "fontFamily": "Arial"}),
            html.Br(),
            html.P(id="recommendation_data", style={"font-size": "20px", "whiteSpace": "normal", "width": "90%", "textAlign": "center"})
        ], className="feature-box"),

        # Current grid mix
        html.Div([
            html.H5("Current Grid Mix", style={"fontWeight": "bold", "fontFamily": "Arial"}),
            html.Div(
                id="grid_mix_container",
                style={"width": "100%", "flex": "1", "display": "flex", "flexDirection": "column"},
                children=[html.P("Loading...", style={"textAlign": "center", "color": "gray", "marginTop": "50px"})]
            )
        ], className="feature-box"),

        # Carbon intensity trend
        html.Div([
            html.H5("Daily Carbon Intensity Trend", style={"fontWeight": "bold", "fontFamily": "Arial"}),
            html.P("This chart shows the typical hourly pattern of carbon intensity, "
                            "calculated from past days with weather conditions similar to today",
                            style={"font-size": "12px", "whiteSpace": "normal", "width": "60%", "textAlign": "center", "fontFamily": "Arial"}),
            dcc.Graph(id="line_graph", style={"height": "300px", "width": "90%"})
        ], className="feature-box"),

        # User impact summary
        html.Div([
            html.H5("User Impact Summary", style={"fontWeight": "bold", "fontFamily": "Arial"}),
            html.Br(),
            html.P(["By shifting your behaviour, you save CO", html.Sub("2"), " equal to: "],
                   style={"font-size": "18px", "whiteSpace": "normal", "width": "100%", "textAlign": "center", "fontFamily": "Arial"}),
            html.Br(),
            html.Div(id="carbon_savings", style={"font-size": "24px", "whiteSpace": "normal", "width": "60%", "textAlign": "center", "fontFamily": "Arial"}),
            html.Br(),
            html.Br(),
            html.P("THANK YOU!", style={"font-size": "18px", "whiteSpace": "normal", "width": "60%", "textAlign": "center", "fontFamily": "Arial"}),
            html.Img(src="/assets/earth_icon.png", style={"height": "60px", "display": "block", "marginLeft": "auto", "marginRight": "auto"})
         ], className="feature-box")

    ], className="grid-container"),

    # 🔁 Auto-refresh every 5 minutes
    dcc.Interval(id="refresh", interval=5*60*1000, n_intervals=0),
    dcc.Store(id="recommendation_data_store")
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

######################### Load Summary Callback ##########################

@app.callback(
    Output("load_summary", "children"),
    Input("device_dropdown", "value"),
    Input("duration_dropdown", "value")
)
def update_load_summary(device_value, duration):
    # Parse device value to extract name and kW
    device_name, kw_str = device_value.split("|")
    kw = float(kw_str)
    
    # Format the summary text
    return f"Representative load: {kw}kW, {duration}hrs"

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

        # --- Check if data is older than 4 hours ---
        try:
            ts_dt = pd.to_datetime(ts)
            hours_old = (datetime.now() - ts_dt).total_seconds() / 3600
            is_old = hours_old > 4
        except Exception:
            is_old = False

        # --- Build UI ---
        return html.Div([
            # Top title
            html.H5(
                "Current Carbon Intensity of Grid",
                style={
                    "textAlign": "center",
                    "marginBottom": "20px",
                    "marginTop": "5px",
                    "fontWeight": "bold",
                    "fontSize": "19px",
                    "fontFamily": "Arial"
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
                            "height": "120px",
                            "display": "block",
                            "margin": "0 auto"
                        }
                    )
                ], style={"flex": "1"})
            ], style={
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "marginBottom": "5px",
            }),

            # Label
            html.P(
                f"{label}",
                style={
                    "textAlign": "center",
                    "marginTop": "5px",
                    "marginBottom": "7px",
                    "fontWeight": "500"
                }
            ),

            # Timestamp + optional warning message
            html.Div([
                html.P(
                    f"Last updated: {ts}",
                    style={
                        "textAlign": "center",
                        "fontSize": "11px",
                        "color": "gray",
                        "marginTop": "0",
                        "marginBottom": "2px"
                    }
                ),
                html.Span(
                    "⚠️ Data older than 4h — values may not reflect current grid conditions."
                    if is_old else "",
                    style={
                        "display": "block",
                        "textAlign": "center",
                        "fontSize": "11px",
                        "color": "#d9534f" if is_old else "gray",
                        "fontWeight": "bold"
                    }
                )
            ])
        ], style={"margin": "0", "padding": "0"})

    except Exception as e:
        print("⚠️ API error:", e)
        return html.P(
            "Data unavailable — retrying in 5 min",
            style={"color": "gray"}
        )


######################### Daily Carbon Intensity Trend ##########################
df_carbon = pd.read_csv("historic_carbon_intensity_data.csv")
df_weather = pd.read_csv("historic_weather_data_sydney.csv")

df_carbon["datetime"] = (pd.to_datetime(df_carbon["datetime"].astype(str).str.strip(),
                        errors="coerce", utc=True).dt.tz_convert("Australia/Sydney").dt.tz_localize(None))
df_carbon["datetime_local"] = df_carbon["datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
df_weather["datetime_local"] = pd.to_datetime(df_weather["datetime_local"].astype(str).str.strip(),
                            errors="coerce", dayfirst=True).dt.strftime("%Y-%m-%d %H:%M:%S")

df_weather_carbon_merged = df_weather.merge(df_carbon[["datetime_local", "intensity_gCO2_per_kWh"]], on="datetime_local", how="left")
df_weather_carbon_merged["intensity_gCO2_per_kWh"] = df_weather_carbon_merged["intensity_gCO2_per_kWh"].fillna("NaN")
df_weather_carbon_merged = df_weather_carbon_merged[df_weather_carbon_merged["intensity_gCO2_per_kWh"] != "NaN"]

df_weather_carbon_merged["datetime_local"] = pd.to_datetime(df_weather_carbon_merged["datetime_local"], errors="coerce")
df_weather_carbon_merged["date"] = df_weather_carbon_merged["datetime_local"].dt.date
df_weather_carbon_merged["hour"] = df_weather_carbon_merged["datetime_local"].dt.hour

columns = ["temperature_2m_C", "wind_speed_10m_kmh", "cloud_cover_pct"]
for c in columns:
    q1, q2 = df_weather_carbon_merged[c].quantile([1/3, 2/3])
    df_weather_carbon_merged[f"{c}_category"] = pd.cut(df_weather_carbon_merged[c],
        bins=[-float("inf"), q1, q2, float("inf")], labels=["Low", "Medium", "High"])

df_weather_carbon_merged["temperature_2m_C_category"] = (df_weather_carbon_merged["temperature_2m_C_category"]
                                                         .replace({"Low": "cold", "Medium": "mild", "High": "hot"}))
df_weather_carbon_merged["wind_speed_10m_kmh_category"] = (df_weather_carbon_merged["wind_speed_10m_kmh_category"]
                                                           .replace({"Low": "calm", "Medium": "breezy", "High": "windy"}))
df_weather_carbon_merged["cloud_cover_pct_category"] = (df_weather_carbon_merged["cloud_cover_pct_category"]
                                                        .replace({"Low": "clear", "Medium": "partly cloudy", "High": "overcast"}))

# df_weather_carbon_merged.to_csv("historic_weather_carbon_data_merged.csv", index=False)

temp_q1, temp_q2 = df_weather_carbon_merged["temperature_2m_C"].quantile([1/3, 2/3]).tolist()
wind_q1, wind_q2 = df_weather_carbon_merged["wind_speed_10m_kmh"].quantile([1/3, 2/3]).tolist()
cloud_q1, cloud_q2 = df_weather_carbon_merged["cloud_cover_pct"].quantile([1/3, 2/3]).tolist()

def _classify(v, q1, q2, labels):
    if v <= q1: return labels[0]
    if v <= q2: return labels[1]
    return labels[2]

def _current_categories():
    r = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": -33.8688, "longitude": 151.2093,
            "current": ["temperature_2m", "wind_speed_10m", "cloud_cover"],
            "timezone": "Australia/Sydney"
        },
        timeout=30
    )
    r.raise_for_status()
    cur = r.json()["current"]
    t = cur["temperature_2m"]
    w = cur["wind_speed_10m"] * 3.6  # m/s -> km/h
    c = cur["cloud_cover"]
    temp_sel = _classify(t, temp_q1,  temp_q2,  ("cold", "mild", "hot"))
    wind_sel = _classify(w, wind_q1,  wind_q2,  ("calm", "breezy", "windy"))
    cloud_sel = _classify(c, cloud_q1, cloud_q2, ("clear", "partly cloudy", "overcast"))
    return temp_sel, wind_sel, cloud_sel

# automatically set radio button values based on live weather data
@app.callback(
    Output("temperature", "value"),
    Output("wind_speed", "value"),
    Output("cloudiness", "value"),
    Input("weather-refresh", "n_intervals"),
    prevent_initial_call=False
)
def set_radios_from_live(_):
    try:
        return _current_categories()
    except Exception:
        return "mild", "breezy", "partly cloudy"

@app.callback(
    Output("line_graph", "figure"),
    Input("temperature", "value"),
    Input("wind_speed", "value"),
    Input("cloudiness", "value"))
def update_line_graph(temp_selection, wind_selection, cloud_selection):
    df_weather_carbon_merged_filtered = df_weather_carbon_merged[
        (df_weather_carbon_merged["temperature_2m_C_category"] == temp_selection) &
        (df_weather_carbon_merged["wind_speed_10m_kmh_category"] == wind_selection) &
        (df_weather_carbon_merged["cloud_cover_pct_category"] == cloud_selection)].sort_values("hour")

    df_weather_carbon_merged_filtered_average = (
        df_weather_carbon_merged_filtered.groupby("hour", as_index=False)["intensity_gCO2_per_kWh"].mean()
        .rename(columns={"intensity_gCO2_per_kWh": "intensity_gCO2_per_kWh_average"}))

    if df_weather_carbon_merged_filtered_average.empty:
        fig_line_graph = px.line(title=f"No data for: {temp_selection}, {wind_selection}, {cloud_selection}")
    else:
        fig_line_graph = px.line(df_weather_carbon_merged_filtered_average,
        x="hour", y="intensity_gCO2_per_kWh_average", markers=True)

    fig_line_graph.update_layout(
        template="plotly_white",
        xaxis_title="Hour of Day",
        yaxis_title="Average Carbon Intensity (gCO₂/kWh)",
        xaxis_title_font=dict(size=10),
        yaxis_title_font=dict(size=10),
        hovermode="x unified",
        height=250,
        margin=dict(l=10, r=10, t=50, b=10))
    return fig_line_graph

######################### Grid mix ##########################

@app.callback(
    Output("grid_mix_container", "children"),
    Input("refresh", "n_intervals")
)
def update_grid_mix(_):
    try:
        # Fetch
        mix = get_electricity_mix() or {}   # expected: { "power_coal": {"timestamp": "...", "value": 123.4}, ... }
        
        DESIRED_FUELS = {"wind", "solar", "hydro", "coal", "gas"}
        rows = []
        timestamp = None
        
        for name, payload in mix.items():
            # "power_solar" -> "solar"
            label = name.removeprefix("power_")
            if label in DESIRED_FUELS:
                val = payload.get("value")
                if val is not None:
                    rows.append({"fueltech": label, "value": float(val)})
                    # Capture timestamp from first valid entry
                    if timestamp is None:
                        timestamp = payload.get("timestamp", "")
        
        # Format timestamp to be more user-friendly
        if timestamp:
            try:
                # Parse ISO format timestamp and format without timezone
                ts_dt = pd.to_datetime(timestamp)
                timestamp = ts_dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                # If parsing fails, keep original timestamp
                pass
        
        # Override point for no data
        #rows = []

        if not rows:
            # No data state - return text message instead of empty chart
            return html.Div([
                html.P(
                    "Unable to load data",
                    style={
                        "color": "gray",
                        "fontSize": "16px",
                        "textAlign": "center",
                        "marginTop": "50px"
                    }
                )
            ])

        # Build DF
        df = pd.DataFrame(rows)
        
        # Calculate total and percentages
        total_power = df["value"].sum()
        df["percentage"] = (df["value"] / total_power * 100).round(1)
        
        # Define custom order: renewables first, then fossil fuels
        fuel_order = ["solar", "wind", "hydro", "coal", "gas"]
        df["fueltech"] = pd.Categorical(df["fueltech"], categories=fuel_order, ordered=True)
        df = df.sort_values("fueltech").reset_index(drop=True)
        
        # Title case the labels
        df["fueltech_display"] = df["fueltech"].str.title()
        
        # Define colors: green shades for renewables, grays/browns for fossil fuels
        color_map = {
            "Solar": "#FDB462",    # Orange/yellow for solar
            "Wind": "#80B1D3",     # Light blue for wind
            "Hydro": "#8DD3C7",    # Teal for hydro
            "Coal": "#999999",     # Dark gray for coal
            "Gas": "#BEBADA"       # Purple-gray for gas
        }
        
        # Create text labels showing MW and percentage
        df["text_label"] = df.apply(
            lambda row: f"{row['percentage']:.1f}%",
            axis=1
        )
        
        fig = px.bar(
            df,
            x="value",
            y="fueltech_display",
            orientation="h",
            color="fueltech_display",
            color_discrete_map=color_map,
            text="text_label",
            title=""
        )
        
        # Update layout for cleaner appearance
        fig.update_traces(
            textposition="inside",
            textfont=dict(size=11, color="white", family="Arial"),
            insidetextanchor="end",  # Align text to the right (end) of the bar
            textangle=0  # Keep text horizontal
        )
        
        fig.update_layout(
            showlegend=False,
            xaxis_title="Megawatts (MW)",
            yaxis_title="",
            xaxis_title_font=dict(size=10),
            height=300,
            margin=dict(l=10, r=10, t=10, b=30),  # Extra bottom margin for timestamp
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis=dict(
                showgrid=True,
                gridcolor="lightgray",
                gridwidth=0.5
            ),
            yaxis=dict(
                tickfont=dict(size=12, family="Arial")
            ),
            autosize=True  # Allow the figure to resize dynamically
        )
        
        # Remove any fixed width constraints
        fig.update_xaxes(automargin=True)
        fig.update_yaxes(automargin=True)

        # Return a Div containing the graph and timestamp
        return html.Div([
            dcc.Graph(
                figure=fig,
                style={"width": "100%", "flex": "1"},
                config={"responsive": True}
            ),
            html.P(
                f"Last updated: {timestamp}" if timestamp else "Last updated: N/A",
                style={
                    "textAlign": "center",
                    "fontSize": "11px",
                    "color": "gray",
                    "marginTop": "5px",
                    "marginBottom": "0",
                    "flexShrink": "0"
                }
            )
        ], style={"width": "100%", "height": "100%", "display": "flex", "flexDirection": "column"})

    except Exception as e:
        print("⚠️ Grid mix API error:", e)
        return html.Div([
            html.P(
                "Unable to load data",
                style={
                    "color": "gray",
                    "fontSize": "16px",
                    "textAlign": "center",
                    "marginTop": "50px"
                }
            )
        ])

######################### Recommendation Data Callback ##########################

@app.callback(
    [
        Output("recommendation_data", "children"),
        Output("recommendation_data_store", "data")
    ],
    [
        Input("device_dropdown", "value"),
        Input("duration_dropdown", "value"),
        Input("temperature", "value"),
        Input("wind_speed", "value"),
        Input("cloudiness", "value"),
        Input("rag_indicator", "children")  # refresh trigger
    ],
)
def update_recommendation_data(device_value, duration, temp_selection, wind_selection, cloud_selection, _):
    """
    Updated recommendation logic (v2):
    1️⃣ If current intensity <= 618.1 → low intensity: no shift needed.
    2️⃣ Else, check forecast for the same day and *only future hours*:
        - if any hour <= 618.1 OR <= 0.7 * current_intensity → suggest load shift.
    3️⃣ Otherwise, recommend starting now or waiting until tomorrow.
    """

    try:
        # --- Get current time and intensity
        ts, current_intensity = get_latest_intensity()

        # testing (hardcoded)
        #ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #current_intensity = 10015  # 👈 use a realistic value, e.g. 615 (not 6150)

        now = datetime.now()
        current_hour = now.hour

        # --- CASE 1: low carbon intensity (green)
        if current_intensity <= 618.1:
            return (
                html.Div([
                    html.P("Carbon Intensity Low – No load shift needed.",
                           style={"fontSize": "18px", "fontWeight": "500"}),
                    html.Img(src="/assets/tick.png",
                             style={"height": "100px", "marginTop": "10px"})
                ], style={"textAlign": "center"}),
                {"shift_needed": False, "recommended_hour": None}
            )

        # --- CASE 2: intensity above threshold → check daily forecast
        df_filtered = df_weather_carbon_merged[
            (df_weather_carbon_merged["temperature_2m_C_category"] == temp_selection) &
            (df_weather_carbon_merged["wind_speed_10m_kmh_category"] == wind_selection) &
            (df_weather_carbon_merged["cloud_cover_pct_category"] == cloud_selection)
        ].sort_values("hour")

        hourly_avg = (
            df_filtered.groupby("hour", as_index=False)["intensity_gCO2_per_kWh"].mean()
        )

        if hourly_avg.empty:
            return (
                html.Div([
                    html.P("⚠️ No forecast data available for today.",
                           style={"fontSize": "16px"})
                ], style={"textAlign": "center"}),
                {"shift_needed": None, "recommended_hour": None}
            )

        # Filter only *future* hours (current_hour + 1 and later)
        hourly_future = hourly_avg[hourly_avg["hour"] > current_hour]

        threshold_abs = 618.1
        threshold_rel = 0.7 * current_intensity

        candidate_hours = hourly_future[
            (hourly_future["intensity_gCO2_per_kWh"] <= threshold_abs) |
            (hourly_future["intensity_gCO2_per_kWh"] <= threshold_rel)
        ]

        if not candidate_hours.empty:
            best_hour = int(candidate_hours.iloc[0]["hour"])
            return (
                html.Div([
                    html.P(f"Lower Carbon Intensity expected at {best_hour:02d}:00. "
                           f"If possible, shift your load to that time.",
                           style={"fontSize": "18px", "fontWeight": "500"}),
                    html.Img(src="/assets/shift.png",
                             style={"height": "100px", "marginTop": "10px"})
                ], style={"textAlign": "center"}),
                {"shift_needed": True, "recommended_hour": best_hour}
            )

        # --- CASE 3: no suitable lower intensity hour found
        return (
            html.Div([
                html.P("No significant drop in carbon intensity expected today.",
                       style={"fontSize": "18px", "fontWeight": "500"}),
                html.P("Start your appliance now or, if not time sensitive, wait until tomorrow.",
                       style={"fontSize": "16px"}),
                html.Img(src="/assets/line.png",
                         style={"height": "100px", "marginTop": "10px"})
            ], style={"textAlign": "center"}),
            {"shift_needed": False, "recommended_hour": None}
        )

    except Exception as e:
        print("⚠️ Recommendation error:", e)
        return "Recommendation data unavailable — please retry shortly.", {"shift_needed": None, "recommended_hour": None}

#################################### User Impact Summary ##########################
@app.callback(
    Output("carbon_savings", "children"),
    Input("recommendation_data_store", "data"),
    Input("device_dropdown", "value"),
    Input("duration_dropdown", "value"),
    Input("temperature", "value"),
    Input("wind_speed", "value"),
    Input("cloudiness", "value")
)
def update_carbon_savings(recommendation_data, device_value, duration, temp_selection, wind_selection, cloud_selection):
    if recommendation_data is None:
        raise PreventUpdate

    shift_needed = recommendation_data.get("shift_needed")
    recommended_hour = recommendation_data.get("recommended_hour")

    if not shift_needed:
        return "No load shift detected - no additional savings."

    device_name, kwh_str = device_value.split("|")
    kwh = float(kwh_str)
    ts, current_intensity = get_latest_intensity()

    df_filtered = df_weather_carbon_merged[
        (df_weather_carbon_merged["temperature_2m_C_category"] == temp_selection) &
        (df_weather_carbon_merged["wind_speed_10m_kmh_category"] == wind_selection) &
        (df_weather_carbon_merged["cloud_cover_pct_category"] == cloud_selection)
        ].sort_values("hour")

    hourly_avg = (df_filtered.groupby("hour", as_index=False)["intensity_gCO2_per_kWh"].mean())

    recommended_intensity = hourly_avg.loc[hourly_avg["hour"] == recommended_hour, "intensity_gCO2_per_kWh"].iloc[0]

    phone_charges = (current_intensity - recommended_intensity) * kwh * duration / 3.25
    car_trips_1km = (current_intensity - recommended_intensity) * kwh * duration / 193.7

    return [
        html.Div([
            html.Img(src="/assets/cell-phone.png", style={"height": "30px", "marginRight": "30px"}),
            f"{round(phone_charges)} phone charges"
        ], style={"display": "flex", "alignItems": "center"}),

        html.Div([
            html.Img(src="/assets/car.png", style={"height": "40px", "marginRight": "20px"}),
            f"{round(car_trips_1km)} km of car travel"
        ], style={"display": "flex", "alignItems": "center"})
    ]

######################   Run the APP     ############################################################

if __name__ == "__main__":
    app.run(debug=True)
