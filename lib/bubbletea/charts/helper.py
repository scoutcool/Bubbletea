import streamlit as st


def hide_action_menu():
    st.markdown(
        """
        <style type='text/css'>
            details {
                display: none;
            }
            .vega-embed.has-actions {
                padding-right: 0;
            }
        </style>
    """,
        unsafe_allow_html=True,
    )
