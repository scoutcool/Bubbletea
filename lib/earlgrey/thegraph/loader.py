import streamlit as st
import requests
import json
import numpy as np
import pandas as pd
import concurrent.futures
from streamlit.report_thread import add_report_ctx
from graphql import parse, print_ast, ArgumentNode, NameNode, IntValueNode, FieldNode, SelectionSetNode, ObjectValueNode, StringValueNode, ObjectFieldNode, EnumValueNode
import earlgrey.thegraph.schema_utils as schema_utils

ITEMS_PER_PAGE = 1000

class TheGraphEntity:
    def __init__(self, node) -> None:
        self.limit = np.Infinity
        self.name = node.name.value
        self.bypassPagination = False
        
        self.__build_pagination_query__(node)
        pass

    def __build_pagination_query__(self, node):
        iArguments = []
        pArguments = []
        whereArg = None
        for a in node.arguments:
            if(a.name.value == 'where'):
                whereArg = a
                iArguments.append(a)
            elif a.name.value == 'bypassPagination':
                self.bypassPagination = bool(a.value.value)
            else:
                iArguments.append(a)
                pArguments.append(a)
        if not self.bypassPagination:
            self.initialQuery = print_ast(node)
            return

        if whereArg == None:
            ast = parse("""{stuff(where:{id_gt:"__LASTID__"}){id}}""", no_location=True)
            whereArg = ast.definitions[0].selection_set.selections[0].arguments[0]
        else:
            fields = whereArg.value.fields.copy()
            fields.append(ObjectFieldNode(name=NameNode(value='id_gt'),value=StringValueNode(value='__LASTID__')))
            whereArg = ArgumentNode(name=NameNode(value='where'), value=ObjectValueNode(fields=fields))

        pArguments.append(whereArg)
        iArguments.append(ArgumentNode(name=NameNode(value='first'), value=IntValueNode(value=ITEMS_PER_PAGE)))
        pArguments.append(ArgumentNode(name=NameNode(value='first'), value=IntValueNode(value=ITEMS_PER_PAGE)))

        selections = node.selection_set.selections.copy()
        selections.append(FieldNode(name=NameNode(value='id')))
        selectionSet = SelectionSetNode(selections=selections)
        
        iNode = FieldNode(directives=node.directives, alias=node.alias, name=node.name, arguments=iArguments, selection_set=selectionSet)
        pNode = FieldNode(directives=node.directives, alias=node.alias, name=node.name, arguments=pArguments, selection_set=selectionSet)

        # print(print_ast(iNode))
        # print(print_ast(pNode))
        self.initialQuery = print_ast(iNode)
        self.paginationQuery = print_ast(pNode)


    def __str__(self):
        keys = ['name', 'bypassPagination', 'initialQuery', 'paginationQuery']
        msg = ''
        for k in keys:
            if(hasattr(self, k)):
                msg += f'{k}: {getattr(self, k)} \n'
        msg += '\n'
        return msg
    def __repr__(self):
        return str(self) 

class SubgraphLoader:
    def __init__(self, subgraphUrl:str) -> None:
        self.subgraphUrl = subgraphUrl
        self.types = None
        self.types = self.__load_schema()
        pass
    
    @st.cache(show_spinner=False)
    def __load_schema(self):
        query = schema_utils.get_inspect_query()
        response = requests.post(self.subgraphUrl, json={'query': query})
        text = json.loads(response.text)
        return text['data']['__schema']['types']
    

    def _parse_thegraph_query(self, queryTemplate):
        ast = parse(queryTemplate, no_location=True)
        if(len(ast.definitions) != 1):
            raise ValueError('The graph query must have one and only definition.')

        entities = []
        selections = ast.definitions[0].selection_set.selections
        for s in selections:
            entity = TheGraphEntity(s)
            entities.append(entity)
        return entities

    @st.cache(show_spinner=False)
    def _load_subgraph_per_entity_per_page(self, entity_name, url, query, since):
        if not since == None:
            query = query.replace('__LASTID__', since)
        
        response = requests.post(url, json={'query': query})
        text = json.loads(response.text)
        if 'data' in text:
            return text["data"][entity_name]
        elif 'errors' in text:
            raise ValueError(text['errors'])
        else:
            raise ValueError(f'Unable to process data: {text}')

    def _findColumnType(self, c:str):
        segs = c.split('.')
        segi = 0
        while segi < len(segs):

            segi += 1

    def _load_subgraph_per_entity_all_pages(self, url, entity:TheGraphEntity, progressCallback):
        arr = []
        i = 0
        while True:
            l = len(arr)
            query = entity.initialQuery if l == 0 else entity.paginationQuery
            since = None if l == 0 else arr[l-1]['id']
            parr = self._load_subgraph_per_entity_per_page(entity.name, url, '{'+query+'}', since)
            arr.extend(parr)
            l = len(parr)
            if progressCallback != None:
                progressCallback({'entity': entity.name, 'count':len(arr)})

            # print('!!pagination asc '+entity.name+' '+str(i)+' '+str(since)+' '+str(len(arr)))
            i += 1
            if(l == 0 or l < ITEMS_PER_PAGE or len(arr) >= entity.limit):
                break
        return arr
    
    def _process_datatypes(self, entity:TheGraphEntity, data):
        if self.types == None:
            self.types = self.__load_schema()
        df = pd.json_normalize(data)
        en = entity.name.title()
        if en.endswith('s'):
            en = en[0:len(en) - 1]

        columns = df.columns
        astypes = {}
        for c in columns:
            path = f"{en}.{c}"
            t = schema_utils.find_column_type(path, self.types)
            dt = df.dtypes[c]
            # print(f"column {c}\t{t}\t{df.dtypes[c]}")
            if t == None:
                continue
            t = t.lower()
            if t in ['int']:
                if dt != 'int64':
                    timestamp_matched = df[df[c].str.match(schema_utils.REGEX_TIMESTAMP) == True]
                    if len(timestamp_matched) == len(df):
                        df[c] = df[c].apply(lambda x: pd.to_datetime(x, unit='s'))
                    else:
                        astypes[c] = 'int64'
            elif t in ['bigdecimal','bigint']:
                astypes[c] = 'float'
        df = df.astype(astypes, copy=False)
        return df

    def _load_subgraph_per_entity(self, url, e:TheGraphEntity, progressCallback):
        df = None
        if(e.bypassPagination):
            data = self._load_subgraph_per_entity_all_pages(url, e, progressCallback)
            df = self._process_datatypes(e, data)
            if hasattr(e, 'orderBy'):
                ascending = True if hasattr(e, 'orderDirection') and e.orderDirection == 'asc' else False
                df.sort_values(by=[e.orderBy], ascending=ascending)
        else:
            data = self._load_subgraph_per_entity_per_page(e.name, url, '{'+e.initialQuery+'}', None)
            df = self._process_datatypes(e, data)
        return {
            'entity': e.name,
            'data': df
        }

    """
    Fetch data from a single subgraph, multiple entities are supported.
    Params:
    `url`: The url of the subgraph. [Explore subgraphs](https://thegraph.com/explorer/)
    `query`: The graph query. [Docs](https://thegraph.com/docs/graphql-api#queries)
        `bypassPagination`: Boolean value, default `False`. The graph has a limitation of 10000 items max per request. To load all items in the selected query, add this flag in the filter of each entity. For example: `deposits(bypassPagination, ....) {...}`.
        If `False`, the function will retrieve 100 items.
    Return:
    ```
    {
        'url': url,
        'data': {
            <entityName>: <array_of_items_from_the_graph>
        }
    }
    ```

    """

