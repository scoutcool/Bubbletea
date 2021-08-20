import streamlit as st
import altair as alt
from altair.utils.schemapi import Undefined
from pandas import DataFrame, set_option, melt

from .heuristics import guess_x_config, guess_y_config, DEFAULT_X, DEFAULT_Y_EXTRA
from .colors import PALETTE

# Suppress SettingWithCopyWarning from pandas
set_option("mode.chained_assignment", None)


# WARNING: Mutates frames
def _calculate_x_config(frames: DataFrame, x: alt.X):
    guessed_x_config = guess_x_config(x, frames)
    x_config = guessed_x_config["config"]
    x_tooltip_config = {**x_config, "timeUnit": Undefined}
    x_axis_config = guessed_x_config["axis"]

    if "title" in x_config:
        frames[x_config["title"]] = frames[x_config["field"]]
        x_config["field"] = x_config["title"]
        del x_config["title"]

    return (x_config, x_tooltip_config, x_axis_config)


# WARNING: Mutates frames
def _calculate_ys_config(frames: DataFrame, ys):
    yExtra = {**ys}
    data = yExtra.pop("data")
    ys_config = list(map(lambda y: guess_y_config(y, frames), data))

    for yc in ys_config:
        if "title" in yc["config"]:
            frames[yc["config"]["title"]] = frames[yc["config"]["field"]]

    return ys_config, yExtra


def _get_annotations(
    frames: DataFrame,
    base: alt.Chart,
    color,
    x_config,
    x_axis_config,
    x_tooltip_config,
    ys_config,
    yExtra=DEFAULT_Y_EXTRA,
):
    stack = yExtra.pop("stack") if "stack" in yExtra else False

    hover_selection = alt.selection(
        type="single",
        nearest=True,
        on="mouseover",
        fields=[x_config["field"]],
        empty="none",
    )
    click_selection = alt.selection_multi(
        nearest=True,
        on="click",
        fields=[x_config["field"]],
        empty="none",
    )

    # Draw a rule at the location of the selection
    hover_rule = (
        alt.Chart(frames)
        .mark_rule(color=color)
        .encode(
            x=alt.X(
                **x_config,
                axis=alt.Axis(
                    **x_axis_config,
                ),
            ),
            opacity=alt.condition(hover_selection, alt.value(1), alt.value(0)),
            tooltip=[
                alt.StringFieldDefWithCondition(
                    **x_tooltip_config, format=x_axis_config["format"]
                ),
                *list(
                    map(
                        lambda y_config: y_config["config"]["title"]
                        or y_config["config"]["field"],
                        ys_config,
                    )
                ),
            ],
        )
        .add_selection(hover_selection)
        .add_selection(click_selection)
    )

    multi_rules = (
        alt.Chart(frames)
        .mark_rule(color=color, xOffset=0.5)
        .encode(
            x=alt.X(
                **x_config,
                axis=alt.Axis(
                    **x_axis_config,
                ),
            ),
            opacity=alt.condition(click_selection, alt.value(1), alt.value(0)),
        )
        .transform_filter(click_selection)
    )

    if base == None:
        return hover_rule, multi_rules

    hover_point = base.mark_point().encode(
        y=alt.Y("value:Q", stack=stack),
        opacity=alt.condition(hover_selection, alt.value(1), alt.value(0)),
    )

    sticky_points = base.mark_point().encode(
        y=alt.Y("value:Q", stack=stack),
        opacity=alt.condition(click_selection, alt.value(1), alt.value(0)),
    )

    return hover_rule, multi_rules, hover_point, sticky_points


def _get_all_config(frames, x, ys):

    x_config, x_tooltip_config, x_axis_config = _calculate_x_config(frames, x)
    ys_config_all, yExtra = _calculate_ys_config(frames, ys)
    return x_config, x_tooltip_config, x_axis_config, ys_config_all, yExtra


