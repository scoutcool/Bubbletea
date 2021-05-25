import thegraph_loader as gl
import streamlit as st


url_aave_subgraph = 'https://api.thegraph.com/subgraphs/name/aave/protocol'
query_template = """
{
    deposits(
        where:{timestamp_gt:1609459200, timestamp_lt:1609462800}
        orderBy: reserve
        orderDirection: desc
        bypassPagination: true
    ) {
        reserve {
            symbol,
            name,
            decimals
        }
        amount
    }
    flashLoans(
        orderBy: timestamp
        orderDirection: asc
    ){
        amount
        timestamp
    }
}
"""
# to break the pagination limit, set `bypassPagination` to `True`

data = gl.load_subgraph(url_aave_subgraph, query_template)
for k in data.keys():
    st.subheader(k)
    st.write(data[k])