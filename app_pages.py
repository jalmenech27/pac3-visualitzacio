import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

# ─────────────────────────────────────────────────────────────
# Configuració general
# ─────────────────────────────────────────────────────────────

st.set_page_config(page_title="PAC3: Cancel·lacions hoteleres", layout="wide")

# ─────────────────────────────────────────────────────────────
# 1. Carrega i preprocessat de dades
# ─────────────────────────────────────────────────────────────

@st.cache_data
def load_data():
    df = pd.read_csv("hotel_bookings.csv")

    # columnes de data -> timestamp
    df["arrival_date"] = pd.to_datetime(
        df.arrival_date_year.astype(str) + "-" +
        df.arrival_date_month + "-" +
        df.arrival_date_day_of_month.astype(str),
        format="%Y-%B-%d"
    )

    # derives utilitzades als gràfics
    df["total_nights"] = df.stays_in_week_nights + df.stays_in_weekend_nights
    df["is_canceled_lbl"] = df.is_canceled.replace({0: "Confirmada", 1: "Cancel·lada"})
    df["market_segment"] = df.market_segment.str.replace("Complementary", "Compl.")
    return df


df = load_data()

# ─────────────────────────────────────────────────────────────
# 2. Filtres – sidebar
# ─────────────────────────────────────────────────────────────

st.sidebar.header("Filtres de període temporal")
min_date = df["arrival_date"].min().date()
max_date = df["arrival_date"].max().date()

