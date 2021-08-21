from pandas.core.tools.datetimes import to_datetime
import streamlit as st
import math
import requests
import json
import pandas as pd
from enum import Enum

_URL_HIST_PRICE_DAY = 'https://min-api.cryptocompare.com/data/histoday'
_URL_HIST_PRICE_HOUR = 'https://min-api.cryptocompare.com/data/histohour'
_URL_HIST_PRICE_MINUTE = 'https://min-api.cryptocompare.com/data/histominute'

@st.cache(show_spinner=False)
def _load_historical_data(url:str):
    response = requests.get(url)
    text = json.loads(response.text)
    if text["Response"] == "Error":
        raise ValueError(text["Message"])
    return text["Data"]


def beta_load_historical_data(from_symbol:str, to_symbol:str, start_timestamp:int, end_timestamp:int, apikey:str, apilimit:int=2000, interval='H', exchange='CCCAGG'):
    interval = interval.lower()
    if apikey == None:
        raise ValueError('CryptoCompare API KEY is not provided. If you don\'t have have, get it here https://min-api.cryptocompare.com/')
    if interval == 'h':
        url = _URL_HIST_PRICE_HOUR
        interval_in_seconds = 3600
    elif interval == 'd':
        url = _URL_HIST_PRICE_DAY
        interval_in_seconds = 86400
    elif interval in ['t', 'min']:
        url = _URL_HIST_PRICE_MINUTE
        interval_in_seconds = 60
    else:
        raise ValueError('Interval must be one of `H` for hour, `D` for day, `min` for minute.')
    
    etime = math.ceil(end_timestamp / interval_in_seconds) * interval_in_seconds
    stime = math.floor(start_timestamp / interval_in_seconds) * interval_in_seconds
    limit = math.ceil((etime - stime) / interval_in_seconds)
    rates = []
    et = etime
    while et > start_timestamp:
        st = max(et - interval_in_seconds * apilimit, stime)
        l = (apilimit - 1) if limit > apilimit else limit
        iurl = f"{url}?fsym={from_symbol}&tsym={to_symbol}&limit={l}&aggregate=1&e={exchange}&api_key={apikey}&toTs={etime}"
        rs = _load_historical_data(iurl)
        rates.extend(rs)
        # print(f'{len(rates)}\t{iurl}')
        limit -= apilimit
        et = st
    df = pd.json_normalize(rates)
    df['time'] = df['time'].apply(lambda x: to_datetime(x, unit='s'))
    df.sort_values(by=['time'], ascending=True)
    return df