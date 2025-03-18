import dash
from dash import dcc, html, Input, Output, State
import dash_ace  # pip install dash-ace
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import re
from datetime import datetime

# Default timeline definition (timestamps MUST be in square brackets)
default_timeline = """
[19:58:12.174] <<Hello>> Hello, World!
[20:58:12.174] <<World>> World, Hello!
"""

def parse_events(raw):
    pattern = re.compile(r'^\[(\d{2}:\d{2}:\d{2}(?:\.\d+)?)\]\s+<<([^>]+)>>\s+(.*)$')
    events = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        match = pattern.match(line)
        if match:
            timestamp_str, obj, msg = match.groups()
            events.append({"timestamp": timestamp_str, "object": obj, "message": msg})
    return events

def create_dataframe(events):
    rows = []
    for event in events:
        try:
            t = datetime.strptime(event['timestamp'], "%H:%M:%S.%f")
        except ValueError:
            t = datetime.strptime(event['timestamp'], "%H:%M:%S")
        rows.append({"timestamp": t, "object": event['object'], "message": event['message']})
    return pd.DataFrame(rows)

def create_figure(df, clicked_time=None):
    unique_objects = sorted(df['object'].unique())
    object_to_y = {obj: i+1 for i, obj in enumerate(unique_objects)}
    colors = px.colors.qualitative.Plotly
    object_to_color = {obj: colors[i % len(colors)] for i, obj in enumerate(unique_objects)}
    df["y"] = df["object"].map(object_to_y)
    marker_colors = [object_to_color[obj] for obj in df["object"]]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["y"],
        mode="markers",
        marker=dict(size=12, symbol="circle", color=marker_colors, line=dict(width=1, color="white")),
        text=[f"{row['timestamp'].strftime('%H:%M:%S.%f')[:-3]} - <<{row['object']}>> {row['message']}" for _, row in df.iterrows()],
        customdata=[{"timestamp": row["timestamp"].isoformat(), "object": row["object"], "message": row["message"]} for _, row in df.iterrows()],
        hovertemplate="%{text}<extra></extra>"
    ))
    if clicked_time is not None:
        fig.add_shape(
            type="line",
            x0=clicked_time,
            y0=0.8,
            x1=clicked_time,
            y1=len(unique_objects)+0.2,
            line=dict(color="red", dash="dash", width=2)
        )
    fig.update_yaxes(
        tickmode="array",
        tickvals=list(object_to_y.values()),
        ticktext=list(object_to_y.keys()),
        gridcolor="lightgray"
    )
    fig.update_xaxes( gridcolor="lightgray",tickformat="%H:%M:%S")
    fig.update_layout(
        clickmode='event+select',
        height=600,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="#343432",
        plot_bgcolor="#343432",
        font = dict(family="Monospace",color="white",size=14),
        uirevision="constant"
    )
    return fig

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    # Header section
    # Main content: Graph and event details
    html.Div([
        dcc.Graph(id="timeline", config={'displayModeBar': False}),
        html.Div(id="event-details", style={
            "whiteSpace": "pre-line", 
            "marginTop": "20px", 
            "padding": "10px",
            "backgroundColor": "#343432",
            "fontFamily": "Consolas",
            "color": "white",
            'borderRadius': '4px'
        })
    ], style={"padding": "20px", "backgroundColor": "#28282B","borderRadius": "8px"}),

    # Input section with Ace Editor (custom mode "timeline") for syntax highlighting
    html.Div([
        dash_ace.DashAceEditor(
            id='ace-editor',
            value=default_timeline,
            mode='timeline',  # custom mode defined in assets/timeline.js
            theme='monokai',
            fontSize=14,
            tabSize=2,
            showPrintMargin=False,
            style={'width': '100%', 'height': '300px', 'borderRadius': '4px',"backgroundColor":"#343432"}
        ),
        html.Button("Update Timeline", id='update-button', n_clicks=0, style={"marginTop": "10px", "padding": "10px 20px", 'width': '100%', 'borderRadius': '4px',"fontFamily": "Consolas",
            "color": "white","backgroundColor":"#343432"}),
        html.Div(id="editor-preview", style={"marginTop": "20px", "color": "white",'borderRadius': '4px'})
    ], style={'marginTop': '20px', 'padding': '20px', 'backgroundColor': '#28282B', "borderRadius": "8px"})
], style={'maxWidth': '1000px', 'margin': '0 auto', 'backgroundColor': '#28282B', 'padding': '20px'})

@app.callback(
    Output("timeline", "figure"),
    [Input("update-button", "n_clicks"),
     Input("timeline", "clickData")],
    State("ace-editor", "value")
)
def update_timeline_callback(n_clicks, clickData, editor_value):
    events = parse_events(editor_value)
    if not events:
        return go.Figure()
    df = create_dataframe(events)
    clicked_time = None
    if clickData is not None:
        ts_str = clickData["points"][0]["customdata"]["timestamp"]
        try:
            clicked_time = datetime.fromisoformat(ts_str)
        except Exception:
            clicked_time = None
    fig = create_figure(df, clicked_time)
    return fig

@app.callback(
    Output("event-details", "children"),
    Input("timeline", "clickData")
)
def display_event(clickData):
    if clickData is None:
        return "Click on an event marker to see details."
    data = clickData["points"][0]["customdata"]
    return f"Time: {data['timestamp']}\nObject: {data['object']}\nMessage: {data['message']}"


if __name__ == '__main__':
    app.run_server(debug=True)
