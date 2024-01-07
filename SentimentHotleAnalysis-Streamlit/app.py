import streamlit as st
import sidebar
import textPage
import imdbReviewsPage


st.title("Hello")
page = sidebar.show()

if page =="Text":
    textPage.renderPage()

elif page =="Hotel reviews":
    imdbReviewsPage.renderPage()
