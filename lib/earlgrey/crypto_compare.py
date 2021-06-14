import streamlit as st
import math
import requests
import json

@st.cache(show_spinner=False)
def _load_historical_data(fromSymbol:str, toSymbol:str, sTime:int, eTime:int, limit:int, apiKey:str):
    url = f"https://min-api.cryptocompare.com/data/histohour?fsym={fromSymbol}&tsym={toSymbol}&limit={limit}&aggregate=1&e=CCCAGG&extraParams=earlgrey&api_key={apiKey}&toTs={eTime}"
    response = requests.get(url)
    text = json.loads(response.text)
    return text["Data"]

def load_historical_data(fromSymbol:str, toSymbol:str, startTimestamp:int, endTimestamp:int, apiKey:str, apiLimit:int):
    eTime = math.ceil(endTimestamp / 86400) * 86400
    sTime = math.floor(startTimestamp / 86400) * 86400
    limit = math.ceil((eTime - sTime) / 3600)
    print(f'load_historical_data limit {limit}')
    et = eTime
    rates = []
    while et > startTimestamp:
        st = max(et - 3600 * apiLimit, sTime)
        l = (apiLimit - 1) if limit > apiLimit else limit
        rs = _load_historical_data(fromSymbol, toSymbol, st, et, l, apiKey)
        rates.extend(rs)
        limit -= apiLimit
        et = st
    
    rates.sort(key=lambda x: float(x['time']), reverse=False)
    return rates