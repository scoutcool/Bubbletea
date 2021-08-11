import datetime
import datetime
from pandas.core.frame import DataFrame
import streamlit as st
import time
import bubbletea

st.header("LIVEPEER Stake Movement")

urlvars = bubbletea.parse_url_var([{'key':'startdate','type':'datetime'}, {'key':'enddate','type':'datetime'}])

try:
    end_date = urlvars['enddate']
except KeyError:
    end_date = datetime.date.today() - datetime.timedelta(days=0)

try:
    start_date = urlvars['startdate']
except KeyError:
    start_date = end_date - datetime.timedelta(days=7)

date_range = st.date_input("Date range", (start_date, end_date))

if not len(date_range) == 2:
    st.warning("*Please select a date range.*")
    st.stop()

start_date = date_range[0]
end_date = date_range[1]

start_timestamp = int(time.mktime(start_date.timetuple()))
end_timestamp = int(time.mktime(end_date.timetuple()))

bubbletea.update_url({'startdate': start_date, 'enddate':end_date})

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
    df = bubbletea.load_subgraph(subgraph_url, query, useBigDecimal=True)

df_bond = df["bondEvents"]
df_bond.rename(columns={"bondedAmount": "amount"}, inplace=True)
df_rebond = df["rebondEvents"]
df_unbond = df["unbondEvents"]

i = 0
df_amount = DataFrame()
for df in [df_bond, df_rebond, df_unbond]:
    if len(df) > 0:
        if i == None:
            df_amount = df[["timestamp", "amount", "round.id"]]
        else:
            df_amount = df_amount.append(df[["timestamp", "amount", "round.id"]])
        i += 1

if len(df_amount) == 0:
    st.write('No data vailable')
else:
    df_amount = df_amount.reset_index()
    df_amount_over_time = bubbletea.aggregate_timeseries(
        df_amount,
        time_column="timestamp",
        interval=bubbletea.TimeseriesInterval.DAILY,
        columns=[
            bubbletea.ColumnConfig(
                name="amount",
                aggregate_method=bubbletea.AggregateMethod.SUM,
                na_fill_value=0.0,
            )
        ],
    )
    df_amount_over_time.index.names = ["time"]
    st.subheader("Stake moved over time")
    st.write(df_amount_over_time)
    bubbletea.plot_line(
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

    df_amount_over_round = bubbletea.aggregate_groupby(
        df_amount,
        by_column="round.id",
        columns=[
            bubbletea.ColumnConfig(
                name="amount",
                aggregate_method=bubbletea.AggregateMethod.SUM,
                na_fill_value=0.0,
            )
        ],
    )
    df_amount_over_round.index.names = ["round"]
    st.write(df_amount_over_round)
    bubbletea.plot_line(
        df_amount_over_round,
        title='Stake moved over rounds',
        x={"field": "round", "title": "Round", "type":"ordinal"},# ['quantitative', 'ordinal', 'temporal', 'nominal']
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

        df.fillna(0.0, inplace=True)
        df.reset_index(inplace=True)
        return df


    df_transcoders = process_transcoders()
    df_loss_gains = bubbletea.aggregate_groupby(
        df_transcoders,
        "transcoder",
        columns=[
            bubbletea.ColumnConfig(
                name="loss",
                aggregate_method=bubbletea.AggregateMethod.SUM,
                na_fill_value=0.0,
            ),
            bubbletea.ColumnConfig(
                name="gain",
                aggregate_method=bubbletea.AggregateMethod.SUM,
                na_fill_value=0.0,
            ),
        ],
    )
    df_loss_gains["total"] = df_loss_gains["loss"] + df_loss_gains["gain"]
    st.write(df_loss_gains)
