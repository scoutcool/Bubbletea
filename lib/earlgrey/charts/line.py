from altair.utils.schemapi import Undefined
from altair.vegalite.v4.schema.channels import Opacity
import streamlit as st
import altair as alt
from pandas import DataFrame
from functools import reduce

PALETTE = [
    "#FF3333",
    "#66D2C3",
    "#2E678E",
    "#F9965B",
    "#4CAAF7",
    "#E3EF89",
    "#8D6DCF",
    "#849AD9",
    "#EF6461",
    "#009FB7",
    "#FED766",
    "#728FE6",
    "#62C1D6",
    "#CF74BA",
    "#7AD07C",
    "#F7AA7C",
    "#39AD92",
    "#74BA7F",
    "#E56A99",
    "#7196BE",
    "#D08D66",
]

DEFAULT_X: alt.X = {"field": "time", "type": "temporal"}
DEFAULT_Y: alt.Y = {
    "type": "quantitative",
    "stack": False,
    "scale": alt.Scale(zero=False),
}


def plot(
    df: DataFrame,
    x: alt.X = DEFAULT_X,
    yLeft: "list[alt.Y]" = [],
    yRight: "list[alt.Y]" = [],
    palette=PALETTE,
    height: int = 400,
    timeFormat="%b %d",
    title: str = None,
    legend="right",  # could be 'left', 'right', 'none'
):
    frames = df.reset_index()

    x_config = {**DEFAULT_X, **x}
    ys_config_left = list(map(lambda y: {**DEFAULT_Y, **y}, yLeft))
    ys_config_right = list(map(lambda y: {**DEFAULT_Y, **y}, yRight))
    ys_config_all = ys_config_left + ys_config_right

    if title != None:
        st.subheader(title)

    # Add additional columns
    if "title" in x_config:
        frames[x_config["title"]] = frames[x_config["field"]]
        x_config["field"] = x_config["title"]
        del x_config["title"]
    for yc in ys_config_all:
        if "title" in yc:
            frames[yc["title"]] = frames[yc["field"]]

    # Create a selection that chooses the nearest point & selects based on x-value
    hover_selection = alt.selection(
        type="single",
        nearest=True,
        on="mouseover",
        fields=[x_config["field"]],
        empty="none",
    )
    click_selection = alt.selection_multi(
        nearest=True, on="click", fields=[x_config["field"]], empty="none"
    )

    # Draw a rule at the location of the selection
    hover_rule = (
        alt.Chart(frames)
        .mark_rule(color=palette[0])
        .encode(
            x=alt.X(**x_config),
            opacity=alt.condition(hover_selection, alt.value(1), alt.value(0)),
            tooltip=[
                x_config["field"],
                *list(
                    map(
                        lambda y_config: y_config["title"] or y_config["field"],
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
        .mark_rule(color=palette[0])
        .encode(
            x=alt.X(**x_config),
            opacity=alt.condition(click_selection, alt.value(1), alt.value(0)),
            tooltip=[
                x_config["field"],
                *list(
                    map(
                        lambda y_config: y_config["title"] or y_config["field"],
                        ys_config_all,
                    )
                ),
            ],
        )
        .transform_filter(click_selection)
    )

    def _get_line_chart(columnDef: alt.Y, index: int, orient="left"):
        column_label = columnDef["field"] + "-label"
        frames[column_label] = columnDef["title"] or columnDef["field"]
        color = palette[index + 1]

        base = alt.Chart(frames).encode(
            alt.X(
                title="",
                axis=alt.Axis(
                    values=frames[x_config["field"]].tolist(),
                    format=timeFormat,
                    domain=False,
                    grid=False,
                ),
                # scale=alt.Scale(nice={"interval": "day", "step": 1}),
                **x_config,
            ),
            alt.Y(
                axis=alt.Axis(
                    format=".2s",
                    titleColor=alt.Value(color),
                    labelExpr="replace(datum.label, 'G', 'B')",
                    grid=False,
                    orient=orient,
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
        line = base.mark_line(color=color, strokeJoin="round")

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
            "line": line,
            "annotations": [hover_point, sticky_points],
        }

    charts = {"yLeft": [], "yRight": []}
    annotations = {"yLeft": [], "yRight": []}
    combined_charts = []

    if len(yLeft) > 0:
        for i, y in enumerate(ys_config_left):
            chart_result = _get_line_chart(y, i)
            charts["yLeft"].append(chart_result["line"])
            annotations["yLeft"] += chart_result["annotations"]

        combined_charts.append(
            alt.layer(*charts["yLeft"], *annotations["yLeft"]).properties(height=height)
        )

    if len(yRight) > 0:
        for i, y in enumerate(ys_config_right):
            chart_result = _get_line_chart(y, i + len(ys_config_left), "right")
            charts["yRight"].append(chart_result["line"])
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
