import bubbletea
import streamlit as st
from datetime import datetime
import pandas as pd
import altair as alt


urlvars = bubbletea.parse_url_var([{'key':'starttimestamp','type':'int'}, {'key':'endtimestamp','type':'int'}])
try:
    end_timestamp = urlvars['endtimestamp']
except KeyError:
    end_timestamp = 1630648800

try:
    start_timestamp = urlvars['starttimestamp']
except KeyError:
    start_timestamp = end_timestamp - 21600

bubbletea.update_url({'starttimestamp': start_timestamp, 'endtimestamp': end_timestamp})

st.header(f"ERC721 Transfer Stats")
st.markdown(f"Query this [subgraph](https://thegraph.com/studio/subgraph/os_erc721/). From _{datetime.fromtimestamp(start_timestamp)}_ to _{datetime.fromtimestamp(end_timestamp)}_")


placeholder = st.empty()
def on_subgraph_progress(obj):
    msg = f"{obj['transferEvents']} transferEvents loaded."
    placeholder.text(msg)

def query_subgraph():
    subgraph_url = "https://api.studio.thegraph.com/query/702/os_erc721/0.0.1"
    query = """
    {
    transferEvents(where:{timestamp_gte:%s, timestamp_lt:%s, txEth_gt:0}, bypassPagination:true) {
    timestamp
    txEth
    txHash
    contract{
        address
        name
    }
    }}
    """ % (start_timestamp, end_timestamp)
    return bubbletea.beta_load_subgraph(subgraph_url, query, on_subgraph_progress)

with st.spinner("Querying subgraph"):
    df_raw = query_subgraph()
df = df_raw['transferEvents']
if(len(df) == 0):
    st.warning(f"No data available.")
    pass

df['txEth'] /= 1000000000

if st.checkbox("Display transfer data"):
    st.write(df)

df = bubbletea.beta_aggregate_groupby(
    df,
    by_column="txHash",
    columns=[
        bubbletea.ColumnConfig(
            name="txEth",
            aggregate_method=bubbletea.AggregateMethod.LAST,
            na_fill_value=0.0,
        ),
        bubbletea.ColumnConfig(
            name="timestamp",
            aggregate_method=bubbletea.AggregateMethod.LAST,
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

st.subheader("Hourly Volume and Txs Count")
df_period = bubbletea.beta_aggregate_timeseries(
    df,
    'timestamp',
    interval=bubbletea.TimeseriesInterval.HOURLY,
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
df_period = df_period.rename(columns={"txEth_x":"ETH", "txEth_y":"Tx Count"})
df_period.index.names = ['timestamp']

if st.checkbox("Display hourly data"):
    st.write(df_period)
    
bubbletea.beta_plot_combo(
    df_period,
    x={
        "field": "timestamp",
    },
    yLeft={
        "title": "Volume",
        "stack": False,
        "marker": bubbletea.line.MARKER,
        "data": [
            {"title": "Volume", "field": "eth_volume"}
        ],
        "scale": alt.Scale(zero=False),
    },
    yRight = {
        "title": "Txs Count",
        "stack": False,
        "marker": bubbletea.line.MARKER,
        "data": [
            {"title": "Txs Count", "field": "tx_count"}
        ],
        "scale": alt.Scale(zero=False),
    },
    legend="none",
)


df_c = bubbletea.beta_aggregate_groupby(
    df,
    by_column="contract.address",
    columns=[
        bubbletea.ColumnConfig(
            name="contract.name", 
            aggregate_method=bubbletea.AggregateMethod.LAST
        ),
        bubbletea.ColumnConfig(
            name="txEth", 
            alias="eth_min",
            aggregate_method=bubbletea.AggregateMethod.MIN,
            na_fill_value=0.0,
        ),
        bubbletea.ColumnConfig(
            name="txEth", 
            alias="eth_max",
            aggregate_method=bubbletea.AggregateMethod.MAX,
            na_fill_value=0.0,
        ),
        bubbletea.ColumnConfig(
            name="txEth", 
            alias="eth_mean",
            aggregate_method=bubbletea.AggregateMethod.MEAN,
            na_fill_value=0.0,
        ),
        bubbletea.ColumnConfig(
            name="txEth", 
            alias="eth_sum",
            aggregate_method=bubbletea.AggregateMethod.SUM,
            na_fill_value=0.0,
        ),
        bubbletea.ColumnConfig(
            name="txEth",
            alias="tx_count",
            aggregate_method=bubbletea.AggregateMethod.COUNT,
            na_fill_value=0.0,
        )
    ],
)


st.subheader("Top Tokens")

df_c = df_c.rename(columns={'contract.name':'contract'})
df_c["contract_url"] = "https://etherscan.io/address/" + df_c.index
df_c = df_c.sort_values(by=['eth_sum', 'tx_count'], ascending=False)

if st.checkbox("Display by-collection data"):
    st.write(df_c)

bubbletea.beta_plot_table(
    df_c,
    [
        {
            "field": "contract", 
            "headerName": "Contract",
            "href": "contract_url",
        },
        {
            "field": "eth_sum",
            "headerName": "Volume (ETH)",
            "valueFormatter": 'Math.floor(value).toString().replace(/(\\d)(?=(\\d{3})+(?!\\d))/g, "$1,")',
        },
        {
            "field": "tx_count",
            "headerName": "# Txs",
        },
        {
            "field": "eth_max",
            "headerName": "Max Price (ETH)",
            "valueFormatter": 'Math.floor(value).toString().replace(/(\\d)(?=(\\d{3})+(?!\\d))/g, "$1,")',
        },
        {
            "field": "eth_min",
            "headerName": "Min Price (ETH)",
            "valueFormatter": 'Math.floor(value).toString().replace(/(\\d)(?=(\\d{3})+(?!\\d))/g, "$1,")',
        },
        {
            "field": "eth_mean",
            "headerName": "Avg Price (ETH)",
            "valueFormatter": 'Math.floor(value).toString().replace(/(\\d)(?=(\\d{3})+(?!\\d))/g, "$1,")',
        },
    ],
    pageSize=20,
)