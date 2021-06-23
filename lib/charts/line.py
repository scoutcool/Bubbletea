from altair.vegalite.v4.schema.channels import Opacity
import streamlit as st
import altair as alt
from pandas import DataFrame
from functools import reduce

PALETTE = [
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
    ys: list[alt.Y] = [],
    palette=PALETTE,
    timeFormat="%b %d",
):
    frames = df.reset_index()

    x_config = {**DEFAULT_X, **x}
    ys_config = list(map(lambda y: {**DEFAULT_Y, **y}, ys))

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
        .mark_rule(color=palette[len(ys)])
        .encode(
            x=alt.X(**x_config),
            opacity=alt.condition(hover_selection, alt.value(1), alt.value(0)),
            tooltip=[
                x_config["field"],
                *list(map(lambda y_config: y_config["field"], ys_config)),
            ],
        )
        .add_selection(hover_selection)
        .add_selection(click_selection)
    )

    multi_rules = (
        alt.Chart(frames)
        .mark_rule(color=palette[len(ys)])
        .encode(
            x=alt.X(**x_config),
            opacity=alt.condition(click_selection, alt.value(1), alt.value(0)),
            tooltip=[
                x_config["field"],
                *list(map(lambda y_config: y_config["field"], ys_config)),
            ],
        )
        .transform_filter(click_selection)
    )

    def _get_line_chart(columnDef: alt.Y, index: int):
        base = alt.Chart(frames).encode(
            alt.X(
                title="",
                axis=alt.Axis(
                    values=frames["time"].tolist(),
                    format=timeFormat,
                    domain=False,
                    grid=False,
                ),
                scale=alt.Scale(nice={"interval": "day", "step": 1}),
                **x_config,
            ),
            alt.Y(
                axis=alt.Axis(
                    format=".2s",
                    titleColor=alt.Value(PALETTE[index]),
                    labelExpr="replace(datum.label, 'G', 'B')",
                ),
                **columnDef,
            ),
        )
        line = base.mark_line(color=PALETTE[index])

        # hover annotations
        hover_point = base.mark_point(color=PALETTE[index]).encode(
            y=alt.Y(
                axis=None,
                **columnDef,
            ),
            opacity=alt.condition(hover_selection, alt.value(1), alt.value(0)),
        )

        # hover_text = base.mark_text(
        #     align="left", dx=8, dy=-8, color=PALETTE[index]
        # ).encode(
        #     y=alt.Y(
        #         axis=None,
        #         **columnDef,
        #     ),
        #     text=alt.condition(hover_selection, columnDef, alt.value(" ")),
        # )

        # sticky annotations
        sticky_points = base.mark_point(color=PALETTE[index]).encode(
            y=alt.Y(
                axis=None,
                **columnDef,
            ),
            opacity=alt.condition(click_selection, alt.value(1), alt.value(0)),
        )

        # sticky_texts = base.mark_text(
        #     align="left", dx=8, dy=-8, color=PALETTE[index]
        # ).encode(
        #     y=alt.Y(
        #         axis=None,
        #         **columnDef,
        #     ),
        #     text=alt.condition(click_selection, columnDef, alt.value(" ")),
        # )

        return {
            "line": line,
            "annotations": [hover_point, sticky_points],
        }

    charts = []
    annotations = []

    for i, y in enumerate(ys_config):
        chart_result = _get_line_chart(y, i)
        charts.append(chart_result["line"])
        annotations += chart_result["annotations"]

    charts.append(hover_rule)
    charts.append(multi_rules)
    charts += annotations

    combined = alt.layer(*charts).resolve_scale(y="independent")

    st.altair_chart(
        combined.properties(height=400),
        use_container_width=True,
    )
