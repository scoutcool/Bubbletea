
import json
import math
from typing import Dict, Union
import pandas as pd
from enum import Enum
from pandas.core.frame import DataFrame

from pandas.core.indexes.datetimes import date_range

class TimeseriesInterval(str, Enum):
    HOURLY = 'h',
    DAILY = 'd',
    WEEKLY = 'w',
    MONTHLY = 'm'
    QUARTER = 'Q'

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

class ColumnType(str, Enum):
    int = 'int32',
    str = 'str',
    float = 'float'

class ColumnConfig:
    def __init__(self, name:str, aggregate_method:AggregateMethod, na_fill_method:NaInterpolationMethod=None, na_fill_value=None, type=None) -> None:
        self.name = name
        self.aggregate_method = aggregate_method
        self.na_fill_method = na_fill_method
        self.na_fill_value = na_fill_value
        self.type = type
        pass

def is_json(candidate):
  try:
    json.loads(candidate)
  except ValueError as e:
    return False
  return True

def aggregate_timeseries(data:Union[Dict,list[Dict],DataFrame], time_column:str, interval:TimeseriesInterval, columns:list[ColumnConfig], **kwargs):
    df = None
    if isinstance(data, DataFrame):
        df = data
    else:
        df = pd.json_normalize(data)

    tmin = df[time_column].min()
    tmax = df[time_column].max()
    if 'start_timestamp' in kwargs:
        tmin = kwargs.get('start_timestamp',tmin)
    if 'end_timestamp' in kwargs:
        tmax = kwargs.get('end_timestamp',tmax)

    tmin = pd.to_datetime(math.floor(tmin / 3600) * 3600, unit='s')
    tmax = pd.to_datetime(math.ceil(tmax / 3600) * 3600, unit='s')

    df[time_column] = df[time_column].apply(lambda x: pd.to_datetime(x, unit='s'))
    
    idx=pd.date_range(start=tmin, end=tmax, freq=interval)
    # print(idx)
    
    df = df.set_index(time_column)
    
    result_df = None
    i = 0
    for c in columns:

        if c.type != None:
            df[c.name] = df[c.name].astype(c.type, copy=False, errors='ignore')

        r = df[[c.name]].resample(interval)
        f = getattr(r, c.aggregate_method)

        _df = f()
        _df.index.names = [time_column]
        if c.na_fill_method != None:
             _df = _df.fillna(method=c.na_fill_method)
             _df = _df.reindex(idx, method=c.na_fill_method)
        elif c.na_fill_value != None:
            _df = _df.fillna(c.na_fill_value)
            _df = _df.reindex(idx, fill_value=c.na_fill_value)
        else:
            _df=_df.reindex(idx)
        _df.index.names = [time_column]
        # print(f'\n\nafter redindex\n{_df}')
        if i == 0:
            result_df = _df
        else:
            result_df = pd.merge(result_df, _df, on=time_column, how="outer")
        i += 1
    return result_df





