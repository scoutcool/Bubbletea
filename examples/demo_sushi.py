#import streamlit as st
#import os
import streamlit as st
st.set_page_config(page_title="Testing Dashboard Layout", layout="wide")

import bubbletea
import math
from demolinks import url
from demoqueries import query

#SUSHI
data = bubbletea.load_subgraph(url["sushiexchange"], query["sushiexchange"])
pairDayDatas = bubbletea.aggregate_timeseries(  
    data["pairDayDatas"],
    time_column="date",
    interval=bubbletea.TimeseriesInterval.DAILY,
    columns=[
        bubbletea.ColumnConfig(
            name="volumeUSD",
            aggregate_method=bubbletea.AggregateMethod.SUM,
            na_fill_value=0.0
        )
    ],
)
pairDayDatas["fees"] = pairDayDatas["volumeUSD"]*0.003

#AAVE
data = bubbletea.load_subgraph(url["aave"], query["aave"])
deposits = data["deposits"]
deposits = deposits[deposits['reserve.symbol'] == 'AAVE'] #Only show deposits with AAVE tokens
deposits['amount'] = deposits["amount"] / math.pow(10, 18) #Convert token amount with 18 decimals
deposits["fees"] = deposits["amount"]+400

deposits_hourly = bubbletea.aggregate_timeseries(
        data=deposits,
        time_column="timestamp",
        interval=bubbletea.TimeseriesInterval.HOURLY,
        columns=[
            bubbletea.ColumnConfig(
                name="amount",
                aggregate_method=bubbletea.AggregateMethod.SUM,
                na_fill_value=0.0,
            ),
             bubbletea.ColumnConfig(
                name="fees",
                aggregate_method=bubbletea.AggregateMethod.SUM,
                na_fill_value=0.0,
            )
        ],
    )
    
bubbletea.plot_line(
        title='My first line chart',
        df=deposits_hourly,
        x={"title": "Time", "field": "timestamp"},
        ys=[{"title": "Amount", "field": "amount"}]
    )
