import earlgrey.thegraph.thegraph_loader as gl
import earlgrey.crypto_compare as cp
import earlgrey.transformers.timeseries as ts
from pandas._libs.tslibs import Period
from pandas.core.frame import DataFrame
import streamlit as st
from streamlit_ace import st_ace
import pandas as pd
import math
import altair as alt
import datetime
import time

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
PERIODS = [ts.TimeseriesInterval.DAILY,ts.TimeseriesInterval.WEEKLY,ts.TimeseriesInterval.MONTHLY]

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



st.title(f"AAVE V2 {TOKEN_SYMBOL} Deposits")

@st.cache(show_spinner=False)
def process_deposits(deposits):
    df_hourly = ts.aggregate_timeseries(
        data=deposits, 
        time_column="time", 
        interval=ts.TimeseriesInterval.HOURLY, 
        columns=[ts.ColumnConfig(name="amount", aggregate_method=ts.AggregateMethod.SUM, na_fill_value=0.0)]
    )

    df_hourly = df_hourly.merge(
        df_rates, left_index=True, right_index=True
    )
    df_hourly["volume"] = df_hourly["amount"] * df_hourly["rate"]
    result = {}
    for p in PERIODS:
        df = ts.aggregate_timeseries(
            data=df_hourly, 
            time_column="time", 
            interval=p,
            columns=[
                ts.ColumnConfig(name="amount", aggregate_method=ts.AggregateMethod.SUM, na_fill_value=0.0),
                ts.ColumnConfig(name="volume", aggregate_method=ts.AggregateMethod.SUM, na_fill_value=0.0),
                ts.ColumnConfig(name="rate", aggregate_method=ts.AggregateMethod.LAST, na_fill_method=ts.NaInterpolationMethod.FORDWARD_FILL),
            ]
        )
        result[p] = df
    return result


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



with st.spinner("Loading deposits data"):
    eth_deposits = get_eth_deposits()
with st.spinner("Aggregating deposit data"):
    dfs = process_deposits(eth_deposits)
    for p in dfs.keys():
        st.subheader(p)
        df = dfs[p]
        get_line_chart(df)