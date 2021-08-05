import bubbletea
import streamlit as st
import pandas as pd
import datetime
import time
import os
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
# subgraph_url = f"https://gateway.thegraph.com/api/{THEGRAPH_APIKEY}/subgraphs/id/0x4bb4c1b0745ef7b4642feeccd0740dec417ca0a0-0"
subgraph_url = "https://api.thegraph.com/subgraphs/name/sushiswap/exchange"

def get_tokens_24h():
    t_now = 1628182953
    # t_now = math.floor(datetime.datetime.now().timestamp())
    t_24hago = t_now - 86400
    query = """{
        tokens(
            bypassPagination:True
        ){
            symbol
            liquidity
            derivedETH
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
        liquidityPositionSnapshots(
            where:{timestamp_gte:%s, timestamp_lt:%s},
            bypassPagination:True
        ){
            # liquidityPosition
            timestamp
            
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
            reserveUSD
            liquidityTokenTotalSupply
            liquidityTokenBalance
        }
    }""" % (t_24hago, t_now, t_24hago, t_now)
    # print(query)
    data = bubbletea.load_subgraph(subgraph_url, query)
    return data
data_tokens_24h = get_tokens_24h()
df_tokens = data_tokens_24h['tokens']
df_tokens['liquidity'] = df_tokens['liquidity'] * df_tokens['derivedETH']
df_24h_hour = data_tokens_24h['pairHourDatas']
# df_24h_mints = data_tokens_24h['mints']
df_24h_ls = data_tokens_24h['liquidityPositionSnapshots']
st.subheader('TOKENS')
st.write(df_tokens)

st.subheader('USDC')
# filter by USDC
df_tokens = df_tokens[df_tokens['symbol'] == 'USDC']
st.write(df_tokens)
df_24h_hour = df_24h_hour[(df_24h_hour['pair.token0.symbol'] == 'USDC') | (df_24h_hour['pair.token1.symbol'] == 'USDC')]
# df_24h_mints = df_24h_mints[(df_24h_mints['pair.token0.symbol'] == 'USDC') | (df_24h_mints['pair.token1.symbol'] == 'USDC')]
df_24h_ls = df_24h_ls[(df_24h_ls['pair.token0.symbol'] == 'USDC') | (df_24h_ls['pair.token1.symbol'] == 'USDC')]

df_24h_ls['pair'] = df_24h_ls['pair.token0.symbol']+df_24h_ls['pair.token1.symbol']
df_24h_ls.sort_values(by=['timestamp'], ascending=False)
df_24h_ls = df_24h_ls.groupby('pair').agg({'reserveUSD':['first','last'],'liquidityTokenTotalSupply':['first','last'], 'liquidityTokenBalance':['first','last']})
df_detla = df_24h_ls.iloc[:, 0] - df_24h_ls.iloc[:, 1]
st.write(df_detla)


st.subheader('24H USDC')
st.write(df_24h_hour)
st.write(df_24h_ls)

volume_24h = df_24h_hour['volumeUSD'].sum()
volume_24h_display = "{:,}".format(volume_24h)
fee_24h_display = "{:,}".format(volume_24h * 0.3)

liquidity_24h = df_detla.iloc[:, 0].sum()
liquidity_24h_display = "{:,}".format(liquidity_24h * 0.3)

c0,c1,c2 = st.beta_columns([1,1,1])
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
        f"""#### Liquidity
            {liquidity_24h_display}
        """)



# df_24h.sort_values(by=['date'], ascending=True)
# st.write(df_24h)


# bubbletea.plot_text("24H Volume", primary_text=0.1, formatter="0,0.00a", key=f"normal{volume_24h}")
# df = get_token_day_data('tokenHourDatas')
# st.write(df)
# df = df[df['token.symbol'] == 'USDC']
# st.write(df)

# query = """
# {
#   pairHourDatas(
#     where:{date_gte:%s, date_lt:%s}
#     bypassPagination: True
#   ){
#     date
#     pair{
#       token0{
#         symbol
#       }
#       token1{
#         symbol
#       }
#     }
#     volumeUSD
#     volumeToken0
#     volumeToken1
#   }
# }
# """ % (
#     start_timestamp,
#     end_timestamp,
# )

# df = get_token_day_data('pairHourDatas')
# st.write(df)
# df1 = df[df['pair.token0.symbol'] == 'USDC']
# t1 = df1['volumeToken0'].sum()
# df2 = df[df['pair.token1.symbol'] == 'USDC']
# t2 = df2['volumeToken1'].sum()
# total = t1+t2
# st.write(total)

# df = pd.concat([df1, df2])
# total = df['volumeUSD'].sum()
# st.write(total)