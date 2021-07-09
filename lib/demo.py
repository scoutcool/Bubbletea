import streamlit as st
import altair as alt

import os

from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title='Earlgrey Demos', page_icon=':coin:', layout='wide', initial_sidebar_state='collapsed')
st.sidebar.title(":hot_pepper: Demos")

alt.renderers.set_embed_options(actions=False)

st.markdown(
    """ <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style> """,
    unsafe_allow_html=True,
)

with st.beta_expander("About Earlgrey"):
    with open('README.md', 'r') as file:
        intro = file.read()
        st.markdown(intro)

display, editor = st.beta_columns((2, 1))


selected_demo = None
with st.sidebar:
    files_str = os.environ.get("demos")
    files = files_str.split(',')
    print(files[0])
    # files = [filename for filename in os.listdir('./lib') if filename.startswith("demo_")]
    selected_demo = st.selectbox('🌟 Pick one', sorted(files))

code_input = """st.header("Earlgrey Demos")"""
with open(f'./lib/{selected_demo}', 'r') as file:
    code_input = file.read()

with editor:
    st.markdown(f'```{code_input}')

with display:
    exec(code_input)
