import os, sys
import pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import datetime
import streamlit as st
import time
from lib import bubbletea

st.header("OPEN SEA ")


urlvars = bubbletea.parse_url_var([{'key':'startdate','type':'datetime'}, {'key':'enddate','type':'datetime'}])

try:
    end_date = urlvars['enddate']
except KeyError:
    end_date = datetime.date.today() - datetime.timedelta(days=0)

try:
    start_date = urlvars['startdate']
except KeyError:
    start_date = end_date - datetime.timedelta(days=3)

date_range = st.date_input("Date range", (start_date, end_date))

if not len(date_range) == 2:
    st.warning("*Please select a date range.*")
    st.stop()

start_date = date_range[0]
end_date = date_range[1]

start_timestamp = int(time.mktime(start_date.timetuple()))
end_timestamp = int(time.mktime(end_date.timetuple()))

bubbletea.update_url({'startdate': start_date, 'enddate':end_date})

#Load txs

subgraph_url = "https://api.studio.thegraph.com/query/8794/nft/0.0.19"
query = """
{
transferEvents(where:{timestamp_gte:%s, timestamp_lt:%s}) {
  id
  timestamp
  txEth
  txHash
  contract{
    address
    name
  }
}}
""" % (start_timestamp, end_timestamp)

with st.spinner("Loading txs"):
    df = bubbletea.beta_load_subgraph(subgraph_url, query, useBigDecimal=True)
df = df['transferEvents']
df['txEth'] /= 1000000000
st.write(df)

df = bubbletea.beta_aggregate_groupby(
    df,
    by_column="txHash",
    columns=[
        bubbletea.ColumnConfig(
            name="txEth",
            type=bubbletea.ColumnType.int,
            aggregate_method=bubbletea.AggregateMethod.LAST,
            na_fill_value=0.0,
        ),
        bubbletea.ColumnConfig(
            name="timestamp",
            aggregate_method=bubbletea.AggregateMethod.LAST,
            # na_fill_value=0.0,
        ),
        bubbletea.ColumnConfig(
            name="contract.name",
            aggregate_method=bubbletea.AggregateMethod.LAST,
        ),
        bubbletea.ColumnConfig(
            name="contract.address",
            aggregate_method=bubbletea.AggregateMethod.LAST,
        )
    ],
)

df['timestamp'] = df['timestamp'].apply(lambda x: pd.to_datetime(int(x), unit='s'))

st.subheader("NFT Txs Daily Volume")
df_daily = bubbletea.beta_aggregate_timeseries(
    df,
    'timestamp',
    interval=bubbletea.TimeseriesInterval.DAILY,
    columns=[
        bubbletea.ColumnConfig(
            name='txEth',
            alias='eth_volume',
            aggregate_method=bubbletea.AggregateMethod.SUM,
            na_fill_value=0.0
        ),
        bubbletea.ColumnConfig(
            name='txEth',
            alias='tx_count',
            aggregate_method=bubbletea.AggregateMethod.COUNT,
            na_fill_value=0.0
        )
    ]
)
df_daily = df_daily.rename(columns={"txEth_x":"ETH", "txEth_y":"Tx Count"})
st.write(df_daily)


st.subheader("NFT Txs Volume By Contract")
df_c = bubbletea.beta_aggregate_groupby(
    df,
    by_column="contract.address",
    columns=[
        bubbletea.ColumnConfig(
            name="contract.name", 
            type=bubbletea.ColumnType.int,
            aggregate_method=bubbletea.AggregateMethod.LAST
        ),
        bubbletea.ColumnConfig(
            name="txEth", 
            alias="eth_min",
            type=bubbletea.ColumnType.int,
            aggregate_method=bubbletea.AggregateMethod.MIN,
            na_fill_value=0.0,
        ),
        bubbletea.ColumnConfig(
            name="txEth", 
            alias="eth_max",
            type=bubbletea.ColumnType.int,
            aggregate_method=bubbletea.AggregateMethod.MAX,
            na_fill_value=0.0,
        ),
        bubbletea.ColumnConfig(
            name="txEth", 
            alias="eth_mean",
            type=bubbletea.ColumnType.int,
            aggregate_method=bubbletea.AggregateMethod.MEAN,
            na_fill_value=0.0,
        ),
        bubbletea.ColumnConfig(
            name="txEth", 
            alias="eth_median",
            type=bubbletea.ColumnType.int,
            aggregate_method=bubbletea.AggregateMethod.MEDIAN,
            na_fill_value=0.0,
        ),
        bubbletea.ColumnConfig(
            name="txEth", 
            alias="eth_sum",
            type=bubbletea.ColumnType.int,
            aggregate_method=bubbletea.AggregateMethod.SUM,
            na_fill_value=0.0,
        ),
        bubbletea.ColumnConfig(
            name="txEth",
            alias="tx_count",
            aggregate_method=bubbletea.AggregateMethod.COUNT,
            # na_fill_value=0.0,
        )
    ],
)

st.subheader("aggregate_methods")
st.write(df_c)

# df_c1 = bubbletea.beta_aggregate_groupby(
#     df,
#     by_column="contract.address",
#     columns=[
#         bubbletea.ColumnConfig(
#             name="txEth", 
#             type=bubbletea.ColumnType.int,
#             aggregate_method=bubbletea.AggregateMethod.MAX,
#             na_fill_value=0.0,
#         )
#     ],
# )
# st.subheader('df_c1')
# st.write(df_c1)
# df_c1 = df_c1.reset_index()

# df_c = pd.merge(df_c, df_c1, on='contract.address', how="outer")
# st.subheader('merged')
# st.write(df_c)

# df_c2 = bubbletea.beta_aggregate_groupby(
#     df,
#     by_column="contract.address",
#     columns=[
#         bubbletea.ColumnConfig(
#             name="txEth", 
#             type=bubbletea.ColumnType.int,
#             aggregate_method=bubbletea.AggregateMethod.MIN,
#             na_fill_value=0.0,
#         )
#     ],
# )
# df_c3 = bubbletea.beta_aggregate_groupby(
#     df,
#     by_column="contract.address",
#     columns=[
#         bubbletea.ColumnConfig(
#             name="txEth", 
#             type=bubbletea.ColumnType.int,
#             aggregate_method=bubbletea.AggregateMethod.MEAN,
#             na_fill_value=0.0,
#         )
#     ],
# )
# df_c4 = bubbletea.beta_aggregate_groupby(
#     df,
#     by_column="contract.address",
#     columns=[
#         bubbletea.ColumnConfig(
#             name="txEth", 
#             type=bubbletea.ColumnType.int,
#             aggregate_method=bubbletea.AggregateMethod.MEDIAN,
#             na_fill_value=0.0,
#         )
#     ],
# )

# df_c = df_c.reset_index()
# df_c['contract_url'] = df_c
# df_c = df_c.rename(columns={'contract.name':'contract'})

# bubbletea.beta_plot_table(
#     df_c,
#     [
#         {"field": "contract", "headerName": "Contract"},
#         {
#             "field": "txEth",
#             "headerName": "ETH",
#             "valueFormatter": 'Math.floor(value).toString().replace(/(\\d)(?=(\\d{3})+(?!\\d))/g, "$1,")',
#         },
#         {
#             "field": "timestamp",
#             "headerName": "Tx Count",
#             # "href": "tx_url",
#         },
#     ],
#     pageSize=10,
# )
