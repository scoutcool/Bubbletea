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
# df_aave_flashloans_by_date['date'] = = df_aave_flashloans_by_date['date'].apply(lambda x: pd.to_datetime(math.floor(x / 86400) * 86400, unit='s'))
df_aave_flashloans_by_date = df_aave_flashloans_by_date.rename(columns={'date':'date'}).set_index('date')


if st.checkbox('Display data: number of txs by day'):
    st.write(df_aave_flashloans_by_date)

st.line_chart(df_aave_flashloans_by_date)



# st.subheader('Histogram: number of flashloans by day')
# max_date = df_aave_flashloans['timestamp'][0]
# min_date = df_aave_flashloans['timestamp'][len(df_aave_flashloans)-1]
# number_of_bins = math.ceil(max_date / 86400) - math.floor(min_date/86400)

# hist_values = np.histogram(df_aave_flashloans.timestamp / 86400, bins=number_of_bins)[0]
# st.bar_chart(hist_values)