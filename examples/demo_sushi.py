#import streamlit as st
#import os
import bubbletea
import math
from demolinks import url
query_hourly = """
{
    pairHourDatas(
        where:{date_gte:1627862400, date_lt:1628535113}
        orderBy: date
        orderDirection: asc
        bypassPagination: true
    ){
        date
        pair{
            token0{
            symbol
        }
        token1{
            symbol
        }
    }
    reserve0
    reserve1
    volumeUSD
    volumeToken0
    volumeToken1
  }
}
"""

query_daily = """
{
    pairDayDatas(
        where:{date_gte:1627862400, date_lt:1628535113}
        orderBy: date
        orderDirection: asc
        bypassPagination: true
  ) {
    id
    date
    token0{
      symbol
      decimals
    }
    token1{
      symbol
      decimals
    }
    volumeUSD
  }
}
"""

data = bubbletea.load_subgraph(url["sushiexchange"], query_daily)
data = data["pairDayDatas"]
print(data)

data_daily = bubbletea.aggregate_timeseries(  
    data,
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

data_daily["fees"] = data_daily["volumeUSD"]*0.003
print(data_daily)

bubbletea.plot_bar(
    title="Daily Fees Collected",
    df= data_daily,
    x={"title": "Time", "field": "date"},
    ys=[{"title": "Fees", "field": "fees"}]
)