import datetime
import streamlit as st

def parse_url_var(specs:list):
    result = {}
    urlvars = st.experimental_get_query_params()
    for k in specs:
        if k['key'] in urlvars.keys():
            value = urlvars[k['key']][0]
            if 'type' in k.keys():
                t = k['type']
                if t == 'datetime':
                    value = datetime.date.fromisoformat(value)
                elif t == 'int':
                    value = int(t)
            result[k['key']] = value
    return result

def update_url(url_state:dict):
    urlvars = st.experimental_get_query_params()
    state = {**urlvars, **url_state}
    st.experimental_set_query_params(**state)
    