import os
import sys
print('hahaahaha')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import lib.earlgrey.thegraph.thegraph_loader as gl
import streamlit as st


url_aave_subgraph = 'https://api.thegraph.com/subgraphs/name/aave/protocol'
query_aave = """
{
    deposits(
        where:{timestamp_gt:1609459200, timestamp_lt:1609462800}
        orderBy: timestamp
        orderDirection: desc
        first:5
        # bypassPagination: true
    ) {
        reserve {
            symbol,
            decimals
        }
        amount
        timestamp
    }
    # flashLoans(
    #     orderBy: timestamp
    #     orderDirection: asc
    #     first:3
    # ){
    #     amount
    #      timestamp
    #  }
}
"""
data = gl.load_subgraph(url_aave_subgraph, query_aave, 
    astypes=[
        gl.FieldConfig(name='amount', type='float'),
        gl.FieldConfig(name='timestamp', type='datetime'),
        gl.FieldConfig(name='reserve.decimals', type='int'),
        gl.FieldConfig(name='random', type='int')
        ]
    )
df = data['data']['deposits']
df = df.astype({'amount':'float'}, copy=False)
print(df.dtypes)
# print(data['data'].dtypes)
# for k in data.keys():
    # print(data[k])
    # st.subheader(k)
    # st.write(data[k])

# url_compoundv2_subgraph = 'https://api.thegraph.com/subgraphs/name/graphprotocol/compound-v2'
# query_compoundv2 = """
# {
# 	mintEvents(
#         where:{blockTime_gte:1609459200, blockTime_lt:1609462800}
#         bypassPagination: true
#     ) {
# 	    cTokenSymbol
#         amount
#         underlyingAmount
# 	}
# }
# """

# data = gl.load_subgraphs([gl.SubgraphDef(url=url_aave_subgraph, query=query_aave), gl.SubgraphDef(url=url_compoundv2_subgraph,query=query_compoundv2)])
# print(data)

# for k in data.keys():
#     st.subheader(k)
#     st.write(data[k])

# # st.write("hello world")