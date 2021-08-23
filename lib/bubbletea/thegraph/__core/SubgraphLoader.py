from .TheGraphEntity import TheGraphEntity
from . import schema_utils
import streamlit as st
from decimal import Decimal
import requests
import pandas as pd
from graphql import parse

class SubgraphLoader:
    def __init__(self, subgraphUrl:str, query) -> None:
        self.subgraphUrl = subgraphUrl
        self.types = None
        self.types = self._load_schema()
        self.entities = self._parse_thegraph_query(query)
        pass

    @st.cache(show_spinner=False)
    def _load_schema(self):
        query = schema_utils.get_inspect_query()
        response = requests.post(self.subgraphUrl, json={'query': query})
        text = schema_utils.process_response_to_json(response)
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
    def _load_subgraph_query(self, url, query):
        response = requests.post(url, json={'query': query})
        return schema_utils.process_response_to_json(response)

    def _process_datatypes(self, entity:TheGraphEntity, data, useBigDecimal):
        if self.types == None:
            self.types = self.__load_schema()
        df = pd.json_normalize(data)
        # en = schema_utils.find_column_type(en, self.types)
        en = schema_utils.find_column_type(f'Query.{entity.name}', self.types)
        # if en.endswith('s'):
        #     en = f"{en[0:1].upper()}{en[1:len(en) - 1]}"

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

    def _load_page(self, progressCallback=None, initialPage=False):
        query = '{'
        has_entity = False
        for e in self.entities:
            if initialPage:
                query += e.initialQuery
                has_entity = True
            elif e.bypassPagination and e.lastId != None:
                # print(f"???_load_page {e.name}\t{e.lastId}")
                eq = e.paginationQuery.replace('__LASTID__', e.lastId)
                query += str(eq)
                has_entity = True
        query += '}'
        if not has_entity:
            return False

        # print(f'~~~query~~~\n{query}\n\n')
        
        text = self._load_subgraph_query(self.subgraphUrl, query)
        data = text['data']
        has_more_page = False
        progress = {}
        for k in data.keys():
            for e in self.entities:
                if k == e.name:
                    d = data[k]
                    l = len(d)
                    e.data.extend(d)
                    if progressCallback != None:
                        progress[k] = l + len(e.data)

                    if e.bypassPagination:
                        e.lastId = None if l == 0 else d[l-1]['id']
                        # print(f'~~~{e.name}\t{k}\t{l}\t{e.lastId}~~~\n{d}\n\n')
                        if l >= schema_utils.get_max_items_per_page():
                            has_more_page = True 
        if progressCallback != None:
            progressCallback(progress)
        return has_more_page
    

    def beta_load_subgraph(self, progressCallback=None, useBigDecimal=False):
        # print('?????beta_load_subgraph')
        has_more_page = self._load_page(progressCallback, True)
        # print(f'?????has_more_page {has_more_page}')
        while has_more_page:
            has_more_page = self._load_page(progressCallback, False)
            
        result = {}
        for e in self.entities:
            df = self._process_datatypes(e, e.data, useBigDecimal)
            if e.bypassPagination and e.orderBy != None:
                ascending = (e.orderDirection == 'asc')
                df.sort_values(e.orderBy, ascending=ascending, inplace=True)
            result[e.name] = df
            # print(f'~~~{e.name} {len(e.data)}~~~\n{df}\n~~~\n')
        return result