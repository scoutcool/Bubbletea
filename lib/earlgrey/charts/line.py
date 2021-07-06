import datetime
import streamlit as st
import altair as alt
from pandas import DataFrame, DatetimeIndex, to_datetime, to_numeric
from pandas.api.types import is_numeric_dtype

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
        col_as_datetime = to_datetime(column, errors="raise", unit="s")
        return [
            col_as_datetime,
            {"type": "temporal", "axis": {"format": "%b %d"}},
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


def plot(
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
                x_config["field"],
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
        .mark_rule(color=palette[0])
        .encode(
            x=alt.X(
                **x_config,
                axis=alt.Axis(
                    **x_axis_config,
                ),
            ),
            opacity=alt.condition(click_selection, alt.value(1), alt.value(0)),
            tooltip=[
                x_config["field"],
                *list(
                    map(
                        lambda y_config: y_config["config"]["title"]
                        or y_config["config"]["field"],
                        ys_config_all,
                    )
                ),
            ],
        )
        .transform_filter(click_selection)
    )

    def _get_line_chart(columnDef: alt.Y, axisDef: alt.Axis, index: int, orient="left"):
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
            chart_result = _get_line_chart(y["config"], y["axis"], i)
            charts["yLeft"].append(chart_result["line"])
            annotations["yLeft"] += chart_result["annotations"]

        combined_charts.append(
            alt.layer(*charts["yLeft"], *annotations["yLeft"]).properties(height=height)
        )

    if len(yRight) > 0:
        for i, y in enumerate(ys_config_right):
            chart_result = _get_line_chart(
                y["config"], y["axis"], i + len(ys_config_left), "right"
            )
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
