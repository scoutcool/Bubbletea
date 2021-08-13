import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib import bubbletea
import streamlit as st


st.subheader('Single Subgraph')
url_aave_subgraph = 'https://api.thegraph.com/subgraphs/name/aave/protocol-v2'
query_aave = """{
    deposits(
        where:{timestamp_gte:1609459200, timestamp_lt:1610236800}
        orderBy: timestamp
        orderDirection: desc
        bypassPagination: true
    ) {
        reserve {
            symbol,
            decimals
        }
        amount
        timestamp
    }
    flashLoans(
        orderBy: timestamp
        orderDirection: asc
        first:3
    ){
        amount
         timestamp
     }
}
"""

# data = bubbletea.load_subgraph(url_aave_subgraph, query_aave)
# print(data)
# df = data['factories']
# print(df.dtypes)

# df_daydata = pd.DataFrame(data = df['dayData'][0])
# print(df_daydata)
# print(df_daydata.dtypes)

url_compoundv2_subgraph = 'https://api.thegraph.com/subgraphs/name/graphprotocol/compound-v2'
query_compoundv2 = """
{
	mintEvents(
        where:{blockTime_gte:1609459200, blockTime_lt:1610236800}
        bypassPagination: true
    ) {
	    cTokenSymbol
        amount
        underlyingAmount
        blockTime
	}
}
"""
# data = gl.load_subgraph(url_compoundv2_subgraph, query_compoundv2)


# data = data['data']
# for k in data.keys():
#     st.markdown(f'### {k}')
#     st.markdown('#### Data')
#     st.write(data[k])
#     st.markdown('#### Column Types')
#     st.write(data[k].dtypes)



# st.markdown('---')
# st.subheader('Multiple Subgraphs')
data = bubbletea.load_subgraphs([
    bubbletea.SubgraphDef(url=url_aave_subgraph, query=query_aave), 
    bubbletea.SubgraphDef(url=url_compoundv2_subgraph, query=query_compoundv2)
    ])
    
df_aave_deposits = data[url_aave_subgraph]['deposits']
df_aave_flashloans = data[url_aave_subgraph]['flashLoans']
df_compound_mints = data[url_compoundv2_subgraph]['mintEvents']
print(df_aave_deposits)
print(df_aave_deposits.dtypes)
print(df_aave_flashloans)
print(df_aave_flashloans.dtypes)
print(df_compound_mints)
print(df_compound_mints.dtypes)

# for k in data.keys():
#     st.subheader(k)
#     subgraph = data[k]
#     for e in subgraph.keys():
#         st.markdown(f'### {e}')
#         df = subgraph[e]
#         st.markdown('#### Data')
#         st.write(df)
#         st.markdown('#### Column Types')
#         st.write(df.dtypes)
#         # print(df.dtypes)