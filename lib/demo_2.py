from earlgrey.thegraph import thegraph_loader as gl
import pandas as pd
from earlgrey.charts import line as l
from earlgrey import crypto_compare as cp
from earlgrey.transformers import timeseries as ts
import os

start_timestamp = 1609459200
end_timestamp = 1610236800

CP_API_TOKEN = "163b4f02ba446862200ecf7a64c3359b6d6bcf9d417aa27a0b5b29c9f9e619be"  # os.environ.get("cp_api_token")
pricing = cp.load_historical_data(
    "AAVE", "USD", start_timestamp, end_timestamp, CP_API_TOKEN, 2000
)
pricing_df = pd.json_normalize(pricing)
print(pricing_df[["time", "close"]])


url_aave_subgraph = "https://api.thegraph.com/subgraphs/name/aave/protocol-v2"
query_aave = """
{
    deposits(
        where:{timestamp_gt:%s, timestamp_lt:%s}
        orderBy: timestamp
        orderDirection: asc
        bypassPagination: true
    ) {
        amount
        timestamp
    }
}
""" % (
    start_timestamp,
    end_timestamp,
)

data = gl.load_subgraph(url_aave_subgraph, query_aave)
data = pd.json_normalize(data["data"]["deposits"])
data_hourly_df = ts.aggregate_timeseries(
    data,
    time_column="timestamp",
    interval=ts.TimeseriesInterval.HOURLY,
    columns=[
        ts.ColumnConfig(
            name="amount",
            type="float",
            aggregate_method=ts.AggregateMethod.SUM,
            na_fill_value=0.0,
        )
    ],
)
data_hourly_df = data_hourly_df.reset_index()
print(data_hourly_df)
result = pd.concat([pricing_df, data_hourly_df], axis=1)
print(result)


l.plot(
    data_hourly_df,
    x={"title": "Time", "field": "timestamp"},
    yLeft=[{"title": "Price", "field": "amount"}],
)
