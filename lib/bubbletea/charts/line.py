from pandas import DataFrame
from .base import _plot_simple

MARKER = "mark_line"


def plot(df: DataFrame, **args):
    return _plot_simple(MARKER, df, **args)
