from earlgrey.thegraph import loader as gl
from earlgrey.transformers import timeseries as ts
from earlgrey import crypto_compare as cp
from earlgrey.charts.line import plot as plot_line
import streamlit as st
import datetime
import time
import os
from earlgrey.transformers import urlparser as urlparser

from flash_card import flash_card


urlvars = urlparser.parse_url_var([{'key':'startdate','type':'datetime'}, {'key':'enddate','type':'datetime'}])

try:
    end_date = urlvars['enddate']
except KeyError:
    end_date = datetime.date.today() - datetime.timedelta(days=0)

try:
    start_date = urlvars['startdate']
except KeyError:
    start_date = end_date - datetime.timedelta(days=7)


CP_API_TOKEN = os.environ.get("cp_api_token")
TOKENS = ["AAVE", "ETH", "USDC", "WBTC"]
token_symbol = TOKENS[0]
token_symbol_cp = TOKENS[0]


st.title(f"AAVE V2 {token_symbol} Deposits")
token_symbol_cp = st.selectbox("Select a token", TOKENS)
if token_symbol_cp == "ETH":
    token_symbol = "WETH"


date_range = st.date_input("Date range", (start_date, end_date))

if not len(date_range) == 2:
    st.warning("*Please select a date range.*")
    st.stop()

start_timestamp = int(time.mktime(date_range[0].timetuple()))
end_timestamp = int(time.mktime(date_range[1].timetuple()))

INTERVALS = {
    ts.TimeseriesInterval.HOURLY: "Hourly",
    ts.TimeseriesInterval.DAILY: "Daily",
    ts.TimeseriesInterval.WEEKLY: "Weekly",
    ts.TimeseriesInterval.MONTHLY: "Monthly",
}
interval = st.selectbox(
    "Set aggregation frequency",
    options=list(INTERVALS.keys()),
    format_func=lambda x: INTERVALS[x],
    index=1,
)


subgraph_url = "https://api.thegraph.com/subgraphs/name/aave/protocol-v2"
query = """
{
    deposits(
        where:{timestamp_gte:%s, timestamp_lt:%s}
        orderBy: timestamp
        orderDirection: asc
        bypassPagination: true
    ) {
        reserve {
            symbol,
            decimals
        }
        amount
        timestamp
    }
}
""" % (
    start_timestamp,
    end_timestamp,
)

def get_rates_df(symbol, start_timestamp, end_timestamp):
    df = cp.load_historical_data(
        symbol, "USD", start_timestamp, end_timestamp, CP_API_TOKEN, 2000
    )
    df['rate'] = df['close']
    return df.set_index('time')

placeholder = st.empty()
def on_deposits_progress(obj):
    msg = f"{obj['count']} {obj['entity']} loaded."
    placeholder.text(msg)


def get_token_deposits():
    data = gl.load_subgraph(subgraph_url, query, on_deposits_progress)
    df = data["data"]["deposits"]
    df = df[df['reserve.symbol'] == token_symbol] #Filter rows where reserve.symbol == selected symbol
    df['amount'] = df['amount'] / (10 ** df['reserve.decimals'])
    return df

@st.cache(show_spinner=False)
def process_deposits(df_deposits, df_rates):
    df_hourly = ts.aggregate_timeseries(
        data=df_deposits,
        time_column="timestamp",
        interval=ts.TimeseriesInterval.HOURLY,
        columns=[
            ts.ColumnConfig(
                name="amount",
                aggregate_method=ts.AggregateMethod.SUM,
                na_fill_value=0.0,
            )
        ],
    )

    df_hourly = df_hourly.merge(df_rates, left_index=True, right_index=True)
    df_hourly["volume"] = df_hourly["amount"] * df_hourly["rate"]
    df_hourly.index.names = ['timestamp']
    result = {}

    df = ts.aggregate_timeseries(
        data=df_hourly,
        time_column="timestamp",
        interval=interval,
        columns=[
            ts.ColumnConfig(
                name="amount",
                aggregate_method=ts.AggregateMethod.SUM,
                na_fill_value=0.0,
            ),
            ts.ColumnConfig(
                name="rate",
                aggregate_method=ts.AggregateMethod.LAST,
                na_fill_method=ts.NaInterpolationMethod.FORDWARD_FILL,
            ),
            ts.ColumnConfig(
                name="volume",
                aggregate_method=ts.AggregateMethod.SUM,
                na_fill_value=0.0,
            ),
        ],
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
    )
    # print(f'after aggregate \n{df}')
    result[interval] = df
    return result


with st.spinner("Loading and processing rates data"):
    df_rates = get_rates_df(token_symbol_cp, start_timestamp, end_timestamp)

with st.spinner("Loading deposits data"):
    df_deposits = get_token_deposits()

with st.spinner("Loading and aggregating deposit data"):
    dfs = process_deposits(df_deposits, df_rates)
    # print(df_rates)
    for p in dfs.keys():
        df = dfs[p]

        plot_line(
            df,
            title=p,
            x={"field": "timestamp", "title": "Time"},
            yLeft=[
                {
                    "field": "amount",
                    "title": "Amount",
                },
                
            ],
            yRight=[
                {
                    "field": "rate",
                    "title": "Rate",
                },
            ],
            legend="right",
        )

        if len(df) > 1:
            coeff = df['amount'].corr(df['rate'])
            flash_card(
                "Coefficient between `amount` and `rate`",
                primary_text=0.1,
                formatter="0,0.00a",
                key=f"normal{p}",
            )
