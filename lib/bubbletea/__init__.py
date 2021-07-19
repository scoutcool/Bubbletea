import streamlit as st
from . import thegraph
from . import crypto_compare as cp
from .transformers import urlparser
from .transformers import timeseries as ts
from .charts import line as line
from flash_card import flash_card

st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

TimeseriesInterval = ts.TimeseriesInterval
AggregateMethod = ts.AggregateMethod
AggregateMethod = ts.AggregateMethod
NaInterpolationMethod = ts.NaInterpolationMethod
ColumnType = ts.ColumnType
ColumnConfig = ts.ColumnConfig
aggregate_groupby = ts.aggregate_groupby
aggregate_timeseries = ts.aggregate_timeseries

load_subgraph = thegraph.load_subgraph
load_subgraphs = thegraph.load_subgraphs
load_historical_data = cp.load_historical_data

plot_line = line.plot
plot_text = flash_card

parse_url_var = urlparser.parse_url_var
update_url = urlparser.update_url