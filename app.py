###############################################################
#  PAC3 – Dashboard Storytelling “Hotel Bookings Cancellations”
#  ────────────────────────────────────────────────────────────
#  Llibreria central: shiny (for python)  |  Gràfics: plotly
#  Autor: Jordi Almiñana Domènech
#  Data: 2025-05-30
###############################################################

# ── 1. Imports ───────────────────────────────────────────────
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from shiny import App, ui, render, reactive
from pathlib import Path

# ── 2. Carrega i pre-processat de dades ──────────────────────
ROOT = Path(__file__).parent
CSV  = ROOT / "hotel_bookings.csv"

@reactive.Calc
def bookings() -> pd.DataFrame:
    """Lectura i pre-processat equivalent al .Rmd original."""
    df = (
        pd.read_csv(CSV)
          # dates
          .assign(arrival_date = 
                  lambda d: pd.to_datetime(
                      d.arrival_date_year.astype(str)   + "-" +
                      d.arrival_date_month              + "-" +
                      d.arrival_date_day_of_month.astype(str),
                      format="%Y-%B-%d"))
    )

    # variables d’interès agregades
    df["total_nights"] = df.stays_in_week_nights + df.stays_in_weekend_nights
    df["is_canceled_lbl"] = df.is_canceled.replace({0:"Confirmada", 1:"Cancel·lada"})
    df["market_segment"]  = df.market_segment.str.replace("Complementary", "Compl.")  # breu
    return df


# ── 3. Funcions gràfiques reutilitzables ─────────────────────
def plot_problem(df):
    data = df.groupby("hotel")["is_canceled"].agg(
        pct_cancel = "mean", n = "size").reset_index()
    fig = px.bar(data, x="hotel", y="pct_cancel",
                 color="hotel", text=data.pct_cancel.map(lambda x:f"{x:.1%}"),
                 title="Plantejament · % de cancel·lacions per tipus d’hotel",
                 labels={"pct_cancel":"% cancel·lacions"})
    fig.update_traces(textposition="outside")
    fig.update_yaxes(tickformat=".0%")
    return fig


def plot_temporal(df):
    data = (
        df.groupby(df.arrival_date.dt.to_period("M"))["is_canceled"]
          .mean().reset_index()
          .assign(arrival_date=lambda d: d.arrival_date.astype(str))
    )
    fig = px.line(data, x="arrival_date", y="is_canceled", markers=True,
                  title="Temporalitat · Cancel·lacions mensuals",
                  labels={"is_canceled":"% cancel·lacions", "arrival_date":"Mes"})
    fig.update_yaxes(tickformat=".0%")
    return fig


def plot_lead_time(df):
    fig = px.box(df, x="is_canceled_lbl", y="lead_time", points="all",
                 color="is_canceled_lbl", title="Lead Time · Distribució")
    return fig


def plot_channels(df):
    data = (
        df.groupby("distribution_channel")
          .agg(pct_cancel=("is_canceled","mean"),
               adr_mean=("adr","mean"),
               n=("is_canceled","size"))
          .reset_index()
    )
    fig = px.scatter(data, x="adr_mean", y="pct_cancel", size="n",
                     color="distribution_channel",
                     title="Canal de reserva · ADR, volum i % cancel·lació",
                     labels={"adr_mean":"ADR mitjà", "pct_cancel":"% cancel·lacions"})
    fig.update_yaxes(tickformat=".0%")
    return fig


def plot_client_types(df):
    data = df.groupby("customer_type")["is_canceled"].mean().reset_index()
    fig = px.bar(data, x="customer_type", y="is_canceled",
                 title="Tipus de client · % cancel·lacions",
                 labels={"is_canceled":"% cancel·lacions"})
    fig.update_yaxes(tickformat=".0%")
    return fig


