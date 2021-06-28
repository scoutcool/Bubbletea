Earlgrey
--

A python library which enables developers to quickly build any data applications on the emerging Web3 infrastructure. Whether you are a developer who builds dashboards to visualize protocol data or data scientist who studies correlations across different crypto data sources, we hope this library will be the fastest way to get what you want.

### Benefits

### How to get started
[Installation and examples](https://www.google.com "Google's Homepage")


### Creating virtual environments
`python3 -m venv <DIR>`

`source <DIR>/bin/activate`

### Install Earlgrey
Earlgrey is published at pypi test for now.
`pip3 install --index-url https://test.pypi.org/simple/ --no-deps example-pkg-earlgrey`

### Earlgrey usage
#### The graph loader:
##### Single subgraph
```
import earlgrey.thegraph.thegraph_loader as gl
data = gl.load_subgraph(<subgraph_url>, <subgraph_query>)
```
#### Multiple subgraphs
```
import earlgrey.thegraph.thegraph_loader as gl
data = gl.load_subgraphs([gl.SubgraphDef(url=<subgraph_url1>, query=<subgraph_query1>), gl.SubgraphDef(url=<subgraph_url2>,query=<subgraph_query2>)])
```


#### Getting rates from (Crypto Compare)[https://www.cryptocompare.com/coins/guides/how-to-use-our-api/]:
You will need to register an API first.
```
import earlgrey.crypto_compare as cp
cp.load_historical_data('ETH', 'USD', 1619827200, 1619913600, <your_api_key>, <your_api_limit>)
```

#### Aggregate for timeseries:
```
import lib.earlgrey.transformers.timeseries as ts
data = [
    {"time":1609459201, "amount":1, "rate":1.1},    #2021/01/01
    {"time":1609459202, "amount":2, "rate":1.2},    #2020/01/01
    {"time":1609632004, "amount":4, "rate":1.4}]    #2020/01/03
df = ts.aggregate_timeseries(
    data = data,
    timeColumn='time',
    interval=ts.TimeseriesInterval.DAILY,
    columnsToAggregate=[
        ts.ColumnConfig(name='amount', aggregateMethod=ts.AggregateMethod.SUM, naFillValue=0.0),
        ts.ColumnConfig(name='rate', aggregateMethod=ts.AggregateMethod.LAST, naFillMethod=ts.NaInterpolationMethod.FORDWARD_FILL)
    ],
    startTimestamp=1609113600,
    endTimestamp=1610236800
)
```


### Run Earlgrey
`earlgrey run <app_file.py>`
