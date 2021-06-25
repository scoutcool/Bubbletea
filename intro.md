Earlgrey
--
A python library which enables developers to quickly build any data applications entirely on the emerging Web3 infrastructure. Whether you are a developer who builds dashboards to visualize protocol data or data scientist who studies correlations across different crypto data sources, we hope this library will be the fastest way to get what you want.

It is an ongoing project. At this stage, we aim to solve three problems:
- An improved way to query data from decentralized query networks such as The Graph
- A set of handy functions for common data transformations (built on Pandas)
- A set of out-of-box charting components to make visualizations effortless (built on Vega-lite)
- A simple templating system to build dashboards (built on Streamlit)

### load_subgraph (url, query)
An improved way to query data from a subgraph on The Graph network 
- Removed the limitation of up to 1000 items per request 
- When a graph query contains multiple entities, this function loads them concurrently

### load_subgraphs (subgraphs)
Querying multiple subgraphs on The Graph network concurrently.

### aggregate_timeseries (data, time_column, interval, columns)
Aggregating time series data

### plot_line (data, xs, ys)
Draw a line chart.

