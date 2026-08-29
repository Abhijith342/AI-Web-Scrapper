#Streamlit is essentially a Python framework for building interactive web apps 
# directly from your scripts. Instead of learning front‑end technologies like HTML, CSS, or JavaScript

import streamlit as st
# Imported streamlit
from scrape import scrape_website   #Importing the scrape_website function from scrape 

st.title("AI Web Scrapper")
#Used title as AI Web Scrapper

url = st.text_input("Enter a Website URL")
# Gives a box where we can past the url


if st.button("Scrape the Site"):    # Creates a button namely Scrape the site
    st.write("Scraping the website")    # After clicking we get this message

    result = scrape_website(url)    #passing the url to the function 
    print(result)   # the result is the html source code 

