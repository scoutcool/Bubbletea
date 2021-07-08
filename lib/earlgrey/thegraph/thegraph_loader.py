from pandas.core.tools.datetimes import to_datetime
import streamlit as st
import pandas as pd
import numpy as np
import requests
import json

import concurrent.futures
from decimal import Decimal

from streamlit.report_thread import add_report_ctx
from graphql import parse, print_ast, ArgumentNode, NameNode, IntValueNode, FieldNode, SelectionSetNode, ObjectValueNode, StringValueNode, ObjectFieldNode, EnumValueNode


ITEMS_PER_PAGE = 1000
class SubgraphDef:
    url: str
    query: str
    def __init__(self, url:str, query:str) -> None:
        self.url = url
        self.query = query

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
            elif a.name.value == 'orderBy':
                self.orderBy = a.value.value
            elif a.name.value == 'orderDirection':
                self.orderDirection = a.value.value
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
        iArguments.append(ArgumentNode(name=NameNode(value='orderBy'), value=EnumValueNode(value='id')))
        pArguments.append(ArgumentNode(name=NameNode(value='orderBy'), value=EnumValueNode(value='id')))
        iArguments.append(ArgumentNode(name=NameNode(value='orderDirection'), value=EnumValueNode(value='asc')))
        pArguments.append(ArgumentNode(name=NameNode(value='orderDirection'), value=EnumValueNode(value='asc')))
        iArguments.append(ArgumentNode(name=NameNode(value='first'), value=IntValueNode(value=ITEMS_PER_PAGE)))
        pArguments.append(ArgumentNode(name=NameNode(value='first'), value=IntValueNode(value=ITEMS_PER_PAGE)))

        selections = node.selection_set.selections.copy()
        selections.append(FieldNode(name=NameNode(value='id')))
        if(hasattr(self, 'orderBy')):
            selections.append(FieldNode(name=NameNode(value=self.orderBy)))
        selectionSet = SelectionSetNode(selections=selections)
        
        iNode = FieldNode(directives=node.directives, alias=node.alias, name=node.name, arguments=iArguments, selection_set=selectionSet)
        pNode = FieldNode(directives=node.directives, alias=node.alias, name=node.name, arguments=pArguments, selection_set=selectionSet)

        # print(print_ast(iNode))
        # print(print_ast(pNode))
        self.initialQuery = print_ast(iNode)
        self.paginationQuery = print_ast(pNode)


    def __str__(self):
        keys = ['name', 'orderBy', 'orderDirection', 'bypassPagination', 'initialQuery']
        msg = ''
        for k in keys:
            if(hasattr(self, k)):
                msg += f'{k}: {getattr(self, k)} \n'
        msg += '\n'
        return msg
    def __repr__(self):
        return str(self) 

class FieldConfig:
    def __init__(self, name:str, type:str, unit='s') -> None:
        self.name = name
        self.type = type
        self.unit = unit

def _parse_thegraph_query(queryTemplate):
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
def _load_subgraph_per_entity_per_page(entity_name, url, query, since):
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

def _load_subgraph_per_entity_all_pages(url, entity:TheGraphEntity, progressCallback):
    arr = []
    i = 0
    while True:
        l = len(arr)
        query = entity.initialQuery if l == 0 else entity.paginationQuery
        since = None if l == 0 else arr[l-1]['id']
        parr = _load_subgraph_per_entity_per_page(entity.name, url, '{'+query+'}', since)
        arr.extend(parr)
        l = len(parr)
        if progressCallback != None:
            progressCallback({'entity': entity.name, 'count':len(arr)})

        # print('!!pagination asc '+entity.name+' '+str(i)+' '+str(since)+' '+str(len(arr)))
        i += 1
        if(l == 0 or l < ITEMS_PER_PAGE or len(arr) >= entity.limit):
            break
    return arr
def _process_datatypes(data, astypes):
    df = pd.json_normalize(data)
    if astypes != None:
        c = {}
        for t in astypes:
            if t.name not in df.columns:
                continue
            if t.type == 'datetime':
                df[t.name] = df[t.name].apply(lambda x: to_datetime(x, unit=t.unit))
            else:
                c[t.name] = t.type
        df = df.astype(c, copy=False)
    return df

def _load_subgraph_per_entity(url, e:TheGraphEntity, progressCallback, astypes):
    df = None
    if(e.bypassPagination):
        data = _load_subgraph_per_entity_all_pages(url, e, progressCallback)
        df = _process_datatypes(data, astypes)
        if astypes != None:
            for col in astypes:
                data
        if hasattr(e, 'orderBy'):
            ascending = True if hasattr(e, 'orderDirection') and e.orderDirection == 'asc' else False
            df.sort_values(by=[e.orderBy], ascending=ascending)
    else:
        data = _load_subgraph_per_entity_per_page(e.name, url, '{'+e.initialQuery+'}', None)
        df = _process_datatypes(data, astypes)
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
def load_subgraph(url, query, progressCallback=None, astypes=None):
    entities = _parse_thegraph_query(query)
    results = {}

    # https://stackoverflow.com/questions/2632520/what-is-the-fastest-way-to-send-100-000-http-requests-in-python
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(entities)) as executor:
        future_to_url = {executor.submit(_load_subgraph_per_entity, url, e, progressCallback, astypes) for e in entities}
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

"""
Fetch data from multiple .
Params:
`url`: The url of the subgraph. [Explore subgraphs](https://thegraph.com/explorer/)
`query`: The graph query. [Docs](https://thegraph.com/docs/graphql-api#queries)
    `bypassPagination`: Boolean value, default `False`. The graph has a limitation of 10000 items max per request. If to load all items in the selected query, add this flag in the filter of each entity. For example: `deposits(bypassPagination, ....) {...}`.
Return:
```
{
    <url1>: {
        <entityName>: <array_of_items_from_the_graph>
    },
    <url2>: {
        <entityName>: <array_of_items_from_the_graph>
    }
}
"""
def load_subgraphs(defs:'list[SubgraphDef]'):
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(defs)) as executor:
        future_to_url = {executor.submit(load_subgraph, d.url, d.query) for d in defs}
        for thread in executor._threads:
            add_report_ctx(thread)

        for future in concurrent.futures.as_completed(future_to_url):
            try:
                data = future.result()
                results[data['url']] = data['data']
            except Exception as exc:
                st.exception(e)
    return results