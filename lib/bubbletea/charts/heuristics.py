import datetime
import streamlit as st
import altair as alt
from pandas import DataFrame, to_datetime, to_numeric
from pandas.api.types import is_numeric_dtype

DEFAULT_X: alt.X = {"field": "time", "type": "temporal"}
DEFAULT_Y: alt.Y = {
    "type": "quantitative",
    "stack": False,
    "scale": alt.Scale(zero=False),
}

FMT_DATE = "%Y/%m/%d"  # yyyy/mm/dd
FMT_FULL_DATETIME = "%Y/%m/%d %I:%M %p"  # yyyy/mm/dd HH:MM a/pm


@st.cache
def get_min_max_date():
    # valid date time is today +/- 20 years
    return [
        int((datetime.datetime.now() - datetime.timedelta(days=20 * 365)).timestamp()),
        int((datetime.datetime.now() + datetime.timedelta(days=20 * 365)).timestamp()),
    ]


[MIN_DATETIME, MAX_DATETIME] = get_min_max_date()


def is_large(df: DataFrame):
    return df.apply(lambda c: int(c) > 1e5).any()


def is_too_large(df: DataFrame):
    return df.apply(lambda c: int(c) > 1e12).any()


def guess_time_axis(df: DataFrame):
    fmt = FMT_FULL_DATETIME if df.apply(lambda d: d.hour != 0).any() else FMT_DATE
    return {"format": fmt, "labelOverlap": "greedy"}


def process_field(df: DataFrame, fieldName: str):
    column = df[fieldName]
    original_dtype = column.dtype

    if original_dtype == "object":
        try_numerify = column.apply(lambda s: to_numeric(s, errors="coerce"))
        if try_numerify.notnull().all():
            column = try_numerify

    if is_numeric_dtype(column):
        axis_config = {
            "format": ".2f",
        }

        if is_large(column):
            axis_config = {
                "format": ".2s",
                "labelExpr": "replace(datum.label, 'G', 'B')",
            }

        if is_too_large(column):
            axis_config = {
                "format": ".2e",
            }

        if (column < MIN_DATETIME).any() or (column > MAX_DATETIME).any():
            return [
                column,
                {"type": "quantitative", "axis": axis_config},
            ]

        try:
            timestamp_col_as_datetime = to_datetime(column, errors="raise", unit="s")
            return [
                timestamp_col_as_datetime,
                {
                    "type": "temporal",
                    "axis": guess_time_axis(timestamp_col_as_datetime),
                },
            ]
        except:
            print("cannot convert to date")

    try:
        general_col_as_datetime = to_datetime(
            column, errors="raise", infer_datetime_format=True
        )

        return [
            general_col_as_datetime,
            {
                "type": "temporal",
                "axis": guess_time_axis(general_col_as_datetime),
            },
        ]
    except:
        print("cannot convert to date")

    return [column, {"type": "nominal", "axis": {}}]


def guess_x_config(x: alt.X, df: DataFrame):
    [col, guessed_x_config] = process_field(df, x["field"])
    df[x["field"]] = col

    axis_config = guessed_x_config["axis"]
    del guessed_x_config["axis"]

    return {
        "config": {
            # base: default
            **DEFAULT_X,
            # guess field type
            **guessed_x_config,
            # input should override heuristics when available
            **x,
        },
        "axis": axis_config,
    }


def guess_y_config(y: alt.Y, df: DataFrame):
    [col, guessed_y_config] = process_field(df, y["field"])
    df[y["field"]] = col

    axis_config = guessed_y_config["axis"]
    del guessed_y_config["axis"]

    return {
        "config": {
            # base: default
            **DEFAULT_Y,
            # guess field type
            **guessed_y_config,
            # input should override heuristics when available
            **y,
        },
        "axis": axis_config,
    }
