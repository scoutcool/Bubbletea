import math
from earlgrey.thegraph import loader as gl
from earlgrey.charts import line as l

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

df = gl.load_subgraph(url_aave_subgraph, query_aave)
df = df["data"]["deposits"]
df['amount'] = df["amount"] / math.pow(10, 18)

l.plot(
    title='AAVE Deposits',
    df=df,
    x={"title": "Time", "field": "timestamp"},
    ys=[{"title": "Amount", "field": "amount"}],
)