def _plot_single(
    marker: str,
    df: DataFrame,
    x: alt.X = DEFAULT_X,
    y: "list[alt.Y]" = [],
    palette: list[str] = PALETTE,
    legend="right",  # could be 'left', 'right', 'none',
    orient="left",  # or 'right'
):
    frames = df.reset_index()

    x_config, x_tooltip_config, x_axis_config, ys_config_all, yExtra = _get_all_config(
        frames, x, y
    )

    legend_selection = alt.selection_multi(fields=["variable"], bind="legend")

    melted = melt(
        frames,
        id_vars=[x_config["field"]],
        value_vars=map(
            lambda y_config: y_config["config"]["title"]
            if "title" in y_config["config"]
            else y_config["config"]["field"],
            ys_config_all,
        ),
    )

    base = alt.Chart(melted).encode(
        alt.X(
            title="",
            **x_config,
            axis=alt.Axis(
                domain=False,
                grid=False,
                **x_axis_config,
            ),
        ),
        alt.Y(
            "value:Q",
            **yExtra,
            axis=alt.Axis(
                grid=False,
                orient=orient,
                **ys_config_all[0]["axis"],
            ),
        ),
        color=(
            alt.Color(
                "variable:N",
                legend=(
                    None if legend == "none" else alt.Legend(title="", orient=legend)
                ),
                scale=alt.Scale(range=palette[1:]),
            )
        ),
        # column=(
        #     alt.Column("variable:N", spacing=5, header=alt.Header(labelOrient="bottom"))
        # ),
        opacity=alt.condition(legend_selection, alt.value(0.75), alt.value(0.3)),
    )

    main = getattr(base, marker)(
        strokeJoin="round",
    ).add_selection(legend_selection)

    return main, base


def _plot_annotations(
    df: DataFrame,
    base: alt.Chart,
    x: alt.X = DEFAULT_X,
    y: "list[alt.Y]" = [],
    palette: list[str] = PALETTE,
):
    frames = df.reset_index()

    x_config, x_tooltip_config, x_axis_config, ys_config_all, yExtra = _get_all_config(
        frames, x, y
    )
    return _get_annotations(
        frames,
        base,
        palette[0],
        x_config,
        x_axis_config,
        x_tooltip_config,
        ys_config_all,
        yExtra,
    )


def _plot_simple(
    marker: str,
    df: DataFrame,
    x: alt.X = DEFAULT_X,
    y=None,
    palette=PALETTE,
    title: str = None,
    height: int = 400,
    legend="right",  # could be 'left', 'right', 'none',
):
    if title != None:
        st.subheader(title)

    chart, base = _plot_single(marker, df, y=y, x=x, palette=palette, legend=legend)
    annotations = _plot_annotations(df=df, base=base, y=y, x=x, palette=palette)

    st.altair_chart(
        alt.layer(chart, *annotations).properties(height=height),
        use_container_width=True,
    )


def _plot_combo(
    df: DataFrame,
    x: alt.X = DEFAULT_X,
    yLeft={},
    yRight={},
    palette=PALETTE,
    title: str = None,
    height: int = 400,
    legend="right",  # could be 'left', 'right', 'none',
    defaultMarker="mark_line",
):

    if title != None:
        st.subheader(title)

    leftData = yLeft.pop("data")
    rightData = yRight.pop("data")

    leftMarker = yLeft.pop("marker") if "marker" in yLeft else defaultMarker
    rightMarker = yRight.pop("marker") if "marker" in yRight else defaultMarker

    left, _ = _plot_single(
        leftMarker,
        df,
        x=x,
        y={"data": leftData, **yLeft},
        palette=palette,
        legend=legend,
        orient="left",
    )

    right, _ = _plot_single(
        rightMarker,
        df,
        x=x,
        y={"data": rightData, **yRight},
        palette=palette,
        legend=legend,
        orient="right",
    )

    annotations = _plot_annotations(
        df=df,
        base=None,
        y={"title": "", "data": leftData + rightData},
        x=x,
        palette=palette,
    )

    st.altair_chart(
        alt.layer(
            left,
            right,
            *annotations,
        )
        .properties(height=height)
        .resolve_scale(y="independent"),
        use_container_width=True,
    )
