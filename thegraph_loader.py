from logging import exception
import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import math

from graphql import parse, print_ast, ArgumentNode, NameNode, IntValueNode, FieldNode, SelectionSetNode

ITEMS_PER_PAGE = 2

class TheGraphEntity:
    def __init__(self, node) -> None:
        self.limit = np.Infinity
        self.name = node.name.value
        self.hasPages = False
        arguments = node.arguments
        whereArg = ''
        first = np.Infinity
        for a in arguments:
            argName = a.name.value
            if(argName == 'first'):
                first = int(a.value.value)
            elif(argName == 'orderBy'):
                self.orderBy = a.value.value
            elif(argName == 'orderDirection'):
                self.orderDirection = a.value.value
            elif(argName == 'where'):
                whereArg = a
        

        if(hasattr(whereArg, 'value') and hasattr(whereArg.value, 'fields')):
            for f in whereArg.value.fields:
                try:
                    if(f.name.value.index(self.orderBy+'_gt') >= 0):
                        self.rangeLowerVar = f.value.value
                except ValueError as error:
                    a = 1

                try:
                    if(f.name.value.index(self.orderBy+'_lt') >= 0):
                        self.rangeUpperVar = f.value.value
                except ValueError as error:
                    a = 1


            
        self.initialQuery = print_ast(node)
        
        self.hasPages = hasattr(self, 'rangeLowerVar') and hasattr(self, 'rangeUpperVar') and hasattr(self, 'orderBy') and hasattr(self, 'orderDirection')
        if(self.hasPages):
            #make sure `first` is in the entity arguments
            shouldRebuildQuery = False
            rebuiltArguments = arguments.copy()
            if(first == np.Infinity):
                rebuiltArguments.append(ArgumentNode(name=NameNode(value='first'), value=IntValueNode(value=ITEMS_PER_PAGE)))
                shouldRebuildQuery = True
            else:
                self.limit = first

            #make sure `orderBy` field is in the entity selection
            hasOrderByField = False
            for f in node.selection_set.selections:
                if(f.name.value == self.orderBy):
                    hasOrderByField = True
                    shouldRebuildQuery = True
                    break
            
            rebuiltSelectionSet = node.selection_set
            
            if(hasOrderByField == False):
                rebuiltSelections = []
                for f in node.selection_set.selections:
                    rebuiltSelections.append(f)
                rebuiltSelections.append(FieldNode(name=NameNode(value=self.orderBy)))
                rebuiltSelectionSet = SelectionSetNode(selections=rebuiltSelections)


            #rebuild query
            if(shouldRebuildQuery):
                node = FieldNode(directives=node.directives, alias=node.alias, name=node.name, arguments=rebuiltArguments, selection_set=rebuiltSelectionSet)
                self.initialQuery = print_ast(node)
            

            #pagination query
            self.paginationQuery = self.initialQuery.replace(self.orderBy+'_gt', self.orderBy+'_gt')
            self.paginationQuery = self.paginationQuery.replace(self.orderBy+'_gte', self.orderBy+'_gt')
            self.paginationQuery = self.paginationQuery.replace(self.orderBy+'_lte', self.orderBy+'_lt')

        pass
    def __str__(self):
        keys = ['name', 'orderBy', 'orderDirection', 'first', 'rangeLowerVar', 'rangeUpperVar', 'hasPages', 'initialQuery']
        msg = ''
        for k in keys:
            if(hasattr(self, k)):
                msg += f'{k}: {getattr(self, k)} \n'
        msg += '\n'
        return msg
    def __repr__(self):
        return str(self)
    
def parse_thegraph_query(queryTemplate):
    ast = parse(queryTemplate, no_location=True)
    if(len(ast.definitions) != 1):
        raise ValueError('The graph query must have one and only definition.')

    entities = []
    selections = ast.definitions[0].selection_set.selections
    for s in selections:
        entity = TheGraphEntity(s)
        entities.append(entity)
    return entities


def load_subgraph_per_entity_per_page(entityName, url, query, queryVarRangeLower, queryVarRangeUpper, rangeLowerValue, rangeUpperValue):
    query = query.replace(queryVarRangeLower, str(rangeLowerValue))
    query = query.replace(queryVarRangeUpper, str(rangeUpperValue))
    
    response = requests.post(url, json={'query': query})
    text = json.loads(response.text)
    return text["data"][entityName]

def load_subgraph_per_entity_all_pages_asc(url, entity:TheGraphEntity, rangeLowerValue, rangeUpperValue):
    t = rangeLowerValue
    arr = []
    i = 0
    while(t < rangeUpperValue):
        query = entity.initialQuery if len(arr) == 0 else entity.paginationQuery
        parr = load_subgraph_per_entity_per_page(entity.name, url, '{'+query+'}', entity.rangeLowerVar, entity.rangeUpperVar, t, rangeUpperValue)
        l = len(parr)
        arr.extend(parr)
        print('!!pagination asc '+entity.name+' '+str(i)+' '+str(t)+' '+str(rangeUpperValue)+' '+str(len(arr)))
        i += 1
        if(l == 0 or l < ITEMS_PER_PAGE or len(arr) >= entity.limit):
            break
        else:
            t = parr[l-1][entity.orderBy]
    return arr


def load_subgraph_per_entity_all_pages_desc(url, entity:TheGraphEntity, rangeLowerValue, rangeUpperValue):
    t = rangeUpperValue
    arr = []
    i = 0
    while(t >= rangeLowerValue):
        query = entity.initialQuery if len(arr) == 0 else entity.paginationQuery
        parr = load_subgraph_per_entity_per_page(entity.name, url, '{'+query+'}', entity.rangeLowerVar, entity.rangeUpperVar, rangeLowerValue, t)
        l = len(parr)
        print('!!pagination asc '+entity.name+' '+str(i)+' '+str(rangeLowerValue)+' '+str(t)+' '+str(len(arr)))
        arr.extend(parr)
        i += 1
        if(l == 0 or l < ITEMS_PER_PAGE or len(arr) >= entity.limit):
            break
        else:
            t = parr[l-1][entity.orderBy]
    return arr

def load_subgraph(url, queryTemplate):
    entities = parse_thegraph_query(queryTemplate)
    # print(entities)
    results = {}
    for e in entities:
        if(e.hasPages):
            if(e.orderDirection == 'asc'):
                results[e.name] = load_subgraph_per_entity_all_pages_asc(url, e, int(e.rangeLowerVar), int(e.rangeUpperVar))
            elif(e.orderDirection == 'desc'):
                results[e.name] = load_subgraph_per_entity_all_pages_desc(url, e, int(e.rangeLowerVar), int(e.rangeUpperVar))
        else:
            results[e.name] = load_subgraph_per_entity_per_page(e.name, url, '{'+e.initialQuery+'}', '--------', '--------', 1, 2)
    return results



# url_aave_subgraph = 'https://api.thegraph.com/subgraphs/name/aave/protocol'
# query_template = """
# {
#     deposits(
#       where:{timestamp_gt:1609459200, timestamp_lt:1609462800}
#         orderBy: timestamp
#         orderDirection: desc
#     ) {
#         reserve {
#             symbol,
#             name,
#             decimals
#         }
#         amount
#         timestamp
#     }
#     flashLoans(
#         orderBy: timestamp
#         orderDirection: asc
#     ){
#         amount
#         timestamp
#     }
# }
# """

# data = load_subgraph(url_aave_subgraph, query_template)
# for k in data.keys():
#     st.subheader(k)
#     st.write(data[k])