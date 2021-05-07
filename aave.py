import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import math

startDate = 1609459200
endDate = 1609977600

url_aave_subgraph = 'https://api.thegraph.com/subgraphs/name/aave/protocol'
query_aave_flashloans = """
{
    flashLoans(
      where:{timestamp_gt:%s, timestamp_lt:%s}
        orderBy: timestamp
        orderDirection: desc
        first: 1000
    ) {
    	reserve {
    		id,
            symbol
    	}
        amount
        totalFee
        timestamp
    }
}
""" % (startDate, endDate)

@st.cache
def load_pricing(symbol, startTimestamp, endTimestamp):
    eTime = math.ceil(endTimestamp / 86400) * 86400
    sTime = math.floor(startTimestamp / 86400) * 86400
    limit = math.ceil((eTime - sTime) / 3600)
    url = 'https://min-api.cryptocompare.com/data/histohour?fsym=%s&tsym=USD&limit=%s&aggregate=1&e=CCCAGG&extraParams=scout&api_key=163b4f02ba446862200ecf7a64c3359b6d6bcf9d417aa27a0b5b29c9f9e619be&toTs=%s' % (symbol, limit, eTime)
    response = requests.get(url)
    text = json.loads(response.text)
    return text["Data"]


# def load_pricing_debug(symbol, startTimestamp, endTimestamp):
#     eTime = math.ceil(endTimestamp / 86400) * 86400
#     sTime = math.floor(startTimestamp / 86400) * 86400
#     limit = math.ceil((eTime - sTime) / 3600)
#     url = 'https://min-api.cryptocompare.com/data/histohour?fsym=%s&tsym=USD&limit=%s&aggregate=1&e=CCCAGG&extraParams=scout&api_key=163b4f02ba446862200ecf7a64c3359b6d6bcf9d417aa27a0b5b29c9f9e619be&toTs=%s' % (symbol, limit, eTime)
#     print('??load_pricing_debug url')
#     print(url)
#     response = requests.get(url)
#     text = json.loads(response.text)
#     return text["Data"]

# dai_pricing = load_pricing_debug('DAI', startDate, endDate)
# print(json.dumps(dai_pricing, indent=4))


@st.cache
def load_thegraph(url, query):
    response = requests.post(url, json={'query': query})
    text = json.loads(response.text)
    return text["data"]



st.title('AAVE Flashloans')

st.subheader('Flashloans via the graph')

data_aave_flashloans = load_thegraph(url_aave_subgraph, query_aave_flashloans)
data_aave_flashloans = data_aave_flashloans["flashLoans"]


df_aave_flashloans = pd.json_normalize(data_aave_flashloans)
df_aave_flashloans['date'] = df_aave_flashloans['timestamp'].apply(lambda x: pd.to_datetime(math.floor(x / 86400) * 86400, unit='s'))
st.write(df_aave_flashloans)



st.subheader('Group by reserve')
df_aave_flashloans_by_reserve =  df_aave_flashloans.groupby(['reserve.symbol']).size().reset_index(name='count')
df_aave_flashloans_by_reserve = df_aave_flashloans_by_reserve.rename(columns={'reserve.symbol':'symbol'}).set_index('symbol')


if st.checkbox('Display data: number of txs by reserve'):
    st.write(df_aave_flashloans_by_reserve)

st.bar_chart(df_aave_flashloans_by_reserve)


st.subheader('Group by date')
df_aave_flashloans_by_date =  df_aave_flashloans.groupby(['date']).size().reset_index(name='count')
df_aave_flashloans_by_date['date'] = df_aave_flashloans_by_date['date'].apply(lambda x: x.strftime("%Y/%m/%d"))
df_aave_flashloans_by_date = df_aave_flashloans_by_date.rename(columns={'date':'date'}).set_index('date')


if st.checkbox('Display data: number of txs by day'):
    st.write(df_aave_flashloans_by_date)

st.line_chart(df_aave_flashloans_by_date)



st.subheader('Token rates via CyptoCompare')
symbols = df_aave_flashloans_by_reserve.index.values

token_rates = {}
token_rates = []
for symbol in symbols:
    pricing = load_pricing(symbol, startDate, endDate)
    rates = []
    for p in pricing:
        rates.append({"symbol": symbol, "rate": p["close"], "time": p["time"], "key_symbol_hour": symbol+str(p["time"])})
    
    token_rates += rates

    # token_rates[symbol] = pricing
    df_pricing = pd.json_normalize(pricing)
    if st.checkbox('Display %s rates' % (symbol)):
        st.write(df_pricing)


st.subheader('Volume by Day')
df_token_rates = pd.json_normalize(token_rates)
if st.checkbox('Display flattened rates'):
    st.write(df_token_rates)

df_aave_flashloans['key_symbol_hour'] = df_aave_flashloans['reserve.symbol']+df_aave_flashloans['timestamp'].apply(lambda x: str(math.floor(x/3600) * 3600))
df_aave_flashloans = df_aave_flashloans.merge(df_token_rates)

df_aave_flashloans = df_aave_flashloans.drop(columns=['reserve.id', 'reserve.symbol', 'key_symbol_hour', 'time'])

if st.checkbox('Display joint table: flashloans + rates'):
    st.write(df_aave_flashloans)

df_aave_flashloans_volume = df_aave_flashloans[['date', 'amount', 'totalFee', 'rate']].copy()
df_aave_flashloans_volume['amountUSD'] = df_aave_flashloans_volume.apply(lambda row: float(row['amount']) * float(row['rate']), axis=1)
df_aave_flashloans_volume['feeUSD'] = df_aave_flashloans_volume.apply(lambda row: float(row['totalFee']) * float(row['rate']), axis=1)


df_aave_flashloans_volume_by_date = df_aave_flashloans_volume.drop(columns=['amount', 'rate', 'totalFee'])

df_aave_flashloans_volume_by_date['date'] = df_aave_flashloans_volume_by_date['date'].apply(lambda x: x.strftime("%Y/%m/%d"))

df_aave_flashloans_volume_by_date =  df_aave_flashloans_volume_by_date.groupby(['date']).sum()#.reset_index(name='count')



if st.checkbox('Display daily volume data'):
    st.write(df_aave_flashloans_volume_by_date)
st.area_chart(df_aave_flashloans_volume_by_date)



# st.subheader('Histogram: number of flashloans by day')
# max_date = df_aave_flashloans['timestamp'][0]
# min_date = df_aave_flashloans['timestamp'][len(df_aave_flashloans)-1]
# number_of_bins = math.ceil(max_date / 86400) - math.floor(min_date/86400)

# hist_values = np.histogram(df_aave_flashloans.timestamp / 86400, bins=number_of_bins)[0]
# st.bar_chart(hist_values)