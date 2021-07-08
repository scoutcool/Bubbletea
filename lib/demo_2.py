from earlgrey.thegraph import thegraph_loader as gl
import pandas as pd
from earlgrey.charts import line as l
from earlgrey import crypto_compare as cp
from earlgrey.transformers import timeseries as ts

start_timestamp = 1609459200    #2021-01-01 UTC
end_timestamp = 1610236800      #2021-01-10 UTC

CP_API_TOKEN = "163b4f02ba446862200ecf7a64c3359b6d6bcf9d417aa27a0b5b29c9f9e619be"  # os.environ.get("cp_api_token")
pricing_df = cp.load_historical_data(
    "AAVE", "USD", start_timestamp, end_timestamp, CP_API_TOKEN, 2000
)


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

data = gl.load_subgraph(url_aave_subgraph, query_aave, 
        astypes=[
                gl.FieldConfig(name='timestamp',type='datetime',unit='s'),
                gl.FieldConfig(name='amount',type='float'),
                gl.FieldConfig(name='reserve.decimals',type='int')
            ]
    )
df = data["data"]["deposits"]
aave_df = df[df['reserve.symbol'] == 'AAVE'] 
aave_hourly_df = ts.aggregate_timeseries(
    aave_df,
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
aave_hourly_df["amount"] = aave_hourly_df["amount"] / 1000000000000000000
# print(aave_hourly_df)
result = aave_hourly_df.merge(pricing_df, left_index=True, right_on='time')
# print(result)

l.plot(result, 
    x={"title":"Time", "field":"time"},
    yLeft = [{"title":"Price", "field":"close"}],
    yRight= [{"title":"Amount", "field":"amount"}]
    )
