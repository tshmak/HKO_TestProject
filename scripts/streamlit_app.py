import os
import sqlite3
from datetime import datetime, timedelta

import streamlit as st
import pandas as pd
import altair as alt

DB_PATH = os.getenv("DB_PATH", "hko.db")

st.set_page_config(page_title="HKO Forecast Explorer", layout="wide")
st.title("HKO Weather Forecast Explorer")

def get_db():
    return sqlite3.connect(DB_PATH)

def get_forecast_data(forecast_date_start: str, forecast_date_end: str):
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT fetch_date, forecast_date, maxtemp_value, mintemp_value
            FROM forecasts
            WHERE forecast_date >= ? AND forecast_date <= ?
            ORDER BY fetch_date, forecast_date
        """, (forecast_date_start, forecast_date_end)).fetchall()
    df = pd.DataFrame([dict(r) for r in rows])
    df["forecast_date"] = pd.to_datetime(df["forecast_date"], format="%Y%m%d")
    return df

def get_fetch_dates():
    with get_db() as conn:
        rows = conn.execute("""
            SELECT DISTINCT fetch_date FROM forecasts ORDER BY fetch_date
        """).fetchall()
    return [r[0] for r in rows]

col1, col2, col3 = st.columns(3)

with col1:
    show_max = st.checkbox("Max Temperature", value=True)
    show_min = st.checkbox("Min Temperature", value=True)

with col2:
    today = datetime.now().strftime("%Y-%m-%d")
    default_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    default_end = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    date_range = st.date_input(
        "Forecast date range",
        value=(datetime.strptime(default_start, "%Y-%m-%d"), datetime.strptime(default_end, "%Y-%m-%d")),
        min_value=datetime(2020, 1, 1),
        max_value=datetime.now() + timedelta(days=365),
    )

with col3:
    st.write("&nbsp;")
    st.write("&nbsp;")
    show_all = st.checkbox("Show all fetch dates", value=True)

if len(date_range) != 2:
    st.warning("Please select a date range with start and end dates.")
    st.stop()

start_str = date_range[0].strftime("%Y%m%d")
end_str = date_range[1].strftime("%Y%m%d")

df = get_forecast_data(start_str, end_str)

if df.empty:
    st.warning("No data found for the selected date range.")
    st.stop()

fetch_dates = sorted(df["fetch_date"].unique())

if not show_all:
    available_fetch_dates = []
    for fd in fetch_dates:
        count = len(df[df["fetch_date"] == fd])
        available_fetch_dates.append((fd, count))
    default_idx = len(available_fetch_dates) - 1 if available_fetch_dates else 0
    selected = st.selectbox(
        "Select fetch date",
        options=range(len(available_fetch_dates)),
        format_func=lambda i: f"{available_fetch_dates[i][0]} ({available_fetch_dates[i][1]} forecasts)",
    )
    selected_fetch_date = available_fetch_dates[selected][0]
    df = df[df["fetch_date"] == selected_fetch_date]
    fetch_dates = [selected_fetch_date]

temp_cols = []
if show_max:
    temp_cols.append("maxtemp_value")
if show_min:
    temp_cols.append("mintemp_value")

if not temp_cols:
    st.warning("Select at least one temperature type.")
    st.stop()

if len(temp_cols) == 1:
    df_plot = df[["fetch_date", "forecast_date", temp_cols[0]]].copy()
    color_field = "fetch_date:N"
    color_title = "Fetch Date"
else:
    df_plot = df[["fetch_date", "forecast_date", "maxtemp_value", "mintemp_value"]].melt(
        id_vars=["fetch_date", "forecast_date"],
        value_vars=temp_cols,
        var_name="temp_type",
        value_name="temperature",
    )
    df_plot["temp_type"] = df_plot["temp_type"].map({"maxtemp_value": "Max", "mintemp_value": "Min"})
    color_field = alt.Color("fetch_date:N", title="Fetch Date", legend=alt.Legend(orient="bottom"))

y_field = "temperature:Q" if len(temp_cols) > 1 else f"{temp_cols[0]}:Q"

chart = alt.Chart(df_plot).mark_line(point=True).encode(
    x=alt.X("forecast_date:T", title="", axis=alt.Axis(format="%Y-%m-%d")),
    y=alt.Y(y_field, title="Temperature (°C)"),
    color=color_field,
    strokeDash=alt.StrokeDash("temp_type:N") if len(temp_cols) > 1 else alt.Undefined,
    tooltip=["fetch_date", "forecast_date", "temperature"] if len(temp_cols) > 1 else ["fetch_date", "forecast_date", temp_cols[0]],
).properties(
    width=800,
    height=400,
    title="Temperature Forecasts"
).interactive()

st.altair_chart(chart, width='stretch')

with st.expander("Raw data"):
    st.dataframe(df_plot, width='stretch')
