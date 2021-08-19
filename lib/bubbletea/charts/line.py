from pandas import DataFrame
from .base import legacy_plot, _plot_simple

MARKER = "mark_line"


def legacy_plot_line(df: DataFrame, **args):
    legacy_plot(MARKER, df, **args)


def plot(df: DataFrame, **args):
    return _plot_simple(MARKER, df, **args)
