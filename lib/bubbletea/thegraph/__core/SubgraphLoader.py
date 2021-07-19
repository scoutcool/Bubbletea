from .TheGraphEntity import TheGraphEntity
from . import schema_utils
import streamlit as st
from decimal import Decimal
import requests
import json
import pandas as pd
from graphql import parse


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
            if(l == 0 or l < schema_utils.get_max_items_per_page() or len(arr) >= entity.limit):
                break
        return arr

    def _process_datatypes(self, entity:TheGraphEntity, data, useBigDecimal):
        if self.types == None:
            self.types = self.__load_schema()
        df = pd.json_normalize(data)
        en = entity.name
        if en.endswith('s'):
            en = f"{en[0:1].upper()}{en[1:len(en) - 1]}"

        columns = df.columns
        astypes = {}
        for c in columns:
            path = f"{en}.{c}"
            t = schema_utils.find_column_type(path, self.types)
            dt = df.dtypes[c]
            if t == None:
                continue
            t = t.lower()
            if t in ['int']:
                if dt == 'int64':
                    timestamp_matched = df[(1500000000 <= df[c]) & (df[c] <= 1800000000)]
                    if len(timestamp_matched) == len(df):
                        df[c] = df[c].apply(lambda x: pd.to_datetime(x, unit='s'))
                    pass
                else:
                    timestamp_matched = df[df[c].str.match(schema_utils.REGEX_TIMESTAMP) == True]
                    if len(timestamp_matched) == len(df):
                        df[c] = df[c].apply(lambda x: pd.to_datetime(x, unit='s'))
                    else:
                        astypes[c] = 'int64'
            elif t in ['bigdecimal','bigint']:
                if useBigDecimal:
                    df[c] = df[c].apply(lambda x: Decimal(x))
                else:
                    astypes[c] = 'float64'
        if len(astypes.keys()) > 0:
            df = df.astype(astypes, copy=False)
        return df

    
    def _load_subgraph_per_entity(self, url, e:TheGraphEntity, progressCallback, useBigDecimal:bool):
        df = None
        if(e.bypassPagination):
            data = self._load_subgraph_per_entity_all_pages(url, e, progressCallback)
            df = self._process_datatypes(e, data, useBigDecimal)
            if hasattr(e, 'orderBy'):
                ascending = True if hasattr(e, 'orderDirection') and e.orderDirection == 'asc' else False
                df.sort_values(by=[e.orderBy], ascending=ascending)
        else:
            data = self._load_subgraph_per_entity_per_page(e.name, url, '{'+e.initialQuery+'}', None)
            df = self._process_datatypes(e, data, useBigDecimal)
        return {
            'entity': e.name,
            'data': df
        }