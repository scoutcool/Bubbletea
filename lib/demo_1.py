import math
from earlgrey.thegraph import loader as gl
from earlgrey.charts import line as l

url_aave_subgraph = "https://api.thegraph.com/subgraphs/name/aave/protocol-v2"
query_aave = """
{
    deposits(
        where:{timestamp_gt:1609459200, timestamp_lt:1610236800}
        orderBy: timestamp
        orderDirection: asc
        bypassPagination: true
    ) {
        amount
        timestamp
    }
}
"""

#Load data from Aave subgraph
df = gl.load_subgraph(url_aave_subgraph, query_aave)
df = df["data"]["deposits"]

#Convert token amount with 18 decimals
df['amount'] = df["amount"] / math.pow(10, 18)

#Draw the data on a line chart
l.plot(
    title='AAVE Deposits',
    df=df,
    x={"title": "Time", "field": "timestamp"},
    ys=[{"title": "Amount", "field": "amount"}],
)
