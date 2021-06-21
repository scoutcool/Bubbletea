import earlgrey.thegraph.thegraph_loader as gl
import earlgrey.crypto_compare as cp
import earlgrey.transformers.timeseries as ts
from pandas.core.frame import DataFrame
import streamlit as st
from streamlit_ace import st_ace
import pandas as pd
import math
import altair as alt
import datetime
import time


# st.set_page_config(page_title="AAVE V2 Deposits", page_icon=":coin:", layout="wide")

PALETTE = [
    "#66D2C3",
    "#2E678E",
    "#F9965B",
    "#4CAAF7",
    "#E3EF89",
    "#8D6DCF",
    "#849AD9",
    "#EF6461",
    "#009FB7",
    "#FED766",
    "#728FE6",
    "#62C1D6",
    "#CF74BA",
    "#7AD07C",
    "#F7AA7C",
    "#39AD92",
    "#74BA7F",
    "#E56A99",
    "#7196BE",
    "#D08D66",
]


@st.cache(show_spinner=False)
def load_pricing(symbol, startTimestamp, endTimestamp):
    return cp.load_historical_data(symbol, 'USD', startTimestamp, endTimestamp, '163b4f02ba446862200ecf7a64c3359b6d6bcf9d417aa27a0b5b29c9f9e619be', 2000)


# 2020/11/01 to 2020/12/10
# START_TIMESTAMP = 1604188800
# END_TIMESTAMP = 1607558400

st.title("AAVE V2 Deposits")

# 2021/04/01 to 2021/06/10
date_range = st.date_input(
    "Date range",
    (
        datetime.date.today() - datetime.timedelta(days=13),
        datetime.date.today() - datetime.timedelta(days=3),
    ),
)


START_TIMESTAMP = int(time.mktime(date_range[0].timetuple()))
END_TIMESTAMP = int(time.mktime(date_range[1].timetuple()))
# print(f'{START_TIMESTAMP} {END_TIMESTAMP}')
TOKEN_SYMBOL_PRICING = "ETH"
TOKEN_SYMBOL = "WETH"
STATIC_DATE_FORMAT = "%Y/%m/%d"

url_aave_subgraph = "https://api.thegraph.com/subgraphs/name/aave/protocol-v2"
query_aave = """
{
    deposits(
        where:{timestamp_gt:%s, timestamp_lt:%s}
        orderBy: timestamp
        orderDirection: asc
        bypassPagination: true
    ) {
        reserve {
            symbol,
            name,
            decimals
        }
        amount
        timestamp
    }
}
""" % (
    START_TIMESTAMP,
    END_TIMESTAMP,
)


rates = []
pricing = load_pricing(TOKEN_SYMBOL_PRICING, START_TIMESTAMP, END_TIMESTAMP)
for p in pricing:
    rates.append({"rate": p["close"], "time": pd.to_datetime(p['time'], unit='s')})
df_rates = DataFrame(rates).set_index('time')

# df_rates = ts.aggregate_timeseries(
#     data=rates, 
#     time_column="time", 
#     interval=ts.TimeseriesInterval.HOURLY, 
#     columns=[ts.ColumnConfig(name="rate", aggregate_method=ts.AggregateMethod.LAST, na_fill_method=ts.NaInterpolationMethod.FORDWARD_FILL)]
# )

if st.checkbox("Display Rates Data"):
    st.write(rates)


@st.cache(show_spinner=False)
def get_eth_deposits():
    data = gl.load_subgraph(url_aave_subgraph, query_aave)
    deposits = data["data"]["deposits"]
    _eth_deposits = []
    for d in deposits:
        if d["reserve"]["symbol"] == TOKEN_SYMBOL:
            _eth_deposits.append(
                {
                    "amount": float(d["amount"]) / math.pow(10, int(d["reserve"]["decimals"])),
                    "time": d["timestamp"],
                }
            )
    return _eth_deposits


# @st.cache(show_spinner=False)
def get_deposits_df():

    _df_eth_deposits = ts.aggregate_timeseries(
        data=eth_deposits, 
        time_column="time", 
        interval=ts.TimeseriesInterval.HOURLY, 
        columns=[ts.ColumnConfig(name="amount", aggregate_method=ts.AggregateMethod.SUM, na_fill_value=0.0)]
    )

    _df_eth_deposits = _df_eth_deposits.merge(
        df_rates, left_index=True, right_index=True
    )
    _df_eth_deposits["volume"] = _df_eth_deposits["amount"] * _df_eth_deposits["rate"]
    return _df_eth_deposits


with st.spinner("Loading deposits data"):
    eth_deposits = get_eth_deposits()
with st.spinner("Aggregating deposit data"):
    df_eth_deposits = get_deposits_df()

if st.checkbox(f"Display {TOKEN_SYMBOL} deposits Data"):
    st.write(eth_deposits)


