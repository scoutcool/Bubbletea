import streamlit as st
import math
import requests
import json

@st.cache(show_spinner=False)
def _load_historical_data(from_symbol:str, to_symbol:str, stime:int, etime:int, limit:int, apikey:str):
    url = f"https://min-api.cryptocompare.com/data/histohour?fsym={from_symbol}&tsym={to_symbol}&limit={limit}&aggregate=1&e=CCCAGG&extraParams=earlgrey&api_key={apikey}&toTs={etime}"
    response = requests.get(url)
    text = json.loads(response.text)
    return text["Data"]

"""
Load hourly pricing data from crypto compare. 
Parmas:
`from_symbol`: Token symbol. Please check if desired token is supported by crypto compare. For example, `WETH` is not whereas `ETH`.
`to_symbol`: Token or fiat symbol.
`start_timestamp`: Start of time range, in unix timestamp seconds. For example 1609459200 `2021-01-01`
`end_timestamp`: End of time range, in unix timestamp seconds.
`apikey`: API Key from crypto compare. Register [here](https://min-api.cryptocompare.com/)
`apilimit`: Number of data points per request. Default is set to 2000 for crypto compare's free tier. 
"""
def load_historical_data(from_symbol:str, to_symbol:str, start_timestamp:int, end_timestamp:int, apikey:str, apilimit:int=2000):
    if apikey == None:
        raise ValueError('CryptoCompare API KEY is not provided. If you don\'t have have, get it here https://min-api.cryptocompare.com/')
    etime = math.ceil(end_timestamp / 86400) * 86400
    stime = math.floor(start_timestamp / 86400) * 86400
    limit = math.ceil((etime - stime) / 3600)
    # print(f'load_historical_data limit {limit}')
    et = etime
    rates = []
    while et > start_timestamp:
        st = max(et - 3600 * apilimit, stime)
        l = (apilimit - 1) if limit > apilimit else limit
        rs = _load_historical_data(from_symbol, to_symbol, st, et, l, apikey)
        rates.extend(rs)
        limit -= apilimit
        et = st
    
    rates.sort(key=lambda x: float(x['time']), reverse=False)
    return rates