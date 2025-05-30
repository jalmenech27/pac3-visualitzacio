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

@st.cache_data(show_spinner=False)
def load_data(path: str = "hotel_bookings.csv") -> pd.DataFrame:
    """Llegeix el dataset cru i afegeix camp de data, etiquetes i metadades útils."""
    df = pd.read_csv(path)

    # Columnes de data → unifiquem en un sol camp datetime
    df["arrival_date"] = pd.to_datetime(
        df.arrival_date_year.astype(str) + "-" + df.arrival_date_month + "-" + df.arrival_date_day_of_month.astype(str),
        format="%Y-%B-%d",
        errors="coerce",
    )

    # Altres derivades
    df["total_nights"] = df.stays_in_week_nights + df.stays_in_weekend_nights
    df["is_canceled_lbl"] = df.is_canceled.replace({0: "Confirmada", 1: "Cancel·lada"})
    df["market_segment"] = df.market_segment.str.replace("Complementary", "Compl.")

    return df


df = load_data()

# ─────────────────────────────────────────────────────────────
# 2. Sidebar · filtres interactius
# ─────────────────────────────────────────────────────────────

st.sidebar.header("Filtres de període temporal")

# Rang temporal (date_input retorna tuple de python dates)
min_date, max_date = df.arrival_date.min(), df.arrival_date.max()
start_date, end_date = st.sidebar.date_input(
    "Interval de dates",
    (min_date.date(), max_date.date()),
    min_value=min_date.date(),
    max_value=max_date.date(),
)

# Ens assegurem de tenir dos valors
if not isinstance(start_date, date):
    start_date = min_date.date()
if not isinstance(end_date, date):
    end_date = max_date.date()

# DataFrame filtrat
mask = df.arrival_date.between(pd.to_datetime(start_date), pd.to_datetime(end_date))
df_filt = df.loc[mask].copy()

# ─────────────────────────────────────────────────────────────
# 3. Funcions de gràfica
#   (totes reben df per poder aprofitar el filtre)
# ─────────────────────────────────────────────────────────────

COLOR_MAP = {
    "City Hotel": "#0072B2",
    "Resort Hotel": "#D55E00",
}


def plot_problem(df: pd.DataFrame):
    """Percentatge de cancel·lacions per tipus d'hotel."""
    data = (
        df.groupby("hotel")
        ["is_canceled"]
        .agg(pct_cancel="mean", n="size")
        .reset_index()
    )
    fig = px.bar(
        data,
        x="hotel",
        y="pct_cancel",
        color="hotel",
        text=data.pct_cancel.map(lambda x: f"{x:.1%}"),
        color_discrete_map=COLOR_MAP,
        title="Plantejament · % de cancel·lacions per tipus d’hotel",
        labels={"pct_cancel": "% cancel·lacions", "hotel": "Tipus d'hotel"},
    )
    fig.update_traces(textposition="outside")
    fig.update_yaxes(tickformat=".0%", range=[0, 1])
    fig.update_layout(showlegend=False)
    return fig


def plot_bubble_anim(df: pd.DataFrame):
    """Evolució temporal de cancel·lacions per canal (bubble chart animat)."""
    # Prepara month_year
    df["month_year"] = df["arrival_date"].dt.to_period("M").astype(str)

    bubble_df = (
        df.groupby(["month_year", "distribution_channel", "hotel"])
        .agg(
            is_canceled_pct=("is_canceled", "mean"),
            lead_time=("lead_time", "mean"),
            num_reserves=("is_canceled", "size"),
        )
        .reset_index()
    )

    bubble_df["is_canceled_pct"] *= 100

    fig = px.scatter(
        bubble_df,
        x="is_canceled_pct",
        y="lead_time",
        size="num_reserves",
        color="hotel",
        animation_frame="month_year",
        animation_group="distribution_channel",
        hover_name="distribution_channel",
        size_max=60,
        range_x=[0, bubble_df["is_canceled_pct"].max() + 5],
        range_y=[0, bubble_df["lead_time"].max() + 20],
        labels={
            "is_canceled_pct": "% Cancel·lació",
            "lead_time": "Lead time mitjà (dies)",
            "num_reserves": "Nombre de reserves",
            "hotel": "Tipus d'hotel",
        },
        title="Evolució de Cancel·lacions per Canal al llarg del Temps",
        color_discrete_map=COLOR_MAP,
    )

    fig.update_layout(transition={"duration": 1000}, legend_title_text="Tipus d'hotel")
    return fig