def load_subgraph(url:str, query:str, progressCallback=None):
    sl = SubgraphLoader(url)
    entities = sl._parse_thegraph_query(query)
    results = {}

    # https://stackoverflow.com/questions/2632520/what-is-the-fastest-way-to-send-100-000-http-requests-in-python
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(entities)) as executor:
        future_to_url = {executor.submit(sl._load_subgraph_per_entity, url, e, progressCallback) for e in entities}
        for thread in executor._threads:
            add_report_ctx(thread)

        for future in concurrent.futures.as_completed(future_to_url):
            # try:
            data = future.result()
            results[data['entity']] = data['data']
            # except Exception as exc:
            #     print('exception!! ')
            #     print(exc)
    return {
        'url': url,
        'data': results
    }

    # """
    # Fetch data from multiple subgraphs .
    # Params:
    # `url`: The url of the subgraph. [Explore subgraphs](https://thegraph.com/explorer/)
    # `query`: The graph query. [Docs](https://thegraph.com/docs/graphql-api#queries)
    #     `bypassPagination`: Boolean value, default `False`. The graph has a limitation of 10000 items max per request. If to load all items in the selected query, add this flag in the filter of each entity. For example: `deposits(bypassPagination, ....) {...}`.
    # Return:
    # ```
    # {
    #     <url1>: {
    #         <entityName>: <array_of_items_from_the_graph>
    #     },
    #     <url2>: {
    #         <entityName>: <array_of_items_from_the_graph>
    #     }
    # }
    # """
    # def load_subgraphs(defs:list[SubgraphDef]):
    #     results = {}
    #     with concurrent.futures.ThreadPoolExecutor(max_workers=len(defs)) as executor:
    #         future_to_url = {executor.submit(load_subgraph, d.url, d.query, d.progressCallback, d.astypes) for d in defs}
    #         for thread in executor._threads:
    #             add_report_ctx(thread)

    #         for future in concurrent.futures.as_completed(future_to_url):
    #             try:
    #                 data = future.result()
    #                 results[data['url']] = data['data']
    #             except Exception as e:
    #                 st.exception(e)
    #     return results







#tests

# url_aave_subgraph = 'https://api.thegraph.com/subgraphs/name/aave/protocol'
# query_aave = """
# {
#     deposits(
#         where:{timestamp_gt:1609459200, timestamp_lt:1609462800}
#         orderBy: timestamp
#         orderDirection: desc
#         first:5
#         # bypassPagination: true
#     ) {
#         reserve {
#             symbol,
#             decimals
#         }
#         amount
#         timestamp
#     }
#     # flashLoans(
#     #     orderBy: timestamp
#     #     orderDirection: asc
#     #     first:3
#     # ){
#     #     amount
#     #     timestamp
#     # }
# }
# """
# data = load_subgraph(url_aave_subgraph, query_aave)

# data = data['data']
# for k in data.keys():
#     st.markdown('---')
#     st.markdown(f'### {k}')
#     st.markdown('#### Data')
#     st.write(data[k])
#     st.markdown('#### Column Types')
#     st.write(data[k].dtypes)

