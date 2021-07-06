from earlgrey.thegraph import thegraph_loader as gl
import pandas as pd
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

data = gl.load_subgraph(url_aave_subgraph, query_aave)
data = pd.json_normalize(data["data"]["deposits"])
l.plot(
    data,
    x={"title": "Time", "field": "timestamp"},
    yLeft=[{"title": "Amount", "field": "amount"}],
)
