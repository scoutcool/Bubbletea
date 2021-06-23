import earlgrey.thegraph.thegraph_loader as gl
import earlgrey.crypto_compare as cp
import earlgrey.transformers.timeseries as ts
from pandas.core.frame import DataFrame
import streamlit as st
import pandas as pd
import math
import datetime
import time
from flash_card import flash_card
from charts.line import plot as plot_line

TOKEN_SYMBOL_PRICING = "ETH"
TOKEN_SYMBOL = "WETH"
PERIODS = [ts.TimeseriesInterval.HOURLY,ts.TimeseriesInterval.DAILY,ts.TimeseriesInterval.WEEKLY,ts.TimeseriesInterval.MONTHLY]

st.title(f"AAVE V2 {TOKEN_SYMBOL} Deposits")
date_range = st.date_input(
    "Date range",
    (
        datetime.date.today() - datetime.timedelta(days=7),
        datetime.date.today() - datetime.timedelta(days=3),
    ),
)
print(f'DATES: {len(date_range)}')
if not len(date_range) == 2:
    print('DATE IS NOT SELECTED')
    st.markdown('*Please complete date selection.*')
    st.stop()


START_TIMESTAMP = int(time.mktime(date_range[0].timetuple()))
END_TIMESTAMP = int(time.mktime(date_range[1].timetuple()))
url_aave_subgraph = "https://api.thegraph.com/subgraphs/name/aave/protocol-v2"
query_aave = """
{
    deposits(
        where:{timestamp_gt:%s, timestamp_lt:%s}
        orderBy: timestamp
        orderDirection: asc
        bypassPagination: true
    ) {
        reserve {
            symbol,
            name,
            decimals
        }
        amount
        timestamp
    }
}
""" % (
    START_TIMESTAMP,
    END_TIMESTAMP,
)

def get_rates_df(symbol, start_timestamp, end_timestamp):
    pricing =cp.load_historical_data(symbol, 'USD', start_timestamp, end_timestamp, '163b4f02ba446862200ecf7a64c3359b6d6bcf9d417aa27a0b5b29c9f9e619be', 2000)
    rates = []
    for p in pricing:
        rates.append({"rate": p["close"], "time": pd.to_datetime(p['time'], unit='s')})
    return DataFrame(rates).set_index('time') 


@st.cache(show_spinner=False)
def get_eth_deposits():
    data = gl.load_subgraph(url_aave_subgraph, query_aave)
    deposits = data["data"]["deposits"]
    _eth_deposits = []
    for d in deposits:
        if d["reserve"]["symbol"] == TOKEN_SYMBOL:
            _eth_deposits.append(
                {
                    "amount": float(d["amount"]) / math.pow(10, int(d["reserve"]["decimals"])),
                    "time": d["timestamp"],
                }
            )
    return _eth_deposits

@st.cache(show_spinner=False)
def process_deposits(deposits, df_rates):
    df_hourly = ts.aggregate_timeseries(
        data=deposits, 
        time_column="time", 
        interval=ts.TimeseriesInterval.HOURLY, 
        columns=[ts.ColumnConfig(name="amount", aggregate_method=ts.AggregateMethod.SUM, na_fill_value=0.0)]
    )

    df_hourly = df_hourly.merge(
        df_rates, left_index=True, right_index=True
    )
    df_hourly["volume"] = df_hourly["amount"] * df_hourly["rate"]
    result = {}
    for p in PERIODS:
        df = ts.aggregate_timeseries(
            data=df_hourly, 
            time_column="time", 
            interval=p,
            columns=[
                ts.ColumnConfig(name="amount", aggregate_method=ts.AggregateMethod.SUM, na_fill_value=0.0),
                ts.ColumnConfig(name="volume", aggregate_method=ts.AggregateMethod.SUM, na_fill_value=0.0),
                ts.ColumnConfig(name="rate", aggregate_method=ts.AggregateMethod.LAST, na_fill_method=ts.NaInterpolationMethod.FORDWARD_FILL),
            ],
            start_timestamp=START_TIMESTAMP,
            end_timestamp=END_TIMESTAMP
            
        )
        result[p] = df
    return result

with st.spinner("Loading and processing rates data"):
    df_rates = get_rates_df(TOKEN_SYMBOL_PRICING, START_TIMESTAMP, END_TIMESTAMP)

with st.spinner("Loading deposits data"):
    eth_deposits = get_eth_deposits()

with st.spinner("Loading and aggregating deposit data"):
    dfs = process_deposits(eth_deposits, df_rates)
    for p in dfs.keys():
        st.subheader(p)
        df = dfs[p]
        
        plot_line(
            df,
            x={
                'field':'time', 
                # 'title':'Time'
            },
            ys=[
                {
                    "field": "amount",
                    "title": "Amount",
                    # "scale": Scale(zero=True),  # Example of disabling zoom-to-fit
                },
                {
                    "field": "rate",
                    "title": "Rate",
                },
                {
                    "field": "volume",
                    "title": "Volume",
                },
            ],
        )

        if len(df) > 1:
            coeff = df['amount'].corr(df['rate'])
            flash_card(
                "coefficient between `amount` and `rate`",
                primary_text=0.1,
                formatter="0,0.00a",
                key=f"normal{p}",
            )