def plot_temporal_heatmap(df: pd.DataFrame):
    """Heatmap any × mes del % de cancel·lacions."""
    data = df.copy()
    data["year"] = data.arrival_date.dt.year.astype(str)
    data["month"] = data.arrival_date.dt.month_name().str[:3]

    heat = (
        data.groupby(["month", "year"])["is_canceled"]
        .mean()
        .mul(100)
        .reset_index()
    )

    months_order = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    heat["month"] = pd.Categorical(heat["month"], categories=months_order, ordered=True)
    heat = heat.pivot(index="month", columns="year", values="is_canceled")

    fig = px.imshow(
        heat,
        text_auto=".1f",
        color_continuous_scale="Reds",
        aspect="auto",
        labels={"x": "Any", "y": "Mes", "color": "% Cancel·lació"},
        title="Temporalitat · Heatmap mensual del % de cancel·lacions",
    )
    return fig


def plot_lead_time_hist(df: pd.DataFrame):
    """Histograma apilat de cancel·lacions per franges de lead time."""
    bins = [-1, 30, 60, 90, 120, 180, 365, np.inf]
    labels = [
        "0–30",
        "31–60",
        "61–90",
        "91–120",
        "121–180",
        "181–365",
        ">365",
    ]
    data = df.copy()
    data["lead_time_cat"] = pd.cut(data.lead_time, bins=bins, labels=labels)

    hist = (
        data.groupby(["lead_time_cat", "is_canceled_lbl"]).size().reset_index(name="count")
    )

    hist["pct"] = hist.groupby("lead_time_cat")["count"].apply(lambda x: x / x.sum())

    fig = px.bar(
        hist,
        x="lead_time_cat",
        y="pct",
        color="is_canceled_lbl",
        barmode="stack",
        labels={"lead_time_cat": "Lead time (dies)", "pct": "%"},
        title="Lead Time · Distribució de cancel·lacions",
        color_discrete_sequence=["#CC79A7", "#56B4E9"],
    )
    fig.update_yaxes(tickformat=".0%")
    fig.update_layout(legend_title_text="Estat de reserva")
    return fig


def plot_channels(df: pd.DataFrame):
    data = (
        df.groupby("distribution_channel")
        .agg(pct_cancel=("is_canceled", "mean"), adr_mean=("adr", "mean"), n=("is_canceled", "size"))
        .reset_index()
    )
    fig = px.scatter(
        data,
        x="adr_mean",
        y="pct_cancel",
        size="n",
        color="distribution_channel",
        title="Canal de reserva · ADR, volum i % cancel·lació",
        labels={"adr_mean": "ADR mitjà", "pct_cancel": "% cancel·lacions"},
    )
    fig.update_yaxes(tickformat=".0%")
    return fig


def plot_client_types(df: pd.DataFrame):
    data = df.groupby("customer_type")["is_canceled"].mean().reset_index()
    fig = px.bar(
        data,
        x="customer_type",
        y="is_canceled",
        title="Tipus de client · % cancel·lacions",
        labels={"is_canceled": "% cancel·lacions", "customer_type": "Tipus de client"},
    )
    fig.update_yaxes(tickformat=".0%")
    return fig


