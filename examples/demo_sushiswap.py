from streamlit.caching import cache
import bubbletea
import streamlit as st
import pandas as pd
import datetime
import time
import os
import requests
import json
import math
from dotenv import load_dotenv
load_dotenv()


urlvars = bubbletea.parse_url_var([{'key':'startdate','type':'datetime'}, {'key':'enddate','type':'datetime'}])

try:
    end_date = urlvars['enddate']
except KeyError:
    end_date = datetime.date.today() - datetime.timedelta(days=0)

try:
    start_date = urlvars['startdate']
except KeyError:
    start_date = end_date - datetime.timedelta(days=7)

date_range = st.date_input("Date range", (start_date, end_date))

if not len(date_range) == 2:
    st.warning("*Please select a date range.*")
    st.stop()

start_date = date_range[0]
end_date = date_range[1]
start_timestamp = int(time.mktime(start_date.timetuple()))
end_timestamp = int(time.mktime(end_date.timetuple()))

bubbletea.update_url({'startdate': start_date, 'enddate': end_date})

# THEGRAPH_APIKEY = os.environ.get("thegraph_apikey")
# subgraph_url_exchange = f"https://gateway.thegraph.com/api/{THEGRAPH_APIKEY}/subgraphs/id/0x4bb4c1b0745ef7b4642feeccd0740dec417ca0a0-0"
subgraph_url_exchange = "https://api.thegraph.com/subgraphs/name/sushiswap/exchange"
subgraph_url_bar = "https://api.thegraph.com/subgraphs/name/matthewlilley/bar"

@st.cache(show_spinner=False)
def get_block_no_by_time(timestamp:int):
    apikey = os.environ.get("etherscan_apikey")
    url = f"https://api.etherscan.io/api?module=block&action=getblocknobytime&timestamp={timestamp}&closest=before&apikey={apikey}"
    response = requests.get(url)
    text = json.loads(response.text)
    return int(text["result"])


def get_tokens_24h():
    query = """{
        tokens(
            bypassPagination:True
        ){
            symbol
            liquidity
            derivedETH
        }
        factories {
            id
            volumeUSD
        }
        pairHourDatas(
            where:{date_gte:%s, date_lt:%s}
            bypassPagination: True
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
        }
    }""" % (t_24hago, t_now)
    # print(query)
    data = bubbletea.beta_load_subgraph(subgraph_url_exchange, query)
    return data



# t_now = 1628182953
t_now = math.floor(datetime.datetime.now().timestamp())
t_24hago = t_now - 86400
b_24hago = get_block_no_by_time(t_24hago)

data_tokens_24h = get_tokens_24h()
df_tokens = data_tokens_24h['tokens']
df_tokens['liquidity'] = df_tokens['liquidity'] * df_tokens['derivedETH']
df_24h_hour = data_tokens_24h['pairHourDatas']
st.subheader('TOKENS')
st.write(df_tokens)


@st.cache(show_spinner=False)
def get_factory_at_block(block):
    data = bubbletea.beta_load_subgraph(subgraph_url_exchange,
    """
    {
        factories(block: {number:%s}) {
        id
        volumeUSD
        }
    }
    """ % (block))
    return data['factories']

factory_24h_ago = get_factory_at_block(b_24hago)

facotory_volume_now = data_tokens_24h['factories']['volumeUSD'][0]
facotory_volume_24h_ago = factory_24h_ago['volumeUSD'][0]
print(factory_24h_ago.dtypes)
st.write(facotory_volume_now)
st.write(facotory_volume_24h_ago)

@st.cache(show_spinner=False)
def get_bar():
    data = bubbletea.beta_load_subgraph(subgraph_url_bar, """
    {
        bars{
            ratio
            totalSupply
        }
    }
    """)
    return data['bars']
df_bar = get_bar()


st.subheader('24H')
st.write(df_24h_hour)

volume_24h = df_24h_hour['volumeUSD'].sum()
volume_24h_display = "{:,}".format(volume_24h)
fee_24h_display = "{:,}".format(volume_24h * 0.3)

volume_oneday = facotory_volume_now - facotory_volume_24h_ago
bar_totalsupply = df_bar['totalSupply'][0]
bar_ratio = df_bar['ratio'][0]
apy = volume_oneday * 0.05 * 0.01 / bar_totalsupply / bar_ratio / 9.59
apy_display = "{:,}".format(apy)



c0,c1,c2 = st.columns([1,1,1])
with c0:
    st.markdown(
        f"""#### Volume
            {volume_24h_display}
        """)
with c1:
    st.markdown(
        f"""#### Fees
            {fee_24h_display}
        """)
with c2:
    st.markdown(
        f"""#### APY
            {apy_display}
        """)

