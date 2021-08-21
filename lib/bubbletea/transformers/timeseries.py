import math
import datetime
from typing import Dict, Union
import pandas as pd
from enum import Enum
from decimal import Decimal
from pandas.core.frame import DataFrame

from pandas.core.indexes.datetimes import DatetimeIndex


class TimeseriesInterval(str, Enum):
    HOURLY = ("H",)
    DAILY = ("D",)
    WEEKLY = ("W-SUN",)
    MONTHLY = "MS"


class AggregateMethod(str, Enum):
    MEAN = ("mean",)
    SUM = ("sum",)
    FIRST = ("first",)
    LAST = ("last",)
    MEDIAN = ("median",)
    MIN = ("min",)
    MAX = ("max",)
    COUNT = "count"


class NaInterpolationMethod(str, Enum):
    FORDWARD_FILL = ("ffill",)
    BACKWARD_FILL = ("bfill",)


class ColumnType(str, Enum):
    int = ("int32",)
    str = ("str",)
    float = ("float64",)
    bigdecimal = ("float64",)


class ColumnConfig:
    def __init__(
        self,
        name: str,
        aggregate_method: AggregateMethod,
        type:ColumnType=None,
        na_fill_method: NaInterpolationMethod = None,
        na_fill_value=None
    ) -> None:
        self.name = name
        self.aggregate_method = aggregate_method
        self.na_fill_method = na_fill_method
        self.na_fill_value = na_fill_value
        self.type = type
        pass


def _to_df(data: Union[Dict, "list[Dict]", DataFrame]):
    return data if (isinstance(data, DataFrame)) else (pd.json_normalize(data))


def _last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    return next_month - datetime.timedelta(days=next_month.day)


def beta_aggregate_timeseries(
    data: Union[Dict, "list[Dict]", DataFrame],
    time_column: str,
    interval: TimeseriesInterval,
    columns: "list[ColumnConfig]",
    start_timestamp: int = None,
    end_timestamp: int = None,
):
    df = _to_df(data)
    if df.index.name == time_column:
        df = df.reset_index()
    if len(df) == 0:
        return df

    tmin = df[time_column].min()
    tmax = df[time_column].max()
    if hasattr(tmin, "timestamp"):
        tmin = tmin.timestamp()
    if hasattr(tmax, "timestamp"):
        tmax = tmax.timestamp()

    if start_timestamp != None:
        tmin = start_timestamp
    if end_timestamp != None:
        tmax = end_timestamp
    

    unit = 's'
    if len(str(tmin)) == 13:
        tmin /= 1000
        tmax /= 1000
        unit = 'ms'

    if interval == TimeseriesInterval.HOURLY:
        tmin = pd.to_datetime(math.floor(tmin / 3600) * 3600, unit="s")
        tmax = pd.to_datetime(math.ceil(tmax / 3600) * 3600, unit="s")
    else:
        tmin = pd.to_datetime(math.floor(tmin / 86400) * 86400, unit="s")
        tmax = pd.to_datetime(math.ceil(tmax / 86400) * 86400, unit="s")

        if interval == TimeseriesInterval.WEEKLY:
            if tmin.weekday() != 0:
                tmin += pd.offsets.Day(6 - tmin.weekday())
            if tmax.weekday() != 0:
                tmax += pd.offsets.Day(6 - tmax.weekday())
        elif interval == TimeseriesInterval.MONTHLY:
            tmin = tmin.replace(day=1)
            tmax = _last_day_of_month(tmax)

    # print(f'time frame {tmin} - {tmax}')
    # print(df[time_column].dtype)
    if not isinstance(df[time_column], DatetimeIndex):
        df[time_column] = pd.to_datetime(df[time_column], unit=unit)

    df = df.set_index(time_column)
    # print(df)

    result_df = None
    i = 0
    for c in columns:
        if c.type != None:
            if c.type == ColumnType.bigdecimal:
                df[c.name] = df[c.name].astype('float64', copy=False, errors="ignore")
            else:
                df[c.name] = df[c.name].astype(c.type, copy=False, errors="ignore")
                
        r = df[[c.name]].resample(interval)
        f = getattr(r, c.aggregate_method)

        _df = f()
        _df.index.names = [time_column]
        # print(f'\n\naggregated\n{_df}')

        idx = pd.date_range(start=tmin, end=tmax, freq=interval)
        if c.na_fill_method != None:
            _df = _df.fillna(method=c.na_fill_method)
            _df = _df.reindex(idx, method=c.na_fill_method)
        elif c.na_fill_value != None:
            _df = _df.fillna(c.na_fill_value)
            _df = _df.reindex(idx, fill_value=c.na_fill_value)
        else:
            _df = _df.reindex(idx)
        _df.index.names = [time_column]

        if interval == TimeseriesInterval.WEEKLY:
            _df = _df.reset_index()
            _df[time_column] = _df[time_column].apply(lambda x: x - pd.offsets.Day(6))
            # print(f'\n\nshift 6 days ahead:\n{_df}')
            _df = _df.set_index(time_column)

        # print(f'\n\nafter redindex\n{_df}')
        if i == 0:
            result_df = _df
        else:
            result_df = pd.merge(result_df, _df, on=time_column, how="outer")
        i += 1
    return result_df


def beta_aggregate_groupby(
    data: Union[Dict, "list[Dict]", DataFrame],
    by_column: str,
    columns: "list[ColumnConfig]",
):
    df = _to_df(data)
    if len(df) == 0:
        return df
    params = dict()
    for c in columns:
        if c.type != None:
            if c.type == ColumnType.bigdecimal:
                df[c.name] = df[c.name].apply(lambda x: Decimal(x))
            else:
                df[c.name] = df[c.name].astype(c.type, copy=False, errors="ignore")
        params[c.name] = pd.NamedAgg(column=c.name, aggfunc=c.aggregate_method)

    df = df.groupby(by_column).agg(**params)
    for c in columns:
        if c.na_fill_method != None:
            df[c.name] = df[c.name].fillna(method=c.na_fill_method)
        elif c.na_fill_value != None:
            df[c.name] = df[c.name].fillna(c.na_fill_value)
    return df
