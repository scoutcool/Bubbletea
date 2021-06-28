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

def load_historical_data(from_symbol:str, to_symbol:str, startTimestamp:int, endTimestamp:int, apikey:str, apiLimit:int=2000):
    if apikey == None:
        raise ValueError('CryptoCompare API KEY is not provided. If you don\'t have have, get it here https://min-api.cryptocompare.com/')
    etime = math.ceil(endTimestamp / 86400) * 86400
    stime = math.floor(startTimestamp / 86400) * 86400
    limit = math.ceil((etime - stime) / 3600)
    # print(f'load_historical_data limit {limit}')
    et = etime
    rates = []
    while et > startTimestamp:
        st = max(et - 3600 * apiLimit, stime)
        l = (apiLimit - 1) if limit > apiLimit else limit
        rs = _load_historical_data(from_symbol, to_symbol, st, et, l, apikey)
        rates.extend(rs)
        limit -= apiLimit
        et = st
    
    rates.sort(key=lambda x: float(x['time']), reverse=False)
    return rates