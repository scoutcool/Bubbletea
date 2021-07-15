from altair.vegalite.v4.schema.core import TimeInterval
import streamlit as st
from . import thegraph
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
aggregate_groupby = ts.aggregate_groupby
aggregate_timeseries = ts.aggregate_timeseries

load_subgraph = thegraph.load_subgraph
load_subgraphs = thegraph.load_subgraphs

plot_line = line.plot
plot_text = flash_card

parse_url_var = urlparser.parse_url_var
update_url = urlparser.update_url