def get_line_chart(
    df,
    timeDef="time:T",
    timeFormat="%b %d",
    timeInterval="day",
    timeStep=1,
    palette=PALETTE,
):
    frames = df.reset_index()

    # Create a selection that chooses the nearest point & selects based on x-value
    nearest = alt.selection(
        type="single", nearest=True, on="click", fields=["time"], empty="none"
    )

    selectors = (
        alt.Chart(frames)
        .mark_point()
        .encode(
            x=timeDef,
            opacity=alt.value(0),
        )
        .add_selection(nearest)
    )

    # Draw a rule at the location of the selection
    rule = (
        alt.Chart(frames)
        .mark_rule(color=palette[2])
        .encode(
            x=timeDef,
        )
        .transform_filter(nearest)
    )

    def variable_chart(columnDef, color):

        base = alt.Chart(frames).encode(
            alt.X(
                timeDef,
                title="",
                axis=alt.Axis(
                    values=frames["time"].tolist(),
                    format=timeFormat,
                    domain=False,
                    grid=False,
                ),
                scale=alt.Scale(nice={"interval": timeInterval, "step": timeStep}),
            ),
            alt.Y(
                columnDef,
                stack=False,
                scale=alt.Scale(zero=False),
                axis=alt.Axis(
                    format=".2s",
                    titleColor=alt.Value(color),
                    labelExpr="replace(datum.label, 'G', 'B')",
                ),
            ),
        )
        line = base.mark_line(color=color)
        point = base.mark_point(color=color,).encode(
            y=alt.Y(
                columnDef,
                stack=False,
                scale=alt.Scale(zero=False),
                axis=None,
            ),
            opacity=alt.condition(nearest, alt.value(1), alt.value(0)),
        )
        text = base.mark_text(align="left", dx=8, dy=-8, color=color,).encode(
            y=alt.Y(
                columnDef,
                stack=False,
                scale=alt.Scale(zero=False),
                axis=None,
            ),
            text=alt.condition(nearest, columnDef, alt.value(" ")),
        )

        return [line, point, text]

    [amount_line, amount_point, amount_text] = variable_chart("amount:Q", palette[0])

    [rate_line, rate_point, rate_text] = variable_chart("rate:Q", palette[1])

    combined = alt.layer(
        selectors,
        amount_line,
        rate_line,
        rule,
        amount_point,
        rate_point,
        amount_text,
        rate_text,
    ).resolve_scale(y="independent")

    st.altair_chart(
        combined.properties(height=400),
        use_container_width=True,
    )

df_eth_deposits = df_eth_deposits.reset_index()
df_eth_deposits["time"] =df_eth_deposits["time"].apply(lambda x: int(x.timestamp()))
# print(df_eth_deposits.to_json(orient='records'))
# print(f"{START_TIMESTAMP} {END_TIMESTAMP}")
df_eth_daily = ts.aggregate_timeseries(
    data=df_eth_deposits, 
    time_column="time", 
    interval=ts.TimeseriesInterval.DAILY, 
    columns=[
        ts.ColumnConfig(name="amount", aggregate_method=ts.AggregateMethod.SUM, na_fill_value=0.0),
        ts.ColumnConfig(name="volume", aggregate_method=ts.AggregateMethod.SUM, na_fill_value=0.0),
        ts.ColumnConfig(name="rate", aggregate_method=ts.AggregateMethod.LAST, na_fill_method=ts.NaInterpolationMethod.FORDWARD_FILL),
    ],
    start_timestamp = math.floor(START_TIMESTAMP/86400)*86400,
    end_timestamp = math.ceil(END_TIMESTAMP/86400)*86400
)
# print(df_eth_daily)

st.subheader("DAILY")
st.write(df_eth_daily)
get_line_chart(df_eth_daily)
# c1, c2 = st.beta_columns([1, 2])
# with c1:
#     st.subheader("DAILY")
#     st.write(df_eth_daily)
# with c2:
#     get_line_chart(df_eth_daily)

df_eth_weekly = ts.aggregate_timeseries(
    data=df_eth_deposits, 
    time_column="time", 
    interval=ts.TimeseriesInterval.WEEKLY, 
    columns=[
        ts.ColumnConfig(name="amount", aggregate_method=ts.AggregateMethod.SUM, na_fill_value=0.0),
        ts.ColumnConfig(name="volume", aggregate_method=ts.AggregateMethod.SUM, na_fill_value=0.0),
        ts.ColumnConfig(name="rate", aggregate_method=ts.AggregateMethod.LAST, na_fill_method=ts.NaInterpolationMethod.FORDWARD_FILL),
    ],
    start_timestamp = math.floor(START_TIMESTAMP/86400)*86400,
    end_timestamp = math.ceil(END_TIMESTAMP/86400)*86400
)

st.subheader("WEEKLY")
st.write(df_eth_weekly)
get_line_chart(df_eth_weekly)
# c1, c2 = st.beta_columns([1, 2])
# with c1:
#     st.subheader("WEEKLY")
#     st.write(df_eth_weekly)
# with c2:
#     get_line_chart(df_eth_weekly)


df_eth_monthly = ts.aggregate_timeseries(
    data=df_eth_deposits, 
    time_column="time", 
    interval=ts.TimeseriesInterval.MONTHLY, 
    columns=[
        ts.ColumnConfig(name="amount", aggregate_method=ts.AggregateMethod.SUM, na_fill_value=0.0),
        ts.ColumnConfig(name="volume", aggregate_method=ts.AggregateMethod.SUM, na_fill_value=0.0),
        ts.ColumnConfig(name="rate", aggregate_method=ts.AggregateMethod.LAST, na_fill_method=ts.NaInterpolationMethod.FORDWARD_FILL),
    ],
    start_timestamp = math.floor(START_TIMESTAMP/86400)*86400,
    end_timestamp = math.ceil(END_TIMESTAMP/86400)*86400
)

st.subheader("MONTHLY")
st.write(df_eth_monthly)
get_line_chart(df_eth_monthly, timeFormat="%b")
# c1, c2 = st.beta_columns([1, 2])
# with c1:
#     st.subheader("MONTHLY")
#     st.write(df_eth_monthly)
# with c2:
#     get_line_chart(df_eth_monthly, timeFormat="%b")