start_date, end_date = st.sidebar.date_input(
    "Interval de dates",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if start_date > end_date:
    st.sidebar.error("⚠️ La data inicial no pot ser posterior a la final.")

# Filtre de dates aplicat al dataframe
mask = (df["arrival_date"].dt.date >= start_date) & (df["arrival_date"].dt.date <= end_date)
df_filt = df.loc[mask]

# ─────────────────────────────────────────────────────────────
# 3. Funcions de gràfic
# ─────────────────────────────────────────────────────────────

def plot_problem(df: pd.DataFrame):
    data = (
        df.groupby("hotel")["is_canceled"]
        .agg(pct_cancel="mean", n="size")
        .reset_index()
    )
    fig = px.bar(
        data,
        x="hotel",
        y="pct_cancel",
        color="hotel",
        text=data.pct_cancel.map(lambda x: f"{x:.1%}"),
        labels={"pct_cancel": "% cancel·lacions", "hotel": "Tipus d'hotel"},
        title="Plantejament · % de cancel·lacions per tipus d’hotel",
    )
    fig.update_traces(textposition="outside")
    fig.update_yaxes(tickformat=".0%", range=[0, 1])
    fig.update_layout(showlegend=False)
    return fig


def plot_bubble_anim(df: pd.DataFrame):
    df = df.copy()
    df["month_year"] = df["arrival_date"].dt.to_period("M").astype(str)

    bubble_df = (
        df.groupby(["month_year", "distribution_channel", "hotel"])
        .agg(
            pct_cancel=("is_canceled", "mean"),
            lead_time=("lead_time", "mean"),
            num_reserves=("is_canceled", "size"),
        )
        .reset_index()
    )

    bubble_df["pct_cancel"] *= 100

    fig = px.scatter(
        bubble_df,
        x="pct_cancel",
        y="lead_time",
        size="num_reserves",
        color="hotel",
        animation_frame="month_year",
        animation_group="distribution_channel",
        hover_name="distribution_channel",
        size_max=60,
        range_x=[0, bubble_df["pct_cancel"].max() + 5],
        range_y=[0, bubble_df["lead_time"].max() + 20],
        labels={
            "pct_cancel": "% Cancel·lació",
            "lead_time": "Lead time mitjà (dies)",
            "num_reserves": "# reserves",
            "hotel": "Tipus d'hotel",
        },
        title="Evolució de cancel·lacions per canal al llarg del temps",
        height=550,
    )

    fig.update_layout(transition={"duration": 1000}, legend_title="Tipus d'hotel")
    return fig


def plot_temporal_heatmap(df: pd.DataFrame):
    tmp = df.copy()
    tmp["Year"] = tmp.arrival_date.dt.year
    tmp["Month"] = tmp.arrival_date.dt.month_name().str[:3]

    data = tmp.groupby(["Month", "Year"])["is_canceled"].mean().reset_index()
    data["pct"] = data["is_canceled"] * 100

    # ordenar mesos
    months_order = [
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec",
    ]
    data["Month"] = pd.Categorical(data["Month"], categories=months_order, ordered=True)
    data = data.sort_values(["Month", "Year"])

    # USAR pivot_table en comptes de pivot
    heat_df = data.pivot_table(
        index="Month",
        columns="Year",
        values="pct",
        aggfunc="mean"
    )

    fig = px.imshow(
        heat_df,
        aspect="auto",
        color_continuous_scale="Reds",
        labels=dict(color="% Cancel·lació"),
        title="Temporalitat · Heatmap mensual del % de cancel·lacions",
    )
    fig.update_xaxes(side="top")
    return fig


def plot_lead_time_hist(df: pd.DataFrame):
    df2 = df.copy()
    bins = [0, 30, 60, 90, 120, 150, 180, 999]
    labels = [
        "0–30",
        "31–60",
        "61–90",
        "91–120",
        "121–150",
        "151–180",
        "180+",
    ]
    df2["lead_time_cat"] = pd.cut(df2["lead_time"], bins=bins, labels=labels, right=False)

    hist = (
        df2.groupby(["lead_time_cat", "is_canceled_lbl"]).size().reset_index(name="count")
    )

    # percentatge dins de cada categoria
    hist["pct"] = hist["count"] / hist.groupby("lead_time_cat")["count"].transform("sum")

    fig = px.bar(
        hist,
        x="lead_time_cat",
        y="pct",
        color="is_canceled_lbl",
        barmode="stack",
        text=hist["pct"].map(lambda x: f"{x:.0%}"),
        labels={
            "lead_time_cat": "Dies d'antelació",
            "pct": "% reserves",
            "is_canceled_lbl": "Estat",
        },
        title="Lead Time · Distribució de cancel·lació segons dies d'antelació",
    )
    fig.update_yaxes(tickformat=".0%", range=[0, 1])
    fig.update_layout(legend_orientation="h", legend_y=-0.25)
    return fig


def plot_channel_evol(df: pd.DataFrame):
    # Preparem les dades amb evolució temporal per mes
    df_tmp = df.copy()
    df_tmp["month_year"] = df_tmp["arrival_date"].dt.to_period("M").astype(str)

    bubble_df = (
        df_tmp
        .groupby(["month_year", "distribution_channel"])
        .agg(
            pct_cancel=("is_canceled", "mean"),
            adr_mean=("adr", "mean"),
            num_reserves=("is_canceled", "size"),
        )
        .reset_index()
    )

    bubble_df["pct_cancel"] *= 100

    # Construcció del scatter animat amb eixos girats (X = % cancel·lacions, Y = ADR)
    fig = px.scatter(
        bubble_df,
        x="pct_cancel",
        y="adr_mean",
        size="num_reserves",
        color="distribution_channel",
        animation_frame="month_year",
        animation_group="distribution_channel",
        hover_name="distribution_channel",
        size_max=60,
        range_x=[0, 100],
        range_y=[bubble_df["adr_mean"].min() * 0.9, bubble_df["adr_mean"].max() * 1.1],
        labels={
            "pct_cancel": "% Cancel·lacions",
            "adr_mean": "ADR mitjà",
            "num_reserves": "# reserves",
            "distribution_channel": "Canal",
        },
        title="Evolució de ADR i % cancel·lacions per canal",
        height=550,
    )

    fig.update_layout(
        transition={"duration": 1000},
        legend_title="Canal",
    )
    fig.update_xaxes(tickformat=".0%", title="% Cancel·lacions")
    fig.update_yaxes(title="ADR mitjà")
    return fig



def plot_client_types(df: pd.DataFrame):
    data = df.groupby("customer_type")["is_canceled"].mean().reset_index()
    color_map = {
        "Contract": "#636EFA",         # blau
        "Group": "#00CC96",            # verd
        "Transient": "#AB63FA",        # lila
        "Transient-Party": "#19D3F3",  # turquesa
    }
    fig = px.bar(
        data,
        x="customer_type",
        y="is_canceled",
        color="customer_type",
        color_discrete_map=color_map,
        labels={"is_canceled": "% cancel·lacions", "customer_type": "Tipus de client"},
        title="Tipus de client · % cancel·lacions",
        text=data.is_canceled.map(lambda x: f"{x:.1%}"),
    )
    fig.update_traces(textposition="outside")
    fig.update_yaxes(tickformat=".0%", range=[0, 1])
    fig.update_layout(showlegend=False)
    return fig


def plot_policies(df: pd.DataFrame):
    # Paleta comuna
    color_map_dep = {
        "No Deposit": "#636EFA",   # blau
        "Non Refund": "#00CC96",   # verd
        "Refundable": "#AB63FA",   # lila
    }
    color_map_flex = {
        "Amb canvis": "#636EFA",   # blau
        "Sense canvis": "#00CC96", # verd
    }

    # Dipòsit
    dep = df.groupby("deposit_type")["is_canceled"].mean().reset_index()
    fig1 = px.bar(
        dep,
        x="deposit_type",
        y="is_canceled",
        color="deposit_type",
        color_discrete_map=color_map_dep,
        labels={"is_canceled": "% cancel·lacions", "deposit_type": "Tipus dipòsit"},
        title="Política de dipòsit · % cancel·lació",
        text=dep.is_canceled.map(lambda x: f"{x:.1%}"),
    )
    fig1.update_traces(textposition="outside")
    fig1.update_yaxes(tickformat=".0%", range=[0, 1])
    fig1.update_layout(showlegend=False)

    # Flexibilitat (booking_changes > 0)
    flex = df.assign(change=np.where(df.booking_changes > 0, "Amb canvis", "Sense canvis"))
    flex = flex.groupby("change")["is_canceled"].mean().reset_index()
    fig2 = px.bar(
        flex,
        x="change",
        y="is_canceled",
        color="change",
        color_discrete_map=color_map_flex,
        labels={"is_canceled": "% cancel·lacions", "change": "Flexibilitat"},
        title="Flexibilitat · % cancel·lació",
        text=flex.is_canceled.map(lambda x: f"{x:.1%}"),
    )
    fig2.update_traces(textposition="outside")
    fig2.update_yaxes(tickformat=".0%", range=[0, 1])
    fig2.update_layout(showlegend=False)

    return fig1, fig2


def sankey_flow(df: pd.DataFrame):
    g = (
        df.groupby(["market_segment", "distribution_channel", "is_canceled_lbl"]).size().reset_index(name="count")
    )
    src_lv1 = g.market_segment
    trg_lv1 = g.distribution_channel
    src_lv2 = g.distribution_channel
    trg_lv2 = g.is_canceled_lbl

    source = pd.concat([src_lv1, src_lv2])
    target = pd.concat([trg_lv1, trg_lv2])
    value = pd.concat([g["count"], g["count"]])

    labels = pd.Series(pd.concat([source, target]).unique())
    src_idx = source.map(lambda x: labels[labels == x].index[0])
    trg_idx = target.map(lambda x: labels[labels == x].index[0])

    fig = go.Figure(
        go.Sankey(
            node=dict(label=labels.tolist()),
            link=dict(source=src_idx, target=trg_idx, value=value),
        )
    )
    fig.update_layout(title="Flux de reserves")
    return fig


# ─────────────────────────────────────────────────────────────
# 4. Layout – Pàgina principal
# ─────────────────────────────────────────────────────────────

st.title("Dashboard Storytelling · Cancel·lacions Hoteleres (PAC3)")

# 4.1 Plantejament
st.header("Plantejament del problema")
st.plotly_chart(plot_problem(df_filt), use_container_width=True)

st.markdown("---")

# 4.2 Evolució de cancel·lacions per canal (Bubble)
st.header("Evolució de cancel·lacions per canal")
st.plotly_chart(plot_bubble_anim(df_filt), use_container_width=True)

st.markdown("---")

# 4.3 Temporalitat
st.header("Temporalitat de les cancel·lacions")
st.plotly_chart(plot_temporal_heatmap(df_filt), use_container_width=True)

st.markdown("---")

# 4.4 Lead Time
st.header("Lead Time i cancel·lacions")
st.plotly_chart(plot_lead_time_hist(df_filt), use_container_width=True)

st.markdown("---")

# 4.5 Canals de reserva
st.header("Canals de reserva: ADR i volum")
st.plotly_chart(plot_channel_evol(df_filt), use_container_width=True)

st.markdown("---")

# 4.6 Tipus de client
st.header("Tipus de client")
st.plotly_chart(plot_client_types(df_filt), use_container_width=True)

st.markdown("---")

# 4.7 Polítiques de reserva
st.header("Polítiques de reserva")
fig_dep, fig_flex = plot_policies(df_filt)
col1, col2 = st.columns(2)
col1.plotly_chart(fig_dep, use_container_width=True)
col2.plotly_chart(fig_flex, use_container_width=True)

st.markdown("---")

# 4.8 Flux de reserves (Sankey)
st.header("Flux de reserves")
st.plotly_chart(sankey_flow(df_filt), use_container_width=True)

st.markdown("---")

# 4.9 Recomanacions finals
st.header("Recomanacions finals")
st.markdown(
    """
- 💳 **Implantar dipòsits** als segments de risc.
- 🔄 **Oferir canvis flexibles** per reduir cancel·lacions.
- 🌐 **Potenciar canals directes** amb incentius.
- 📈 **Overbooking calculat** a temporada alta.
"""
)

st.caption("Autor: Jordi Almiñana Domènech · UOC · Visualització de Dades · PAC3 · 2025")

