from .__core.SubgraphLoader import SubgraphLoader
import streamlit as st
import concurrent.futures
from streamlit.report_thread import add_report_ctx

class SubgraphDef:
    def __init__(self, url:str, query:str, progressCallback=None, useBigDecimal=False) -> None:
        self.url = url
        self.query = query
        self.progressCallback = progressCallback
        self.useBigDecimal = useBigDecimal



"""
Fetch data from a single subgraph, multiple entities are supported.
Params:
`url`: The url of the subgraph. [Explore subgraphs](https://thegraph.com/explorer/)
`query`: The graph query. [Docs](https://thegraph.com/docs/graphql-api#queries)
    `bypassPagination`: Boolean value, default `False`. The graph has a limitation of 10000 items max per request. To load all items in the selected query, add this flag in the filter of each entity. For example: `deposits(bypassPagination, ....) {...}`.
    If `False`, the function will retrieve 100 items.
`progressCallback`: A callback function that is called when items are retreived from the graph. The argument is defined as `({<Entity_name>: <Number_of_items_loaded>})`
`useBigDecimal`: bool. Default `Faulse`. When True, `BigDecimal`, `BigInt` types from the graph will be converted to Decimal 128 type numbers so to keep the precision of the numbers. Otherwise, converted to float64. Recommend to set to `True` if to display the numbers.
Return:
```
{
    'url': url,
    'data': {
        <Entity_name>: <DataFrame_of_items_from_the_graph>
    }
}
```

"""
def beta_load_subgraph(url:str, query:str, progressCallback=None, useBigDecimal=False):
    sl = SubgraphLoader(url, query)
    return sl.beta_load_subgraph(progressCallback, useBigDecimal)

"""
Fetch data from multiple subgraphs .
Params:
`url`: The url of the subgraph. [Explore subgraphs](https://thegraph.com/explorer/)
`query`: The graph query. [Docs](https://thegraph.com/docs/graphql-api#queries)
    `bypassPagination`: Boolean value, default `False`. The graph has a limitation of 10000 items max per request. If to load all items in the selected query, add this flag in the filter of each entity. For example: `deposits(bypassPagination, ....) {...}`.
Return:
```
{
    <url1>: {
        <Entity_name>: <DataFrame_of_items_from_the_graph>
    },
    <url2>: {
        <Entity_name>: <DataFrame_of_items_from_the_graph>
    }
}
"""
def beta_load_subgraphs(defs:list[SubgraphDef]):
    results = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(defs)) as executor:
        future_to_url = {executor.submit(beta_load_subgraph, d.url, d.query, d.progressCallback, d.useBigDecimal): d for d in defs}
        # future_to_url = {executor.submit(beta_load_subgraph, d.url, d.query, d.progressCallback, d.useBigDecimal) for d in defs}
        # for thread in executor._threads:
        #     add_report_ctx(thread)

        for future in concurrent.futures.as_completed(future_to_url):
            d = future_to_url[future]
            try:
                data = future.result()
                results[d.url] = data
            except Exception as e:
                st.exception(e)
    return results
