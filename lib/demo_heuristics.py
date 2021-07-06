import pandas as pd
import streamlit as st
from earlgrey.charts.line import plot as plot_line

""" 
--- Nominal Heuristics ---
"""
data1 = pd.DataFrame(
    [
        {"round": "2202", "amount": 828.2251570173},
        {"round": "2203", "amount": 4827.6408169493},
        {"round": "2204", "amount": 463730.3969766065},
        {"round": "2205", "amount": 2073.7760719195},
        {"round": "2206", "amount": 3688.1534016416},
        {"round": "2207", "amount": 10989.8938808655},
        {"round": "2208", "amount": 4315.027494327},
        {"round": "2209", "amount": 6081.6985613663},
        {"round": "2210", "amount": 89277.0851194817},
    ]
)

data2 = pd.DataFrame(
    [
        {"round": 2202, "amount": 828.2251570173},
        {"round": 2203, "amount": 4827.6408169493},
        {"round": 2204, "amount": 463730.3969766065},
        {"round": 2205, "amount": 2073.7760719195},
        {"round": 2206, "amount": 3688.1534016416},
        {"round": 2207, "amount": 10989.8938808655},
        {"round": 2208, "amount": 4315.027494327},
        {"round": 2209, "amount": 6081.6985613663},
        {"round": 2210, "amount": 89277.0851194817},
    ]
)

st.subheader("Nominal numbers as string")
st.write(data1)

plot_line(
    data1,
    x={"field": "round", "title": "Round"},
    ys=[
        {
            "field": "amount",
            "title": "Amount",
        }
    ],
)

st.subheader("Nominal numbers as number")
st.write(data2)

plot_line(
    data2,
    x={"field": "round", "title": "Round"},
    ys=[
        {
            "field": "amount",
            "title": "Amount",
        }
    ],
)

""" 
--- Temporal Heuristics ---
"""

data3 = pd.DataFrame(
    [
        {"timestamp": 1622604285, "amount": "10.61"},
        {"timestamp": 1622587860, "amount": "174.369647093131412495"},
        {"timestamp": 1622587466, "amount": "100"},
        {"timestamp": 1622587869, "amount": "350.960251"},
        {"timestamp": 1622549795, "amount": "135.702228799664830896"},
        {"timestamp": 1622536122, "amount": "2587.295826956326400766"},
        {"timestamp": 1622570789, "amount": "148.50322579"},
        {"timestamp": 1622556317, "amount": "3989.013487515292353837"},
        {"timestamp": 1622582747, "amount": "62.955517806121539286"},
    ]
)

data4 = pd.DataFrame(
    [
        {"timestamp": "1622604285", "amount": "10.61"},
        {"timestamp": "1622587860", "amount": "174.369647093131412495"},
        {"timestamp": "1622587466", "amount": "100"},
        {"timestamp": "1622587869", "amount": "350.960251"},
        {"timestamp": "1622549795", "amount": "135.702228799664830896"},
        {"timestamp": "1622536122", "amount": "2587.295826956326400766"},
        {"timestamp": "1622570789", "amount": "148.50322579"},
        {"timestamp": "1622556317", "amount": "3989.013487515292353837"},
        {"timestamp": "1622582747", "amount": "62.955517806121539286"},
    ]
)

st.subheader("Timestamps as number")
st.write(data3)

plot_line(
    data3,
    x={
        "field": "timestamp",
    },
    ys=[
        {
            "field": "amount",
            "title": "Amount",
        }
    ],
)

st.subheader("Timestamps as string")
st.write(data3)
plot_line(
    data4,
    x={
        "field": "timestamp",
    },
    ys=[
        {
            "field": "amount",
            "title": "Amount",
        }
    ],
)
