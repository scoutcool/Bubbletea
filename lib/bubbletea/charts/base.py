from altair.vegalite.v4.api import value
from altair.vegalite.v4.schema.channels import Opacity
from altair.vegalite.v4.schema.core import StringFieldDefWithCondition
import streamlit as st
import altair as alt
from pandas import DataFrame, melt

from .heuristics import guess_x_config, guess_y_config, DEFAULT_X
from .colors import PALETTE


def plot(
    marker: str,
    df: DataFrame,
    x: alt.X = DEFAULT_X,
    ys: "list[alt.Y]" = None,
    yLeft: "list[alt.Y]" = [],
    yRight: "list[alt.Y]" = [],
    palette=PALETTE,
    height: int = 400,
    title: str = None,
    legend="right",  # could be 'left', 'right', 'none',
):
    """Plot a line chart for the given data frame.

    Parameters
    ----------
    df : pd.DataFrame (required)
        The data frame to plot a line chart with.

    x : altair.X (optional)
        Configuration for altair X encoding. Default to {"field": "time", "type": "temporal"}

    ys : List of altair.Y (required)
        Configurations for altair Y encoding. E.g. {"field": "amount", "type": "quantitative"}

        "field" is required, "type" and other formatting options will be inferred from the data on the best-effort basis.

        `ys` will overwrite `yLeft` if both are defined.

    yLeft : List of altair.Y (optional)
        Configurations for left-side altair Y encoding.

    yRight : List of altair.Y (optional)
        Configurations for right-side altair Y encoding.

    palette: List of colors (optional)
        Color palette for data series, wil be used in order.

    height: int (optional, default to 400)
        Chart height in pixels.

    title: str (optional)
        Chart title.

    legend: enum[left, right, none] (optional, default to left)
        Chart legend setting.

    Returns
    -------
    line_chart: altair.Chart
        The line chart plotted.
    """
    if ys == None and len(yLeft) == 0 and len(yRight) == 0:
        raise "Must define ys, yLeft, or yRight"

    if ys != None and len(ys) != 0:
        yLeft = ys

    is_dual_y = len(yLeft) > 0 and len(yRight) > 0

    frames = df.reset_index()

    guessed_x_config = guess_x_config(x, frames)
    x_config = guessed_x_config["config"]
    x_tooltip_config = x_config.copy()
    del x_tooltip_config["timeUnit"]
    x_axis_config = guessed_x_config["axis"]

    ys_config_left = list(map(lambda y: guess_y_config(y, frames), yLeft))
    ys_config_right = list(map(lambda y: guess_y_config(y, frames), yRight))
    ys_config_all = ys_config_left + ys_config_right

    if title != None:
        st.subheader(title)

    # Add additional columns
    if "title" in x_config:
        frames[x_config["title"]] = frames[x_config["field"]]
        x_config["field"] = x_config["title"]
        del x_config["title"]
    for yc in ys_config_all:
        if "title" in yc["config"]:
            frames[yc["config"]["title"]] = frames[yc["config"]["field"]]

    # Create a selection that chooses the nearest point & selects based on x-value
    hover_selection = alt.selection(
        type="single",
        nearest=True,
        on="mouseover",
        fields=[x_config["field"]],
        empty="none",
    )
    click_selection = alt.selection_multi(
        # nearest=True,
        on="click",
        fields=[x_config["field"]],
        empty="none",
    )

    # Draw a rule at the location of the selection
    hover_rule = (
        alt.Chart(frames)
        .mark_rule(color=palette[0])
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
                        ys_config_all,
                    )
                ),
            ],
        )
        .add_selection(hover_selection)
        .add_selection(click_selection)
    )

    multi_rules = (
        alt.Chart(frames)
        .mark_rule(color=palette[0], xOffset=0.5)
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

    def _get_base_chart(columnDef: alt.Y, axisDef: alt.Axis, index: int, orient="left"):

        column_label = columnDef["field"] + "-label"
        frames[column_label] = columnDef["title"] or columnDef["field"]
        color = palette[index + 1]

        base = alt.Chart(frames).encode(
            alt.X(
                title="",
                # scale=alt.Scale(nice={"interval": "day", "step": 1}),
                **x_config,
                axis=alt.Axis(
                    # values=frames[x_config["field"]].tolist(),
                    domain=False,
                    grid=False,
                    **x_axis_config,
                ),
            ),
            alt.Y(
                axis=alt.Axis(
                    titleColor=alt.Value(color),
                    grid=(not is_dual_y),
                    orient=orient,
                    **axisDef,
                ),
                **columnDef,
            ),
            color=(
                alt.Color(
                    field=column_label,
                    type="ordinal",
                    legend=(
                        None
                        if legend == "none"
                        else alt.Legend(title="", orient=legend)
                    ),
                    scale=alt.Scale(range=palette[1:]),
                )
            ),
        )
        main = getattr(base, marker)(
            color=color,
            strokeJoin="round",
            opacity=(0.75 if len(ys_config_all) > 1 else 1.0),
        )

        # hover annotations
        hover_point = base.mark_point(color=color).encode(
            y=alt.Y(
                axis=alt.Axis(title=""),
                **columnDef,
            ),
            opacity=alt.condition(hover_selection, alt.value(1), alt.value(0)),
        )

        # sticky annotations
        sticky_points = base.mark_point(color=color).encode(
            y=alt.Y(
                axis=alt.Axis(title=""),
                **columnDef,
            ),
            opacity=alt.condition(click_selection, alt.value(1), alt.value(0)),
        )

        return {
            "main": main,
            "annotations": [] if marker == "mark_bar" else [hover_point, sticky_points],
        }

    charts = {"yLeft": [], "yRight": []}
    annotations = {"yLeft": [], "yRight": []}
    combined_charts = []

    if len(yLeft) > 0:
        for i, y in enumerate(ys_config_left):
            chart_result = _get_base_chart(y["config"], y["axis"], i)
            charts["yLeft"].append(chart_result["main"])
            annotations["yLeft"] += chart_result["annotations"]

        combined_charts.append(
            alt.layer(*charts["yLeft"], *annotations["yLeft"]).properties(height=height)
        )

    if len(yRight) > 0:
        for i, y in enumerate(ys_config_right):
            chart_result = _get_base_chart(
                y["config"], y["axis"], i + len(ys_config_left), "right"
            )
            charts["yRight"].append(chart_result["main"])
            annotations["yRight"] += chart_result["annotations"]

        combined_charts.append(
            alt.layer(*charts["yRight"], *annotations["yRight"]).properties(
                height=height
            )
        )

    combined = (
        alt.layer(*combined_charts, hover_rule, multi_rules)
        .resolve_scale(y="independent")
        .properties(height=height)
    )

    st.altair_chart(
        combined,
        use_container_width=True,
    )