def plot_policies(df: pd.DataFrame):
    # Dipòsit
    dep = df.groupby("deposit_type")["is_canceled"].mean().reset_index()
    fig1 = px.bar(
        dep,
        x="deposit_type",
        y="is_canceled",
        title="Política de dipòsit · % cancel·lació",
        labels={"is_canceled": "% cancel·lació", "deposit_type": "Dipòsit"},
    )
    fig1.update_yaxes(tickformat=".0%")

    # Flexibilitat
    flex = df.assign(change=np.where(df.booking_changes > 0, "Amb canvis", "Sense canvis"))
    flex = flex.groupby("change")["is_canceled"].mean().reset_index()
    fig2 = px.bar(
        flex,
        x="change",
        y="is_canceled",
        title="Flexibilitat · % cancel·lació",
        labels={"is_canceled": "% cancel·lació", "change": "Canvis"},
    )
    fig2.update_yaxes(tickformat=".0%")
    return fig1, fig2


def sankey_flow(df: pd.DataFrame):
    g = (
        df.groupby(["market_segment", "distribution_channel", "is_canceled_lbl"]).size().reset_index(name="count")
    )

    # Nodes i enllaços
    labels = pd.Series(pd.concat([g.market_segment, g.distribution_channel, g.is_canceled_lbl]).unique())
    label_to_idx = {label: idx for idx, label in labels.items()}

    # Primer nivell: market_segment → distribution_channel
    src_lv1 = g.market_segment.map(label_to_idx)
    trg_lv1 = g.distribution_channel.map(label_to_idx)

    # Segon nivell: distribution_channel → is_canceled_lbl
    src_lv2 = g.distribution_channel.map(label_to_idx)
    trg_lv2 = g.is_canceled_lbl.map(label_to_idx)

    source = pd.concat([src_lv1, src_lv2])
    target = pd.concat([trg_lv1, trg_lv2])
    value = pd.concat([g["count"], g["count"]])

    fig = go.Figure(
        go.Sankey(
            node=dict(label=labels.tolist()),
            link=dict(source=source, target=target, value=value),
        )
    )
    fig.update_layout(title="Flux de reserves")
    return fig

# ─────────────────────────────────────────────────────────────
# 4. Interfície principal (una pàgina)
# ─────────────────────────────────────────────────────────────

st.title("Dashboard Storytelling · Cancel·lacions Hotel·leres (PAC3)")

# 4.1 Plantejament
st.header("Plantejament del problema")
st.plotly_chart(plot_problem(df_filt), use_container_width=True)

# 4.2 Evolució per canal (Bubble)
st.header("Evolució de cancel·lacions per canal")
st.plotly_chart(plot_bubble_anim(df_filt), use_container_width=True)

# 4.3 Temporalitat (Heatmap)
st.header("Temporalitat de les cancel·lacions")
st.plotly_chart(plot_temporal_heatmap(df_filt), use_container_width=True)

# 4.4 Lead Time
st.header("Lead Time")
st.plotly_chart(plot_lead_time_hist(df_filt), use_container_width=True)

# 4.5 Canals de reserva (ADR, volum, % cancel·lació)
st.header("Canals de reserva")
st.plotly_chart(plot_channels(df_filt), use_container_width=True)

# 4.6 Tipus de client
st.header("Tipus de client")
st.plotly_chart(plot_client_types(df_filt), use_container_width=True)

# 4.7 Polítiques de reserva
st.header("Polítiques de reserva")
col1, col2 = st.columns(2)
fig1, fig2 = plot_policies(df_filt)
col1.plotly_chart(fig1, use_container_width=True)
col2.plotly_chart(fig2, use_container_width=True)

# 4.8 Flux complet (Sankey)
st.header("Flux de reserves")
st.plotly_chart(sankey_flow(df_filt), use_container_width=True)

# 4.9 Recomanacions finals
st.markdown("---")
st.header("Recomanacions finals")
st.markdown(
    """
- 💳 **Implantar dipòsits** als segments amb risc alt de cancel·lació.
- 🔄 **Oferir canvis flexibles** per reduir cancel·lacions en lloc d'anul·lacions directes.
- 🌐 **Potenciar canals directes** amb incentius (descomptes o beneficis addicionals).
- 📈 **Aplicar overbooking calculat** durant la temporada alta.
    """
)

# Peu de pàgina
st.caption("Autor: Jordi Almiñana Domènech | UOC · Visualització de Dades · PAC3 · 2025")
