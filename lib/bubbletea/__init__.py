import streamlit as st
from . import thegraph
from . import cryptocompare as cp
from .transformers import urlparser
from .transformers import timeseries as ts
from .charts import line as line
from .charts import area as area
from .charts import bar as bar
from .charts import combo as combo
from flash_card import flash_card
import altair as alt

# CSS hack to hide menu from streamlit
st.markdown(
    """ <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style> """,
    unsafe_allow_html=True,
)

TimeseriesInterval = ts.TimeseriesInterval
AggregateMethod = ts.AggregateMethod
NaInterpolationMethod = ts.NaInterpolationMethod
ColumnType = ts.ColumnType
ColumnConfig = ts.ColumnConfig
SubgraphDef = thegraph.SubgraphDef
beta_aggregate_groupby = ts.beta_aggregate_groupby
beta_aggregate_timeseries = ts.beta_aggregate_timeseries

beta_load_subgraph = thegraph.beta_load_subgraph
beta_load_subgraphs = thegraph.beta_load_subgraphs

beta_load_historical_data = cp.beta_load_historical_data

beta_plot_line = line.plot
beta_plot_bar = bar.plot
beta_plot_area = area.plot
beta_plot_combo = combo.plot
beta_plot_text = flash_card

parse_url_var = urlparser.parse_url_var
update_url = urlparser.update_url


alt.renderers.set_embed_options(actions=False)
