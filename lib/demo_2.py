
import time
import earlgrey
from earlgrey import crypto_compare as cp
from earlgrey.transformers import timeseries as ts
import os
import datetime


from dotenv import load_dotenv
load_dotenv()

urlvars = earlgrey.parse_url_var([{'key':'startdate','type':'datetime'}, {'key':'enddate','type':'datetime'}])

try:
    end_date = urlvars['enddate']
except KeyError:
    end_date = datetime.date.today() - datetime.timedelta(days=0)

try:
    start_date = urlvars['startdate']
except KeyError:
    start_date = end_date - datetime.timedelta(days=7)

earlgrey.update_url({'startdate': start_date, 'enddate': end_date})

start_timestamp = int(time.mktime(start_date.timetuple()))
end_timestamp = int(time.mktime(end_date.timetuple()))

CP_API_TOKEN = os.environ.get("cp_api_token")
pricing_df = cp.load_historical_data("AAVE", "USD", start_timestamp, end_timestamp, CP_API_TOKEN, 2000)


url_aave_subgraph = "https://api.thegraph.com/subgraphs/name/aave/protocol-v2"
query_aave = """
{
    deposits(
        where:{timestamp_gte:%s, timestamp_lt:%s}
        orderBy: timestamp
        orderDirection: asc
        bypassPagination: true
    ) {
        amount
        timestamp
        reserve {
            symbol
            decimals
        }
    }
}
""" % (
    start_timestamp,
    end_timestamp,
)

data = earlgrey.load_subgraph(url_aave_subgraph, query_aave)
df = data["data"]["deposits"]
aave_df = df[df['reserve.symbol'] == 'AAVE'] 
aave_hourly_df = ts.aggregate_timeseries(
    aave_df,
    time_column="timestamp",
    interval=ts.TimeseriesInterval.HOURLY,
    columns=[
        ts.ColumnConfig(
            name="amount",
            aggregate_method=ts.AggregateMethod.SUM,
            na_fill_value=0.0,
        )
    ],
)
aave_hourly_df["amount"] = aave_hourly_df["amount"] / 1000000000000000000
# print(aave_hourly_df)
result = aave_hourly_df.merge(pricing_df, left_index=True, right_on='time')
# print(result)

earlgrey.plot_line(
    title='Hourly AAVE Deposits vs Pricing',
    df=result, 
    x={"title":"Time", "field":"time"},
    yLeft = [{"title":"Price", "field":"close"}],
    yRight= [{"title":"Amount", "field":"amount"}]
    )
