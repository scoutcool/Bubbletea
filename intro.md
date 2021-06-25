Earlgrey
--
A python library which enables developers to quickly build any data applications entirely on the emerging Web3 infrastructure. It is an ongoing project. At this stage, we aim to solve three problems:
- An improved way to query data from decentralized query networks such as The Graph
- Handy functions for common data transformations
- A set of out-of-box charting components to make it easy to visualize any data


### load_subgraph (url, query)
An improved way to query data from a subgraph on The Graph network 
- Removed the limitation of up to 1000 items per request 
- When a graph query contains multiple entities, this function loads them concurrently

### load_subgraphs (subgraphs)
Querying multiple subgraphs on The Graph network concurrently.

### aggregate_timeseries
Building time based charts is a very common use case. This function 

### plot_line (data, xs, ys)
Draw a line chart.

