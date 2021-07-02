from earlgrey.thegraph import thegraph_loader as gl
import pandas as pd
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

data = gl.load_subgraph(url_aave_subgraph, query_aave)
data = pd.json_normalize(data["data"]["deposits"])
data["timestamp"] = data["timestamp"].apply(
    lambda x: pd.to_datetime(x, unit="s")
)  # will be removed once chart lib is updated

l.plot(
    data,
    x={"title": "Time", "field": "timestamp"},
    yLeft=[{"title": "Amount", "field": "amount"}],
)