import streamlit as st
import pandas as pd
import joblib
from streamlit_echarts import st_echarts

# ----------------------------
# Load Files
# ----------------------------

model = joblib.load("inventory_model.pkl")
encoder = joblib.load("product_encoder.pkl")
monthly = pd.read_excel("Monthly_Product_Sales.xlsx")

st.set_page_config(page_title="Inventory Prediction", layout="wide")

st.title("📦 Samruddhi Agro Inventory Prediction")

# ----------------------------
# Product Selection
# ----------------------------

product = st.selectbox(
    "Select Product",
    sorted(monthly["Item Name"].unique())
)

pid = encoder.transform([product])[0]

st.write(f"**Product ID :** {pid}")

# ----------------------------
# Historical Data
# ----------------------------

history = monthly[
    monthly["Item Name"] == product
].sort_values(["Year", "Month"])

history["Period"] = (
    history["Month"].astype(str)
    + "-"
    + history["Year"].astype(str)
)

st.subheader("Historical Sales")

st.dataframe(history)

# ----------------------------
# Historical Chart
# ----------------------------

option = {
    "tooltip": {"trigger": "axis"},
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
            "name": "Quantity",
            "type": "line",
            "smooth": True,
            "data": history["Quantity"].tolist()
        }
    ]
}

st_echarts(option, height="400px")

# ----------------------------
# Prediction
# ----------------------------

st.subheader("Predict Future Inventory")

col1, col2 = st.columns(2)

with col1:
    year = st.selectbox(
        "Year",
        [2026, 2027, 2028]
    )

with col2:
    month = st.selectbox(
        "Month",
        list(range(1, 13))
    )

# ----------------------------
# Predict
# ----------------------------

if st.button("Predict Inventory"):

    X = [[pid, year, month]]

    prediction = model.predict(X)[0]

    st.success(
        f"Recommended Inventory : {round(prediction)} Units"
    )

    # ----------------------------
    # Historical + Prediction
    # ----------------------------

    forecast = history.copy()

    period = f"{month}-{year}"

    xaxis = forecast["Period"].tolist() + [period]

    history_values = forecast["Quantity"].tolist() + [None]

    prediction_values = [None] * len(forecast) + [round(prediction)]

    option2 = {
        "tooltip": {"trigger": "axis"},
        "legend": {
            "data": ["History", "Prediction"]
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
                "name": "History",
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

    st.subheader("Historical + Prediction")

    st_echarts(option2, height="450px")