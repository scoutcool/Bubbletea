import streamlit as st
import altair as alt
from streamlit.errors import StreamlitAPIException
from earlgrey.transformers import urlparser as urlparser
import os

from dotenv import load_dotenv
load_dotenv()

try:
    st.set_page_config(page_title='Earlgrey Demos', page_icon=':coin:', layout='wide', initial_sidebar_state='collapsed')
except StreamlitAPIException:
    pass

st.sidebar.title(":hot_pepper: Demos")

alt.renderers.set_embed_options(actions=False)

with st.beta_expander("About Earlgrey"):
    with open('README.md', 'r') as file:
        intro = file.read()
        st.markdown(intro)

display, editor = st.beta_columns((2, 1))

urlvars = urlparser.parse_url_var([{'key':'demo'}])
try:
    selected_demo = urlvars['demo']
except KeyError:
    selected_demo = None
    pass


with st.sidebar:
    files_str = os.environ.get("demos")
    files = sorted(files_str.split(','))
    try:
        index = files.index(selected_demo)
    except ValueError:
        index = 0
    selected_demo = st.selectbox('🌟 Pick one', files, index=index)
    urlparser.update_url({'demo': selected_demo})

code_input = """st.header("Earlgrey Demos")"""
with open(f'./lib/{selected_demo}', 'r') as file:
    code_input = file.read()

with editor:
    st.markdown(f'```{code_input}')

with display:
    exec(code_input)
