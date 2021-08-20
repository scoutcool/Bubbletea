from pandas import DataFrame
from .base import _plot_simple

MARKER = "mark_bar"


def plot(df: DataFrame, **args):
    return _plot_simple(MARKER, df, **args)
