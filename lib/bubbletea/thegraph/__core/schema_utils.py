
import json


REGEX_TIMESTAMP = r'^1[5-9]\d\d\d\d\d\d\d\d$'
ITEMS_PER_PAGE = 1000

def get_max_items_per_page():
  return ITEMS_PER_PAGE

def process_response_to_json(response):
    if response.status_code != 200:
        raise ValueError(f'The Graph Connection Error: {response.status_code}')
    text = json.loads(response.text)
    if 'errors' in text:
        errors = text['errors']
        raise ValueError(f'The Graph Error: {errors}')
    return text

def _ultimate_ofType(fieldType):
    if fieldType['ofType'] == None:
        return fieldType['name']
    else:
        return _ultimate_ofType(fieldType['ofType'])

def _find_entity(entityName, types):
    for t in types:
        if t['name'] == entityName:
            return t
    return None

def _find_field_type(fieldName, entity):
    if entity == None:
      return None
    # print(f'??? _find_field_type: {fieldName} {entity}')
    if 'fields' in entity.keys():
      for f in entity['fields']:
          if f['name'] == fieldName:
              if f['type'] != None:
                  t = f['type']
                  if t['name'] != None:
                      return t['name']
                  return _ultimate_ofType(t)
              return 
    return None

def find_column_type(entityPath, types):
    segs = entityPath.split('.')
    while len(segs) >= 2:
        en = segs[0]
        field = segs[1]
        entity = _find_entity(en, types)
        # print(f"??? find_column_type\t{field} {entity}")
        fieldType = _find_field_type(field, entity)
        if fieldType == None:
            return None
        segs.pop(0)
        if len(segs) == 1:
            return fieldType
        segs[0] = fieldType
        return find_column_type('.'.join(segs), types)
    return 
    
def get_inspect_query():
    return """ 
     {
    __schema {
      types {
        ...FullType
      }
    }
  }
    fragment FullType on __Type {
      name
      fields(includeDeprecated: true) {
        name
        type {
          ...TypeRef
        }
      }
    }
    fragment TypeRef on __Type {
      name
      ofType {
        name
        ofType {
          name
          ofType {
            name
            ofType {
              name
              ofType {
                name
                ofType {
                  name
                  ofType {
                    name
                  }
                }
              }
            }
          }
        }
      }
    }
    """