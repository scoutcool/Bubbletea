import streamlit as st

import os

st.set_page_config(page_title='Earlgrey Demos', page_icon=':coin:', layout='wide', initial_sidebar_state='collapsed')
st.sidebar.title(":hot_pepper: Demos")

with st.beta_expander("About Earlgrey"):
    with open('README.md', 'r') as file:
        intro = file.read()
        st.markdown(intro)

display, editor = st.beta_columns((1, 1))


selected_demo = None
with st.sidebar:
    files = os.listdir('demo/')
    files.remove('notebook.py')
    selected_demo = st.selectbox('🌟 Pick one', sorted(files))

code_input = """st.header("Earlgrey Demos")"""
with open(f'demo/{selected_demo}', 'r') as file:
    code_input = file.read()

with editor:
    st.markdown(f'```{code_input}')

with display:
    exec(code_input)
