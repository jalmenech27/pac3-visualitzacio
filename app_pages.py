import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="PAC3: Cancel·lacions hoteleres", layout="wide")

df = pd.read_csv("hotel_bookings.csv")
df["arrival_date"] = pd.to_datetime(
    df["arrival_date_year"].astype(str) + "-" +
    df["arrival_date_month"] + "-" +
    df["arrival_date_day_of_month"].astype(str)
)
df["total_nights"] = df.stays_in_week_nights + df.stays_in_weekend_nights
df["is_canceled_lbl"] = df.is_canceled.replace({0:"Confirmada", 1:"Cancel·lada"})
df["market_segment"]  = df.market_segment.str.replace("Complementary", "Compl.")

st.title("Dashboard Storytelling · Cancel·lacions Hotel·leres (PAC3)")

st.header("Plantejament del problema")
st.plotly_chart(plot_problem(df), use_container_width=True)

st.header("Temporalitat de les cancel·lacions")
st.plotly_chart(plot_temporal(df), use_container_width=True)

st.header("Lead Time")
st.plotly_chart(plot_lead_time(df), use_container_width=True)

st.header("Canals de reserva")
st.plotly_chart(plot_channels(df), use_container_width=True)

st.header("Tipus de client")
st.plotly_chart(plot_client_types(df), use_container_width=True)

st.header("Polítiques de reserva")
col1, col2 = st.columns(2)
fig1, fig2 = plot_policies(df)
col1.plotly_chart(fig1, use_container_width=True)
col2.plotly_chart(fig2, use_container_width=True)

st.header("Flux de reserves (Sankey)")
st.plotly_chart(sankey_flow(df), use_container_width=True)

st.header("Evolució de Cancel·lacions (Bubble Chart animat)")
st.plotly_chart(plot_bubble_anim(df), use_container_width=True)

st.markdown("---")
st.header("Recomanacions finals")
st.markdown("""
- 💳 Implantar dipòsits als segments de risc.
- 🔄 Oferir canvis flexibles per reduir cancel·lacions.
- 🌐 Potenciar canals directes amb incentius.
- 📈 Overbooking calculat a temporada alta.
""")
st.caption("Autor: Jordi Almiñana Domènech | PAC3 · UOC · 2025")
