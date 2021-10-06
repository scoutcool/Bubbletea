import streamlit as st
from streamlit.errors import StreamlitAPIException
import bubbletea
import os

from dotenv import load_dotenv
load_dotenv()

try:
    st.set_page_config(page_title='bubbletea Demos', page_icon=':coin:', layout='wide', initial_sidebar_state='collapsed')
except StreamlitAPIException:
    pass

files_str = os.environ.get("demos")
files = sorted(files_str.split(','))
urlvars = bubbletea.parse_url_var([{'key':'demo'}])
try:
    selected_demo = urlvars['demo']
except KeyError:
    selected_demo = files[0]
    pass

def on_demo_change():
    selected_demo = st.session_state.demo_selector
    bubbletea.update_url({'demo': selected_demo})


code_input = """st.header("bubbletea Demos")"""

if selected_demo in files:
    st.sidebar.title(":hot_pepper: Demos")
    with st.expander("About Bubbletea"):
        with open('README.md', 'r') as file:
            intro = file.read()
            st.markdown(intro)

    display, editor = st.columns((2, 1))   

    with st.sidebar:
        try:
            index = files.index(selected_demo)
        except ValueError:
            index = 0
        selected_demo = st.selectbox('🌟 Pick one', files, index=index, on_change=on_demo_change, key='demo_selector')

    with open(f'./examples/{selected_demo}', 'r') as file:
        code_input = file.read()

    with editor:
        st.markdown(f'```{code_input}')

    with display:
        exec(code_input)
else:
    with open(f'./examples/{selected_demo}', 'r') as file:
        code_input = file.read()
        exec(code_input)