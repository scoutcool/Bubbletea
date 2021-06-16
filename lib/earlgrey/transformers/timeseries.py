
import json
import math
import pandas as pd
from enum import Enum

from pandas.core.indexes.datetimes import date_range

class TimeseriesInterval(str, Enum):
    HOURLY = 'H',
    DAILY = 'd',
    WEEKLY = 'W',
    MONTHLY = 'M'

class AggregateMethod(str, Enum):
    MEAN = 'mean',
    SUM = 'sum',
    FIRST = 'first',
    LAST = 'last',
    MEDIAN = 'median',
    MIN = 'min',
    MAX = 'max',
    COUNT = 'count'


class NaInterpolationMethod(str, Enum):
    FORDWARD_FILL='ffill',
    BACKWARD_FILL='bfill',

class ColumnConfig:
    def __init__(self, name:str, aggregateMethod:AggregateMethod, naFillMethod:NaInterpolationMethod=None, naFillValue=None) -> None:
        self.name = name
        self.aggregateMethod = aggregateMethod
        self.naFillMethod = naFillMethod
        self.naFillValue = naFillValue
        pass

def aggregate_timeseries(data:json, timeColumn:str, interval:TimeseriesInterval, columnsToAggregate:list[ColumnConfig], **kwargs):
    df = pd.json_normalize(data)
    tmin = math.floor(df[timeColumn].min()/3600) * 3600
    tmin = kwargs.get('startTimestamp',tmin)
    tmax = math.ceil(df[timeColumn].max()/3600) * 3600
    tmax = kwargs.get('endTimestamp',tmax)
    tmin = pd.to_datetime(tmin, unit='s')
    tmax = pd.to_datetime(tmax, unit='s')

    df[timeColumn] = df[timeColumn].apply(lambda x: pd.to_datetime(x, unit='s'))
    
    idx=pd.date_range(start=tmin, end=tmax, freq=interval)
    print(idx)
    
    df = df.set_index(timeColumn)

    columns = []
    for c in columnsToAggregate:
        columns.append(c.name)
    result_df = None
    i = 0
    for c in columnsToAggregate:
        r = df[[c.name]].resample(interval)
        f = getattr(r, c.aggregateMethod)

        # print(f"\n\n??? {c.name} {c.aggregateMethod} {c.naFillValue}")
        _df = f()
        _df.index.names = [timeColumn]
        if c.naFillMethod != None:
             _df = _df.fillna(method=c.naFillMethod)
             _df = _df.reindex(idx, method=c.naFillMethod)
        elif c.naFillValue != None:
            _df = _df.fillna(c.naFillValue)
            _df = _df.reindex(idx, fill_value=c.naFillValue)
        else:
            _df=_df.reindex(idx)
        _df.index.names = [timeColumn]
        # print(f'\n\nafter redindex\n{_df}')
        if i == 0:
            result_df = _df
        else:
            result_df = pd.merge(result_df, _df, on=timeColumn, how="outer")
        i += 1
    return result_df





