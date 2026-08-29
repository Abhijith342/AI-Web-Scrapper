#Streamlit is essentially a Python framework for building interactive web apps 
# directly from your scripts. Instead of learning front‑end technologies like HTML, CSS, or JavaScript

import streamlit as st
# Imported streamlit
from scrape import (
    scrape_website,
    split_dom_content,
    clean_body_content,
    extract_body_content
)
#Importing functions from scrape 

st.title("AI Web Scrapper")
#Used title as AI Web Scrapper

url = st.text_input("Enter a Website URL")
# Gives a box where we can past the url


if st.button("Scrape the Site"):    # Creates a button namely Scrape the site
    st.write("Scraping the website")    # After clicking we get this message

    result = scrape_website(url)    #passing the url to the function contains html source also

    body_content = extract_body_content(result)
    cleaned_content = clean_body_content(body_content)

    # Stores the cleaned_content  in streamlit's session state
    # so it can be accessed again even if streamlit reruns the script 

    st.session_state.dom_content = cleaned_content 

    # Creates a collapsable section to view the scrapped DOM content 
    with st.expander("View DOM Cotent"):
        
        st.text_area("DOM Content",cleaned_content,height=300)  # Contains DOM contents with height of 300

