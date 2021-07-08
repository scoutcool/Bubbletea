import datetime
import streamlit as st
import time
import pandas as pd
import earlgrey.thegraph.thegraph_loader as gl
import earlgrey.transformers.timeseries as ts
from earlgrey.charts.line import plot as plot_line


st.header("LIVEPEER Stake Movement")
date_range = st.date_input(
    "Date range",
    (
        datetime.date.today() - datetime.timedelta(days=7),
        datetime.date.today() - datetime.timedelta(days=0),
    ),
)

if not len(date_range) == 2:
    st.warning("*Please select a date range.*")
    st.stop()

start_timestamp = int(time.mktime(date_range[0].timetuple()))
end_timestamp = int(time.mktime(date_range[1].timetuple()))

subgraph_url = "https://api.thegraph.com/subgraphs/name/livepeer/livepeer"
query_date_clause = "{timestamp_gte:%s,timestamp_lt:%s}" % (
    start_timestamp,
    end_timestamp,
)
query = """
{
  bondEvents(where: %s, bypassPagination:true)
  {
  	timestamp,
    bondedAmount,
    round {id},
    newDelegate {id},
    oldDelegate {id},
    delegator {id},
  },
  unbondEvents(where: %s, bypassPagination:true)
  {
    timestamp,
    amount,
    withdrawRound,
    round {id},
    delegate {id},
    delegator {id},
  },
  rebondEvents(where: %s, bypassPagination:true)
  {
    timestamp,
    amount,
    round {id},
    delegate {id},
    delegator {id},
  }
}
""" % (
    query_date_clause,
    query_date_clause,
    query_date_clause,
)

with st.spinner("Loading data from the graph"):
    data = gl.load_subgraph(subgraph_url, query, astypes=[
        gl.FieldConfig(name='timestamp', type='datetime', unit='s'),
        gl.FieldConfig(name='round', type='int32'),
        gl.FieldConfig(name='amount', type='float')
    ])

df_bond = data["data"]["bondEvents"]
df_bond.rename(columns={"bondedAmount": "amount"}, inplace=True)
df_rebond = data["data"]["rebondEvents"]
df_unbond = data["data"]["unbondEvents"]
for df in [df_bond, df_rebond, df_unbond]:
    df["amount"] = df["amount"].apply(lambda x: float(x))
df_amount = (
    df_bond[["timestamp", "amount", "round.id"]]
    .append(df_rebond[["timestamp", "amount", "round.id"]])
    .append(df_unbond[["timestamp", "amount", "round.id"]])
    .reset_index()
)
df_amount_over_time = ts.aggregate_timeseries(
    df_amount,
    time_column="timestamp",
    interval=ts.TimeseriesInterval.DAILY,
    columns=[
        ts.ColumnConfig(
            name="amount",
            aggregate_method=ts.AggregateMethod.SUM,
            type=ts.ColumnType.float,
            na_fill_value=0.0,
        )
    ],
)
df_amount_over_time.index.names = ["time"]
st.subheader("Stake moved over time")
plot_line(
    df_amount_over_time,
    x={
        "field": "time",
    },
    yLeft=[
        {
            "field": "amount",
            "title": "Amount",
        }
    ],
)

st.subheader("Stake moved over rounds")
df_amount_over_round = ts.aggregate_groupby(
    df_amount,
    by_column="round.id",
    columns=[
        ts.ColumnConfig(
            name="amount",
            aggregate_method=ts.AggregateMethod.SUM,
            type=ts.ColumnType.float,
            na_fill_value=0.0,
        )
    ],
)
df_amount_over_round.index.names = ["round"]
st.write(df_amount_over_round)
plot_line(
    df_amount_over_round,
    x={"field": "round", "title": "Round"},
    yLeft=[
        {
            "field": "amount",
            "title": "Amount",
        }
    ],
)


st.subheader("Transcoder Stake Changes")


def process_transcoders():
    df0 = df_bond[["timestamp", "amount", "round.id", "oldDelegate.id"]]
    df0.rename(columns={"oldDelegate.id": "transcoder", "amount": "loss"}, inplace=True)

    df1 = df_bond[["timestamp", "amount", "round.id", "newDelegate.id"]]
    df1.rename(columns={"newDelegate.id": "transcoder", "amount": "gain"}, inplace=True)

    df2 = df_unbond[["timestamp", "amount", "round.id", "delegate.id"]]
    df2.rename(columns={"delegate.id": "transcoder", "amount": "loss"}, inplace=True)

    df3 = df_rebond[["timestamp", "amount", "round.id", "delegate.id"]]
    df3.rename(columns={"delegate.id": "transcoder", "amount": "gain"}, inplace=True)
    df = df0.append(df1).append(df1).append(df2).append(df3)

    df.reset_index(inplace=True)
    return df


df_transcoders = process_transcoders()
df_loss_gains = ts.aggregate_groupby(
    df_transcoders,
    "transcoder",
    columns=[
        ts.ColumnConfig(
            name="loss",
            aggregate_method=ts.AggregateMethod.SUM,
            type=ts.ColumnType.float,
            na_fill_value=0.0,
        ),
        ts.ColumnConfig(
            name="gain",
            aggregate_method=ts.AggregateMethod.SUM,
            type=ts.ColumnType.float,
            na_fill_value=0.0,
        ),
    ],
)
df_loss_gains["total"] = df_loss_gains["loss"] + df_loss_gains["gain"]
st.write(df_loss_gains)
# print(df_transcoders)
# df_transcoders =
