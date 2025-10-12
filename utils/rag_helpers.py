from dash import html

GREEN_MAX = 618.1
AMBER_MAX = 752.6

def get_rag_color_label(value):
    if value <= GREEN_MAX:
        return "green", "Low (clean grid)"
    elif value <= AMBER_MAX:
        return "amber", "Medium"
    else:
        return "red", "High (dirty grid)"

def rag_display(value, timestamp, color, label):
    return html.Div([
        html.Div(className=f"rag-dot {color}"),
        html.H3(f"{value:.1f} gCO₂/kWh"),
        html.P(label),
        html.Small(f"Last updated {timestamp.strftime('%H:%M')}")
    ], className="rag-content")
