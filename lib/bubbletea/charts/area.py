from pandas import DataFrame
from .base import plot as base_plot

def plot(df: DataFrame, **args):
    return base_plot("mark_area", df, **args)
