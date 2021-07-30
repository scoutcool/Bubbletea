import time
import bubbletea
import os
import datetime
import streamlit as st


from dotenv import load_dotenv

load_dotenv()

try:
    # Hack to avoid streamlit exception
    st.set_page_config(page_title="Demo 2", layout="wide")
except:
    pass

urlvars = bubbletea.parse_url_var(
    [{"key": "startdate", "type": "datetime"}, {"key": "enddate", "type": "datetime"}]
)

try:
    end_date = urlvars["enddate"]
except KeyError:
    end_date = datetime.date.today() - datetime.timedelta(days=0)

try:
    start_date = urlvars["startdate"]
except KeyError:
    start_date = end_date - datetime.timedelta(days=7)

bubbletea.update_url({"startdate": start_date, "enddate": end_date})

start_timestamp = int(time.mktime(start_date.timetuple()))
end_timestamp = int(time.mktime(end_date.timetuple()))

# # # # # # # # # # # # # # # # #
# Load data from AAVE subgraph  #
# # # # # # # # # # # # # # # # #
url_aave_subgraph = "https://api.thegraph.com/subgraphs/name/aave/protocol-v2"
query_aave = """
{
    deposits(
        where:{timestamp_gte:%s, timestamp_lt:%s}
        orderBy: timestamp
        orderDirection: asc
        bypassPagination: true
    ) {
        amount
        timestamp
        reserve {
            symbol
            decimals
        }
    }
}
""" % (
    start_timestamp,
    end_timestamp,
)

data_aave = bubbletea.load_subgraph(url_aave_subgraph, query_aave)
data_aave = data_aave["deposits"]
data_aave = data_aave[
    data_aave["reserve.symbol"] == "AAVE"
]  # Only show deposits with AAVE tokens
data_hourly_aave = bubbletea.aggregate_timeseries(  # aggregate deposits data by hours
    data_aave,
    time_column="timestamp",
    interval=bubbletea.TimeseriesInterval.HOURLY,
    columns=[
        bubbletea.ColumnConfig(
            name="amount",
            aggregate_method=bubbletea.AggregateMethod.SUM,
            na_fill_value=0.0,
        )
    ],
)
data_hourly_aave["amount"] = (
    data_hourly_aave["amount"] / 1000000000000000000
)  # Divided by 18 decimals

# # # # # # # # # # # # # # # # # # # # # # #
# Load pricing data from cryptocompare.com  #
# # # # # # # # # # # # # # # # # # # # # # #
CP_API_TOKEN = os.environ.get("cp_api_token")
pricing_df = bubbletea.load_historical_data(
    "AAVE", "USD", start_timestamp, end_timestamp, CP_API_TOKEN, 2000
)

# # # # # # # # # # # # # # # # # # # # # # #
# merge the aave subgraph and pricing data  #
# # # # # # # # # # # # # # # # # # # # # # #
result = data_hourly_aave.merge(pricing_df, left_index=True, right_on="time")

# # # # # # # # # # # # # # # # #
# Draw the data on a line chart #
# # # # # # # # # # # # # # # # #
bubbletea.plot_line(
    title="Hourly AAVE Deposits vs Pricing",
    df=result,
    x={"title": "Time", "field": "time"},
    yLeft=[{"title": "Price", "field": "close"}],
    yRight=[{"title": "Amount", "field": "amount"}],
)

# # # # # # # # # # # # # # # # #
# Draw the data on a area chart #
# # # # # # # # # # # # # # # # #
bubbletea.plot_area(
    title="Hourly AAVE Deposits vs Pricing",
    df=result,
    x={"title": "Time", "field": "time"},
    yLeft=[{"title": "Price", "field": "close"}],
    yRight=[{"title": "Amount", "field": "amount"}],
)

# # # # # # # # # # # # # # # # #
# Draw the data on a bar chart #
# # # # # # # # # # # # # # # # #
bubbletea.plot_bar(
    title="Hourly AAVE Deposits vs Pricing",
    df=result,
    x={"title": "Time", "field": "time"},
    yLeft=[{"title": "Price", "field": "close"}],
    yRight=[{"title": "Amount", "field": "amount"}],
)