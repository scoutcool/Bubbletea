import bubbletea
import streamlit as st
import pandas as dp
import datetime
import time
import os
import altair as alt

urlvars = bubbletea.parse_url_var([{'key':'startdate','type':'datetime'}, {'key':'enddate','type':'datetime'}])

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

start_date = date_range[0]
end_date = date_range[1]
start_timestamp = int(time.mktime(start_date.timetuple()))
end_timestamp = int(time.mktime(end_date.timetuple()))

bubbletea.update_url({'startdate': start_date, 'enddate': end_date})

INTERVALS = {
    bubbletea.TimeseriesInterval.HOURLY: "Hourly",
    bubbletea.TimeseriesInterval.DAILY: "Daily",
    bubbletea.TimeseriesInterval.WEEKLY: "Weekly",
    bubbletea.TimeseriesInterval.MONTHLY: "Monthly",
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
    df = bubbletea.beta_load_historical_data(
        symbol, "USD", start_timestamp, end_timestamp, CP_API_TOKEN, 2000, 'H'
    )
    df['rate'] = df['close']
    return df.set_index('time')

placeholder = st.empty()
def on_deposits_progress(obj):
    msg = f"{obj['deposits']} deposits loaded."
    placeholder.text(msg)


def get_token_deposits():
    data = bubbletea.beta_load_subgraph(subgraph_url, query, on_deposits_progress)
    df = data["deposits"]
    df = df[df['reserve.symbol'] == token_symbol] #Filter rows where reserve.symbol == selected symbol
    df['amount'] = df['amount'] / (10 ** df['reserve.decimals'])
    return df

def process_deposits(df_deposits, df_rates):
    df_hourly = bubbletea.beta_aggregate_timeseries(
        data=df_deposits,
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

    df_hourly = df_hourly.merge(df_rates, left_index=True, right_index=True)
    df_hourly["volume"] = df_hourly["amount"] * df_hourly["rate"]
    df_hourly.index.names = ['timestamp']

    df = bubbletea.beta_aggregate_timeseries(
        data=df_hourly,
        time_column="timestamp",
        interval=interval,
        columns=[
            bubbletea.ColumnConfig(
                name="amount",
                aggregate_method=bubbletea.AggregateMethod.SUM,
                na_fill_value=0.0,
            ),
            bubbletea.ColumnConfig(
                name="rate",
                aggregate_method=bubbletea.AggregateMethod.LAST,
                na_fill_method=bubbletea.NaInterpolationMethod.FORDWARD_FILL,
            ),
            bubbletea.ColumnConfig(
                name="volume",
                aggregate_method=bubbletea.AggregateMethod.SUM,
                na_fill_value=0.0,
            ),
        ],
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
    )
    df.fillna(0.0, inplace=True)
    return df


with st.spinner("Loading and processing rates data"):
    df_rates = get_rates_df(token_symbol_cp, start_timestamp, end_timestamp)

with st.spinner("Loading deposits data"):
    df_deposits = get_token_deposits()

with st.spinner("Loading and aggregating deposit data"):
    df = process_deposits(df_deposits, df_rates)
    st.write(df)
    p = INTERVALS[interval]
    bubbletea.beta_plot_combo(
        df,
        title=p,
        x={"field": "timestamp", "title": "Time"},
        yLeft={
            "marker": bubbletea.line.MARKER,
            "data":[{"title": "Amount","field":"amount"}]
        },
        yRight={
            "marker": bubbletea.line.MARKER,
            "data":[{"title": "Rate","field":"rate"}],
            "scale": alt.Scale(zero=False),
        },
        legend="none",
    )

    if len(df) > 1:
        coeff = df['amount'].corr(df['rate'])
        bubbletea.beta_plot_text(
            "Coefficient between `amount` and `rate`",
            primary_text=0.1,
            formatter="0,0.00a",
            key=f"normal{p}",
        )
