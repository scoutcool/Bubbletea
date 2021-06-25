import streamlit as st

from streamlit_ace import st_ace
import os

st.set_page_config(page_title='Streamlit Sandbox', page_icon=':coin:', layout='wide', initial_sidebar_state='collapsed')
st.sidebar.title(":hot_pepper: Demos")

display, editor = st.beta_columns((1, 1))


option = None
selected_demo = None
editor_theme = None
editor_key_binding = None
editor_wrap = False
with st.sidebar:
    files = os.listdir('demo/')
    files.remove('notebook.py')
    # files.remove('aave.py')
    selected_demo = st.selectbox('🌟 Pick one', sorted(files))

    st.markdown("""
    ---
    """)
    editor_theme = st.sidebar.selectbox("Editor Theme", options=['solarized_dark','solarized_light'], index=1)
    editor_key_binding = st.sidebar.selectbox("Key binding", options=["emacs", "sublime", "vim", "vscode"], index=3)
    # editor_wrap = st.sidebar.checkbox("Wrap lines", value=False)

code_input = """st.header("Earlgrey Demos")"""
with open(f'demo/{selected_demo}', 'r') as file:
    code_input = file.read()

print(f"!!!! code has changed\n{code_input}")
with editor:
    st.markdown(f'```{code_input}')
    # with st.echo(code_location='below'):
        # f'```{code_input}```'
    
    # st.write('#### Code editor')
    # code = st_ace(
    #     value=code_input,
    #     language="python",
    #     placeholder="st.header('Hello world!')",
    #     theme=editor_theme,
    #     keybinding=editor_key_binding,
    #     font_size=14,
    #     tab_size=4,
    #     wrap=st.sidebar.checkbox("Wrap lines", value=False),
    #     show_gutter=True,
    #     show_print_margin=False,
    #     auto_update=False,
    #     readonly=False,
    #     key="ace-editor"
    # )
    # st.write('Hit `CTRL+ENTER` to refresh')
    # st.write('*Remember to save your code separately!*')
    # print(f'????? !!!! {selected_demo}\n{code}')

with display:
    exec(code_input)
