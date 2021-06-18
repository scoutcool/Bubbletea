import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import lib.earlgrey.transformers.timeseries as ts
import pandas as pd
import json
import math

def is_json(candidate):
    try:
        pd.json_normalize()
        s = str(candidate)
        print(s)
        json.loads(s)
    except ValueError as e:
        print(e)
        return False
    return True

# data = [
#     {"time":1609459201, "amount":100.8428986732, "rate":"1.1"},    #2021/01/01
#     {"time":1609459202, "amount":200.8428986732, "rate":"1.2"},    #2020/01/01
#     {"time":1609632004, "amount":400.8428986732, "rate":"1.4"}]    #2020/01/03
# data = [{"time":1623470400,"amount":342.8428986732,"rate":2284.03,"volume":783063.4658565485},{"time":1623474000,"amount":659.0768128897,"rate":2290.69,"volume":1509740.6645183791},{"time":1623477600,"amount":145.8705492951,"rate":2299.31,"volume":335401.6126996332},{"time":1623481200,"amount":224.1610242195,"rate":2323.8,"volume":520905.3880813619},{"time":1623484800,"amount":109.7416150334,"rate":2309.22,"volume":253417.5322675332},{"time":1623488400,"amount":4589.925444684,"rate":2327.6,"volume":10683510.4650464915},{"time":1623492000,"amount":309.4396147385,"rate":2394.73,"volume":741024.328602692},{"time":1623495600,"amount":231.8042248997,"rate":2390.71,"volume":554176.6785099012},{"time":1623499200,"amount":235.6877159042,"rate":2439.76,"volume":575021.4617544537},{"time":1623502800,"amount":1074.5793881941,"rate":2436.84,"volume":2618578.0363269965},{"time":1623506400,"amount":1066.3871346782,"rate":2422.23,"volume":2583034.9092316669},{"time":1623510000,"amount":0.045,"rate":2393.81,"volume":107.72145},{"time":1623513600,"amount":5.3873315419,"rate":2392.75,"volume":12890.5375469253},{"time":1623517200,"amount":11.974819658,"rate":2412.97,"volume":28894.8805902517},{"time":1623520800,"amount":92.459366912,"rate":2422.98,"volume":224027.1968404377},{"time":1623524400,"amount":67.749,"rate":2410.71,"volume":163323.19179},{"time":1623528000,"amount":115.16709082,"rate":2404.61,"volume":276931.9382566467},{"time":1623531600,"amount":143.2390123975,"rate":2404.97,"volume":344485.5276457103},{"time":1623535200,"amount":119.8055541939,"rate":2381.75,"volume":285346.8787012265},{"time":1623538800,"amount":3159.601177426,"rate":2369.62,"volume":7487054.1420521373},{"time":1623542400,"amount":2619.062821438,"rate":2390.41,"volume":6260633.9589937096},{"time":1623546000,"amount":2053.2392926261,"rate":2411.91,"volume":4952228.382277891},{"time":1623549600,"amount":169.0942384364,"rate":2383.99,"volume":403118.973489904},{"time":1623553200,"amount":1030.4881132766,"rate":2335.81,"volume":2407024.4398726504},{"time":1623556800,"amount":0.0,"rate":2342.72,"volume":0.0}]
# data = [
#     {"time":1623470400, "amount":1, "rate":1.1},    #6/12
#     {"time":1623513788, "amount":2, "rate":1.2},    #6/12
#     {"time":1623600188, "amount":3, "rate":1.3},    #6/13
#     {"time":1623686588, "amount":4, "rate":1.4}     #6/14
#     ]
data = [
    {"time":1607954665, "amount":1, "rate":1.1},    #12/14/2020
    {"time":1608229389, "amount":1, "rate":1.1},    #12/17/2020
    {"time":1610907789, "amount":2, "rate":1.2},    #01/17/2021
    # {"time":1613586189, "amount":3, "rate":1.3},    #02/17/2021
    # {"time":1623686588, "amount":4, "rate":1.4}     #06/17/2021
    ]
data = pd.json_normalize(data)

df = ts.aggregate_timeseries(
    data = data,
    time_column='time',
    interval=ts.TimeseriesInterval.WEEKLY,
    columns=[
        ts.ColumnConfig(name='amount', 
                aggregate_method=ts.AggregateMethod.SUM, 
                na_fill_value=0.0,
                type=ts.ColumnType.float),
        ts.ColumnConfig(name='rate', 
                aggregate_method=ts.AggregateMethod.LAST, 
                na_fill_method=ts.NaInterpolationMethod.FORDWARD_FILL,
                type=ts.ColumnType.float)
    ],
    # start_timestamp=1623456000,
    # end_timestamp= 1623628800
)
print('~~~~final output~~~')
print(df)