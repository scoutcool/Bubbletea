import streamlit as st
import pandas as pd
import numpy as np
import requests
import json


st.title('Livepeer Unbonding Demo')

#subgraph: https://thegraph.com/explorer/subgraph/livepeer/livepeer
url = 'https://api.thegraph.com/subgraphs/name/livepeer/livepeer'


def load_data(rawdata):
	data = pd.json_normalize(rawdata["data"]["days"])
	data['date'] = data['date'].apply(lambda x: pd.to_datetime(x, unit='s'))
	df = pd.DataFrame({
	  'volumeETH': data['volumeETH'],
	  'date': data['date']
	})
	df = df.set_index('date')
	return df
    
# query = """
# 	{
# 	  days(where: { date_gte:1617926400 }) {
# 	    volumeETH,
# 	    date
# 	  }
# 	}
# """

# r = requests.post(url, json={'query': query}) #'variables':variables})
# chart_data = load_data(json.loads(r.text))
# st.line_chart(chart_data)

rawdata = {
  "data": {
    "days": [
      {
        "date": 1617926400,
        "volumeETH": "0.211764705882352941"
      },
      {
        "date": 1618012800,
        "volumeETH": "0"
      },
      {
        "date": 1618099200,
        "volumeETH": "0.413793103448275862"
      },
      {
        "date": 1618185600,
        "volumeETH": "0.206896551724137931"
      },
      {
        "date": 1618272000,
        "volumeETH": "0.613636363636363635"
      },
      {
        "date": 1618358400,
        "volumeETH": "0"
      },
      {
        "date": 1618444800,
        "volumeETH": "0.204545454545454545"
      },
      {
        "date": 1618531200,
        "volumeETH": "0.202247191011235955"
      },
      {
        "date": 1618617600,
        "volumeETH": "0.202247191011235955"
      },
      {
        "date": 1618704000,
        "volumeETH": "0.202247191011235955"
      },
      {
        "date": 1618790400,
        "volumeETH": "0"
      }
    ]
  }
}

data = pd.json_normalize(rawdata["data"]["days"])
data['date'] = data['date'].apply(lambda x: pd.to_datetime(x, unit='s'))
data['date'] = data['date'].apply(lambda x: x.strftime('%Y/%m/%d'))

df = pd.DataFrame(data=data,columns=['date', 'volumeETH'])
print('df1:')
print(df)
# df['date']=(pd.to_datetime(df['date'], unit='s'))
# print('\n\ndf2:')
# print(df)

df = df.set_index('date')
print('\n\ndf3:')
print(df)



# df = pd.DataFrame({
#   'date': ['2020/04/09','2020/04/10', '2020/04/11', '2020/04/12'],
#   'volume': [10, 20, 30, 40]
# })
# df = df.set_index('date')

# df = pd.DataFrame(
#     np.random.randn(20, 3),
#     columns=['volume'])

st.write(df)
st.line_chart(df)
