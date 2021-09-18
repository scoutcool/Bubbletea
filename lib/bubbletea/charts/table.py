from functools import reduce
from typing import Optional
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

    COL_ROW_INDEX = "__row_index__"
    df[COL_ROW_INDEX] = "#"

    gb = GridOptionsBuilder.from_dataframe(
        df[
            reduce(
                lambda seq, cd: [*seq, cd["field"], cd["href"]]
                if "href" in cd
                else [*seq, cd["field"]],
                [
                    {
                        "field": COL_ROW_INDEX,
                    },
                    *columnDefs,
                ],
                [],
            )
        ],
    )

    cellsytle_jscode = JsCode(
        """
        function(params) {
            return {
                'font-family': 'monospace',
            }
        };
        """
    )

    gb.configure_column(
        COL_ROW_INDEX,
        headerName="#",
        valueGetter="node.rowIndex + 1",
        width=32,
        suppressMenu=True,
        pinned=True,
        lockPinned=True,
        sortable=False,
    )

    refresh_row_index_jscode = JsCode(
        """
        function(e) {
            e.api.refreshCells({columns: ["%s"], force: true, suppressFlash: true}); 
        }
        """
        % (COL_ROW_INDEX)
    )

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
            gb.configure_column(
                **columnDef,
                cellRenderer=link_jscode,
                cellStyle=cellsytle_jscode,
            )
        elif df[columnDef["field"]].dtypes.kind == "M":
            gb.configure_column(
                **columnDef, cellStyle=cellsytle_jscode, type=["dateColumnFilter"]
            )
        else:

            gb.configure_column(
                **columnDef,
                cellStyle=cellsytle_jscode,
            )

    # gb.configure_side_bar() # side bar is enterprise feature
    gb.configure_selection("disabled")
    gb.configure_pagination(
        paginationAutoPageSize=(pageSize == None), paginationPageSize=(pageSize or 10)
    )
    gb.configure_auto_height(False)
    gb.configure_grid_options(
        enableCellChangeFlash=True,
        onSortChanged=refresh_row_index_jscode,
        onFilterChanged=refresh_row_index_jscode,
    )
    gridOptions = gb.build()

    AgGrid(
        df,
        width="100%",
        gridOptions=gridOptions,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,  # Set it to True to allow jsfunction to be injected
    )
