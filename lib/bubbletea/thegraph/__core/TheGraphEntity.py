
import numpy as np
from . import schema_utils
from graphql import parse, print_ast, ArgumentNode, NameNode, IntValueNode, FieldNode, SelectionSetNode, ObjectValueNode, StringValueNode, ObjectFieldNode, EnumValueNode

class TheGraphEntity:
    def __init__(self, node) -> None:
        self.limit = np.Infinity
        self.name = node.name.value
        self.bypassPagination = False
        self.orderBy = None
        
        self.__build_pagination_query__(node)
        self.lastId = None
        self.data = []
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
            elif a.name.value == 'orderBy':
                self.orderBy = a.value.value
            elif a.name.value == 'orderDirection':
                self.orderDirection = a.value.value
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
        if self.bypassPagination:
            iArguments.append(ArgumentNode(name=NameNode(value='orderBy'), value=EnumValueNode(value='id')))
            pArguments.append(ArgumentNode(name=NameNode(value='orderBy'), value=EnumValueNode(value='id')))
            iArguments.append(ArgumentNode(name=NameNode(value='orderDirection'), value=EnumValueNode(value='asc')))
            pArguments.append(ArgumentNode(name=NameNode(value='orderDirection'), value=EnumValueNode(value='asc')))
        iArguments.append(ArgumentNode(name=NameNode(value='first'), value=IntValueNode(value=schema_utils.get_max_items_per_page())))
        pArguments.append(ArgumentNode(name=NameNode(value='first'), value=IntValueNode(value=schema_utils.get_max_items_per_page())))

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
        keys = ['name', 'bypassPagination', 'initialQuery', 'paginationQuery', 'orderBy', 'orderDirection']
        msg = ''
        for k in keys:
            if(hasattr(self, k)):
                msg += f'{k}: {getattr(self, k)} \n'
        msg += '\n'
        return msg
    def __repr__(self):
        return str(self) 