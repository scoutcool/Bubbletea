import thegraph_loader as gl
import streamlit as st
# from streamlit.ReportThread import add_report_ctx


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
        first:3
    ){
        amount
        timestamp
    }
}
"""

data = gl.load_subgraph(url_aave_subgraph, query_template)
for k in data.keys():
    st.subheader(k)
    st.write(data[k])


# import pandas as pd
# import concurrent.futures
# import requests
# import time

# out = []
# CONNECTIONS = 100
# TIMEOUT = 5

# # tlds = open('../data/sample_1k.txt').read().splitlines()
# urls = ['https://google.com','https://amazon.com']

# def load_url(url, timeout):
#     ans = requests.get(url, timeout=timeout)
#     return ans.status_code

# with concurrent.futures.ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
#     future_to_url = (executor.submit(load_url, url, TIMEOUT) for url in urls)
#     time1 = time.time()
#     for future in concurrent.futures.as_completed(future_to_url):
#         try:
#             data = future.result()
#             print('data ')
#             print(data)
#         except Exception as exc:
#             data = str(type(exc))
#         finally:
#             out.append(data)

#             print(str(len(out)),end="\r")

#     time2 = time.time()

# print('done ')
# print(str(time2 - time2))
# # print(f"Took {time2-time1:.2f} s")
# print(pd.Series(out).value_counts())