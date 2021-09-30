import time
import math
import bubbletea
import streamlit as st


from dotenv import load_dotenv

load_dotenv()


st.header("OPEN SEA ")
end_timestamp = math.floor(time.time())

# end_timestamp = 1633020435
start_timestamp = end_timestamp - 43200



#Load txs

placeholder = st.empty()
def on_progress(obj):
    msg = f"{obj['transferEvents']} txs loaded."
    placeholder.text(msg)
    
subgraph_url = "https://api.studio.thegraph.com/query/8794/nft/0.0.19"
query = """
{
transferEvents(where:{timestamp_gte:%s, timestamp_lt:%s, txEth_gt:0}, bypassPagination:true) {
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
    df = bubbletea.beta_load_subgraph(subgraph_url, query)
df = df['transferEvents']
df['txEth'] /= 1000000000
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

st.subheader("12H")
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


st.subheader("Top NFTs")

df_c = df_c.rename(columns={'contract.name':'contract'})
df_c["contract_url"] = "https://etherscan.io/address/" + df_c.index
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
    pageSize=10,
)