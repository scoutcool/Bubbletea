from earlgrey.thegraph import thegraph_loader as gl
import pandas as pd
from earlgrey.charts import line as l
from earlgrey import crypto_compare as cp
from earlgrey.transformers import timeseries as ts
import os

start_timestamp = 1609459200
end_timestamp = 1610236800

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
data_hourly = ts.aggregate_timeseries(
    data,
    time_column="timestamp",
    interval=ts.TimeseriesInterval.HOURLY,
    columns=[
        ts.ColumnConfig(
            name="amount",
            aggregate_method=ts.AggregateMethod.SUM,
            na_fill_value=0.0,
        )
    ]
)

print(data_hourly)
l.plot(data_hourly, 
    x={"title":"Time", "field":"timestamp"},
    yLeft = [{"title":"Price", "field":"amount"}]
    )