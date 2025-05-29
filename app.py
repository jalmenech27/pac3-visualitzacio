###############################################################
#  PAC3 – Dashboard Storytelling “Hotel Bookings Cancellations”
#  Versió Streamlit (per a Streamlit Cloud)
#  Autor: Jordi Almiñana Domènech
#  Data: 2025-05-30
###############################################################

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="PAC3: Cancel·lacions Hotel·leres", layout="wide")

# ── 1. Carrega i pre-processat de dades ──────────────────────
@st.cache_data
def load_data():
    df = (
        pd.read_csv("hotel_bookings.csv")
          # dates
          .assign(arrival_date = 
                  lambda d: pd.to_datetime(
                      d.arrival_date_year.astype(str)   + "-" +
                      d.arrival_date_month              + "-" +
                      d.arrival_date_day_of_month.astype(str),
                      format="%Y-%B-%d"))
    )
    df["total_nights"] = df.stays_in_week_nights + df.stays_in_weekend_nights
    df["is_canceled_lbl"] = df.is_canceled.replace({0:"Confirmada", 1:"Cancel·lada"})
    df["market_segment"]  = df.market_segment.str.replace("Complementary", "Compl.")
    return df

df = load_data()

# ── 2. Funcions gràfiques ───────────────────────────────────
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

# ── 3. Interfície Streamlit (amb pestanyes) ─────────────────
st.title("Dashboard Storytelling · Cancel·lacions Hotel·leres (PAC3)")
tabs = st.tabs([
    "Plantejament", "Temporalitat", "Lead Time", "Canals",
    "Clientela", "Polítiques", "Flux", "Recomanacions"
])

with tabs[0]:
    st.subheader("Plantejament del problema")
    st.plotly_chart(plot_problem(df), use_container_width=True)

with tabs[1]:
    st.subheader("Temporalitat de les cancel·lacions")
    st.plotly_chart(plot_temporal(df), use_container_width=True)

with tabs[2]:
    st.subheader("Lead Time vs Cancel·lació")
    st.plotly_chart(plot_lead_time(df), use_container_width=True)

with tabs[3]:
    st.subheader("Canals de reserva")
    st.plotly_chart(plot_channels(df), use_container_width=True)

with tabs[4]:
    st.subheader("Tipus de client")
    st.plotly_chart(plot_client_types(df), use_container_width=True)

with tabs[5]:
    st.subheader("Polítiques i flexibilitat")
    col1, col2 = st.columns(2)
    fig1, fig2 = plot_policies(df)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)

with tabs[6]:
    st.subheader("Flux de reserves (Sankey)")
    st.plotly_chart(sankey_flow(df), use_container_width=True)

with tabs[7]:
    st.subheader("Recomanacions finals")
    st.markdown("""
    - 💳 **Implantar dipòsits als segments de risc.**
    - 🔄 **Oferir canvis flexibles per reduir cancel·lacions.**
    - 🌐 **Potenciar canals directes amb incentius.**
    - 📈 **Overbooking calculat a temporada alta.**
    """)

st.markdown("---")
st.caption("Autor: Jordi Almiñana Domènech | PAC3 · UOC · 2025")
