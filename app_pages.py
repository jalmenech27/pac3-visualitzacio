import dash
from dash import dcc, html
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv("hotel_bookings.csv")
df["arrival_date"] = pd.to_datetime(
    df["arrival_date_year"].astype(str) + "-" +
    df["arrival_date_month"] + "-" +
    df["arrival_date_day_of_month"].astype(str)
)
df["total_nights"] = df.stays_in_week_nights + df.stays_in_weekend_nights
df["is_canceled_lbl"] = df.is_canceled.replace({0: "Confirmada", 1: "Cancel·lada"})
df["market_segment"] = df.market_segment.str.replace("Complementary", "Compl.")

# Funcions gràfiques (les mateixes que ja tens, omitides aquí per brevetat)
# ... (Inclou: plot_problem, plot_temporal, plot_lead_time, plot_channels, plot_client_types, plot_policies, sankey_flow, plot_bubble_anim)

# ------ Layout "tot en una sola pàgina" ------
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H2("Dashboard Cancel·lacions Hotel·leres (PAC3)"),
    html.Div([
        html.H3("Plantejament del problema"),
        dcc.Graph(figure=plot_problem(df)),
    ], style={"marginBottom":40}),
    
    html.Div([
        html.H3("Temporalitat de les cancel·lacions"),
        dcc.Graph(figure=plot_temporal(df)),
    ], style={"marginBottom":40}),
    
    html.Div([
        html.H3("Lead Time"),
        dcc.Graph(figure=plot_lead_time(df)),
    ], style={"marginBottom":40}),
    
    html.Div([
        html.H3("Canals de reserva"),
        dcc.Graph(figure=plot_channels(df)),
    ], style={"marginBottom":40}),
    
    html.Div([
        html.H3("Tipus de client"),
        dcc.Graph(figure=plot_client_types(df)),
    ], style={"marginBottom":40}),
    
    html.Div([
        html.H3("Polítiques de reserva"),
        html.Div([
            dcc.Graph(figure=plot_policies(df)[0]),
            dcc.Graph(figure=plot_policies(df)[1]),
        ], style={"display": "flex", "justifyContent": "space-between"}),
    ], style={"marginBottom":40}),
    
    html.Div([
        html.H3("Flux de reserves (Sankey)"),
        dcc.Graph(figure=sankey_flow(df)),
    ], style={"marginBottom":40}),
    
    html.Div([
        html.H3("Evolució de Cancel·lacions (Bubble Chart animat)"),
        dcc.Graph(figure=plot_bubble_anim(df)),
    ], style={"marginBottom":40}),
    
    html.Hr(),
    html.H3("Recomanacions finals"),
    html.Ul([
        html.Li("💳 Implantar dipòsits als segments de risc."),
        html.Li("🔄 Oferir canvis flexibles per reduir cancel·lacions."),
        html.Li("🌐 Potenciar canals directes amb incentius."),
        html.Li("📈 Overbooking calculat a temporada alta."),
    ]),
    html.Br(),
    html.Div("Autor: Jordi Almiñana Domènech | PAC3 · UOC · 2025", style={"fontSize": 12, "textAlign": "center"})
])

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
