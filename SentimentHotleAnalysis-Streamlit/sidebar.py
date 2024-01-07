from pickle import FALSE
import streamlit as st
from streamlit_option_menu import option_menu

def show():
    with st.sidebar:
        st.markdown("""
                    # Applications
                    """, unsafe_allow_html = False)
        selected = option_menu(
            menu_title = None,
            options = ["Text", "Hotel reviews"], #required
            icons = ["card-text", "film"], #optional
            default_index = 0, #optional
        )
        return selected