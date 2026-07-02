import streamlit as st
import pandas as pd
import joblib
from streamlit_echarts import st_echarts
from pathlib import Path

# ----------------------------------------------------
# Page Configuration
# ----------------------------------------------------

st.set_page_config(
    page_title="Samruddhi Agro Inventory Prediction",
    page_icon="📦",
    layout="wide"
)

# ----------------------------------------------------
# Load Files
# ----------------------------------------------------

BASE_DIR = Path(__file__).parent

model = joblib.load(BASE_DIR / "inventory_model_cat.pkl")
encoder = joblib.load(BASE_DIR / "product_encoder.pkl")
monthly = pd.read_excel(BASE_DIR / "Monthly_Product_Sales.xlsx")

st.title("📦 Samruddhi Agro Inventory Prediction")

# ----------------------------------------------------
# Latest Available Data
# ----------------------------------------------------

latest_year = int(monthly["Year"].max())

latest_month = int(
    monthly[monthly["Year"] == latest_year]["Month"].max()
)

st.info(
    f"Latest Historical Data Available : {latest_month:02d}-{latest_year}"
)

# ----------------------------------------------------
# Product Selection
# ----------------------------------------------------

product = st.selectbox(
    "🔍 Select Product",
    sorted(monthly["Item Name"].unique())
)

pid = encoder.transform([product])[0]

st.write(f"**Product ID :** {pid}")

# ----------------------------------------------------
# Historical Data
# ----------------------------------------------------

history = monthly[
    monthly["Item Name"] == product
].sort_values(["Year", "Month"])

history["Period"] = (
    history["Month"].astype(str).str.zfill(2)
    + "-"
    + history["Year"].astype(str)
)

st.subheader("📈 Historical Sales")

st.dataframe(
    history,
    use_container_width=True
)

# ----------------------------------------------------
# Metrics
# ----------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Months Available",
        len(history)
    )

with col2:
    last_qty = history.iloc[-1]["Quantity"]

    st.metric(
        "Last Month Sales",
        round(last_qty)
    )

# ----------------------------------------------------
# Historical Chart
# ----------------------------------------------------

option = {

    "tooltip": {
        "trigger": "axis"
    },

    "xAxis": {
        "type": "category",
        "data": history["Period"].tolist()
    },

    "yAxis": {
        "type": "value",
        "name": "Quantity"
    },

    "series": [

        {

            "name": "Historical",

            "type": "line",

            "smooth": True,

            "data": history["Quantity"].tolist()

        }

    ]
}

st_echarts(option, height="420px")

# ----------------------------------------------------
# Prediction Section
# ----------------------------------------------------

st.subheader("🔮 Predict Future Inventory")

future_periods = []

for y in range(latest_year, latest_year + 3):

    for m in range(1, 13):

        if (y > latest_year) or (y == latest_year and m > latest_month):

            future_periods.append(f"{y}-{m:02d}")

selected = st.selectbox(
    "Forecast Month",
    future_periods
)

year = int(selected.split("-")[0])
month = int(selected.split("-")[1])

# ----------------------------------------------------
# Predict
# ----------------------------------------------------

if st.button("Predict Inventory"):

    X = [[
        pid,
        year,
        month
    ]]

    prediction = model.predict(X)[0]

    difference = prediction - last_qty

    percent = (difference / last_qty) * 100 if last_qty != 0 else 0

    st.success(
        f"Recommended Inventory : {round(prediction)} Units"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Predicted Quantity",
            round(prediction)
        )

    with col2:

        st.metric(
            "Growth vs Last Month",
            f"{percent:.1f}%"
        )

    # ------------------------------------------
    # Historical + Prediction
    # ------------------------------------------

    xaxis = history["Period"].tolist()

    prediction_period = f"{month:02d}-{year}"

    xaxis.append(prediction_period)

    history_values = history["Quantity"].tolist()

    history_values.append(None)

    prediction_values = [None] * len(history)

    prediction_values.append(round(prediction))

    option2 = {

        "tooltip": {
            "trigger": "axis"
        },

        "legend": {
            "data": [
                "Historical",
                "Prediction"
            ]
        },

        "xAxis": {
            "type": "category",
            "data": xaxis
        },

        "yAxis": {
            "type": "value",
            "name": "Quantity"
        },

        "series": [

            {

                "name": "Historical",

                "type": "line",

                "smooth": True,

                "data": history_values

            },

            {

                "name": "Prediction",

                "type": "line",

                "smooth": True,

                "data": prediction_values

            }

        ]

    }

    st.subheader("📊 Historical + Forecast")

    st_echarts(option2, height="450px")