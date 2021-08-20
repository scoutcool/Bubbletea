from pandas import DataFrame
from .base import _plot_simple

MARKER = "mark_area"


def plot(df: DataFrame, **args):
    return _plot_simple(MARKER, df, **args)
