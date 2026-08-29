#Streamlit is essentially a Python framework for building interactive web apps 
# directly from your scripts. Instead of learning front‑end technologies like HTML, CSS, or JavaScript

import streamlit as st
# Imported streamlit

st.title("AI Web Scrapper")
#Used title as AI Web Scrapper

url = st.text_input("Enter a Website URL")
# Gives a box where we can past the url


if st.button("Scrape the Site"):    # Creates a button namely Scrape the site
    st.write("Scraping the website")    # After clicking we get this message

