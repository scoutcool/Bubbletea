from functools import reduce
from typing import Optional
import streamlit as st
from pandas import DataFrame
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode


def plot(df: DataFrame, columnDefs: list[dict], pageSize: Optional[int]):
    """
    Table plotting params:

    - df (Required)

        DataFrame for the table

    - columnDef (Required)

        List of column definitions as defined in
        https://www.ag-grid.com/javascript-data-grid/column-definitions/

        A special field "href" is supported, it should be set to the name of the
        column in the DataFrame that holds the target URL to link to.


    - pageSize (Optional)

        Set to None for let Ag-grid to determine page size.

    """

    gb = GridOptionsBuilder.from_dataframe(
        df[
            reduce(
                lambda seq, cd: [*seq, cd["field"], cd["href"]]
                if "href" in cd
                else [*seq, cd["field"]],
                columnDefs,
                [],
            )
        ]
    )

    gb.configure_default_column(groupable=True)

    for columnDef in columnDefs:
        if "href" in columnDef:
            link_jscode = JsCode(
                """
                function(params) {
                    return `<a href="${params.data.%s}" target="_blank">${params.value}</a>`
                };
                """
                % (columnDef["href"])
            )
            gb.configure_column(field=columnDef["href"], hide=True)
            del columnDef["href"]
            gb.configure_column(**columnDef, cellRenderer=link_jscode)
        else:
            gb.configure_column(**columnDef)

    gb.configure_side_bar()
    gb.configure_selection("disabled")
    gb.configure_pagination(
        paginationAutoPageSize=(pageSize == None), paginationPageSize=(pageSize or 10)
    )
    gb.configure_grid_options(domLayout="normal")
    gridOptions = gb.build()

    AgGrid(
        df,
        width="100%",
        gridOptions=gridOptions,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,  # Set it to True to allow jsfunction to be injected
    )