def plot_policies(df):
    """Dipòsit vs flexibilitat."""
    # Dipòsit
    dep = df.groupby("deposit_type")["is_canceled"].mean().reset_index()
    fig1 = px.pie(dep, names="deposit_type", values="is_canceled",
                  title="Política de dipòsit · % cancel·lació", hole=.4)
    fig1.update_traces(textposition='inside', texttemplate='%{value:.1%}')

    # Flexibilitat (booking_changes>0)
    flex = df.assign(change = np.where(df.booking_changes>0,"Amb canvis","Sense canvis"))
    flex = flex.groupby("change")["is_canceled"].mean().reset_index()
    fig2 = px.pie(flex, names="change", values="is_canceled",
                  title="Flexibilitat · % cancel·lació", hole=.4)
    fig2.update_traces(textposition='inside', texttemplate='%{value:.1%}')
    return fig1, fig2


def sankey_flow(df):
    """Segment → Canal → Cancel·lació (Sankey)."""
    g = (df.groupby(["market_segment","distribution_channel","is_canceled_lbl"])
            .size().reset_index(name="count"))
    src_lv1 = g.market_segment
    trg_lv1 = g.distribution_channel
    src_lv2 = g.distribution_channel
    trg_lv2 = g.is_canceled_lbl

    source = pd.concat([src_lv1, src_lv2])
    target = pd.concat([trg_lv1, trg_lv2])
    value  = pd.concat([g["count"], g["count"]])

    labels = pd.Series(pd.concat([source, target]).unique())
    src_idx = source.map(lambda x: labels[labels==x].index[0])
    trg_idx = target.map(lambda x: labels[labels==x].index[0])

    fig = go.Figure(go.Sankey(
        node=dict(label=labels.tolist()),
        link=dict(source=src_idx, target=trg_idx, value=value)))
    fig.update_layout(title="Flux de reserves")
    return fig


# ── 4. Interfície d’usuari ───────────────────────────────────
app_ui = ui.page_fluid(
    ui.h2("Dashboard Cancel·lacions Hotel·leres"),
    ui.navset_tab(
        ui.nav_panel("Plantejament",  ui.output_plot("p_problem")),
        ui.nav_panel("Temporalitat",  ui.output_plot("p_temp")),
        ui.nav_panel("Lead Time",     ui.output_plot("p_lead")),
        ui.nav_panel("Canals",        ui.output_plot("p_chan")),
        ui.nav_panel("Clientela",     ui.output_plot("p_client")),
        ui.nav_panel("Polítiques", 
            ui.row(
                ui.column(6, ui.output_plot("p_dep")),
                ui.column(6, ui.output_plot("p_flex"))
            )),
        ui.nav_panel("Flux", ui.output_plot("p_flow")),
        ui.nav_panel("Recomanacions",
            ui.tags.ul(
                ui.tags.li("💳 Implantar dipòsits als segments de risc."),
                ui.tags.li("🔄 Oferir canvis flexibles per reduir cancel·lacions."),
                ui.tags.li("🌐 Potenciar canals directes amb incentius."),
                ui.tags.li("📈 Overbooking calculat a temporada alta.")
            ))
    )
)

# ── 5. Lògica reactiva / server ─────────────────────────────
def server(input, output, session):

    @output
    @render.plot
    def p_problem():   return plot_problem(bookings())

    @output
    @render.plot
    def p_temp():      return plot_temporal(bookings())

    @output
    @render.plot
    def p_lead():      return plot_lead_time(bookings())

    @output
    @render.plot
    def p_chan():      return plot_channels(bookings())

    @output
    @render.plot
    def p_client():    return plot_client_types(bookings())

    @output
    @render.plot
    def p_dep():       
        f1, _ = plot_policies(bookings()); return f1

    @output
    @render.plot
    def p_flex():      
        _, f2 = plot_policies(bookings()); return f2

    @output
    @render.plot
    def p_flow():      return sankey_flow(bookings())


# ── 6. Objecte Shiny App ────────────────────────────────────
app = App(app_ui, server)

