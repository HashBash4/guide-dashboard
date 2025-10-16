# Test file for loading an openelectricity test directly

import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import pandas as pd
from openelectricity_api import get_electricity_mix

app = dash.Dash(__name__)

def build_figure():
    print("Fetching latest mix data")
    mix = get_electricity_mix()   # expected: { "power_coal": {"timestamp": "...", "value": 123.4}, ... }

    if not mix:
        # Empty/None so return a placeholder figure
        empty_df = pd.DataFrame({ "fueltech": [], "value": [] })
        return px.bar(empty_df, x="value", y="fueltech", orientation="h", title="No data")

    # Flatten rows. Just fuel tech and amount
    rows = []
    # Get most recent timestamp we see
    latest_ts = None

    for name, payload in mix.items():
        # Name is eg "power_solar". Drop the "power_" from it and repalce _ with space
        label = name.replace("power_", "").replace("_", "")

        val = payload.get("value")
        ts = payload.get("timestamp")
        rows.append({"fueltech": label, "value": val})
        if ts and (latest_ts is None or ts > latest_ts):
            latest_ts = ts

    df = pd.DataFrame(rows)
    # Sort by ascending in value. Might change this…
    df.sort_values("value", ascending=True)

    title = "NEM power by fueltech"
    if latest_ts:
        title += f" - {latest_ts}"
    
    fig = px.bar(
        df,
        x="value",
        y="fueltech",
        orientation="h",
        labels={"value": "MW", "fueltech": "Fueltech"},
        title=title
    )

    return fig

app.layout = html.Div(
    children=[
        html.H1("Testing OpenElectricity API"),
        dcc.Graph(id="mix-graph"),
        # Auto-refresh every 60 seconds
        dcc.Interval(id="refresh", interval=60*1000, n_intervals=0)
    ]
)

@app.callback(
    Output("mix-graph", "figure"),
    Input("refresh", "n_intervals")
)
def update_graph(_):
    try:
        return build_figure()
    except Exception as e:
        # Error df and figure
        error_df = pd.DataFrame({ "fueltech": [], "value": [] })
        return px.bar(error_df, x="value", y="fueltech", orientation="h", title=f"Error: {e}")

if __name__ == "__main__":
    # debug=True enables hot reload + nice error overlay
    app.run(debug=True, host="0.0.0.0", port=8050)
