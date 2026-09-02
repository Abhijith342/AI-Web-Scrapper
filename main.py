# Streamlit is a Python framework used to create
# interactive web applications without needing
# separate HTML, CSS, or JavaScript files.

import streamlit as st

# json is used to convert Ollama's JSON string
# response into a Python dictionary.
import json


# Import functions responsible for:
# 1. Splitting webpage text into smaller sections
# 2. Creating embeddings for those sections
# 3. Finding sections relevant to the user's question
from retrieve import (
    split_into_sections,
    create_embeddings,
    retrieve_relevant_content
)


# Import functions responsible for:
# 1. Opening/scraping the website
# 2. Extracting the <body> from the HTML
# 3. Cleaning unnecessary HTML content
from scrape import (
    scrape_website,
    extract_body_content,
    clean_body_content,
)


# Import the function that sends the relevant
# webpage content to Ollama for information extraction.
from parse import parse_with_ollama


# ---------------------------------------------------------
# CACHED SCRAPING FUNCTION
# ---------------------------------------------------------

# @st.cache_data tells Streamlit to remember the result
# of this function.
#
# If the same URL is requested again, Streamlit can reuse
# the previous result instead of scraping the website again.
@st.cache_data
def cached_scrape(url):

    # Scrape the website and return its HTML content.
    return scrape_website(url)


# ---------------------------------------------------------
# PAGE TITLE
# ---------------------------------------------------------

# Display the main title of our application.
st.title("AI Web Scrapper")


# ---------------------------------------------------------
# WEBSITE URL INPUT
# ---------------------------------------------------------

# Create a text box where the user can enter
# the website they want to scrape.
url = st.text_input(
    "Enter a Website URL"
)


# ---------------------------------------------------------
# SCRAPE BUTTON
# ---------------------------------------------------------

# This block runs when the user clicks
# the "Scrape the Site" button.
if st.button("Scrape the Site"):

    # Check whether the user actually entered a URL.
    if not url:

        # If the URL is empty, show a warning.
        st.warning(
            "Please enter a website URL."
        )

    else:

        # -------------------------------------------------
        # STEP 1 — SCRAPE WEBSITE
        # -------------------------------------------------

        # st.spinner displays a loading message
        # while the operation is running.
        with st.spinner(
            "Scraping the website..."
        ):

            # Send the URL to our Selenium + Bright Data
            # scraping function.
            #
            # result contains the HTML of the webpage.
            result = scrape_website(url)


        # -------------------------------------------------
        # STEP 2 — CLEAN WEBSITE CONTENT
        # -------------------------------------------------

        with st.spinner(
            "Cleaning webpage..."
        ):

            # Extract only the <body> portion
            # from the complete HTML.
            body_content = extract_body_content(
                result
            )

            # Remove unnecessary elements such as:
            # <script>
            # <style>
            #
            # and convert the remaining HTML into
            # readable text.
            cleaned_content = clean_body_content(
                body_content
            )


        # -------------------------------------------------
        # STEP 3 — STORE CLEANED CONTENT
        # -------------------------------------------------

        # Streamlit reruns the Python script whenever
        # the user interacts with the application.
        #
        # session_state allows us to keep our webpage
        # content available between those reruns.
        st.session_state.dom_content = (
            cleaned_content
        )


        # -------------------------------------------------
        # STEP 4 — PREPARE CONTENT FOR AI SEARCH
        # -------------------------------------------------

        with st.spinner(
            "Preparing webpage for AI search..."
        ):

            # Divide the large webpage text into
            # smaller sections.
            #
            # Example:
            #
            # 12000 characters
            #        ↓
            # Section 1
            # Section 2
            # Section 3
            # ...
            sections = split_into_sections(
                cleaned_content
            )


            # Convert every section into an embedding.
            #
            # An embedding represents the meaning of
            # the text as numbers.
            #
            # These embeddings allow us to perform
            # semantic search later.
            embeddings = create_embeddings(
                sections
            )


            # Tell the user how many sections
            # were created and indexed.
            st.success(
                f"Website ready! "
                f"{len(sections)} sections indexed."
            )


            # Store the sections in Streamlit's
            # session state so they can be used later
            # when the user clicks "Parse Content".
            st.session_state.sections = sections


            # Store the embeddings as well.
            st.session_state.embeddings = embeddings


        # Tell the user how much cleaned text
        # was obtained from the website.
        st.success(
            f"Website scraped successfully — "
            f"{len(cleaned_content):,} characters"
        )


        # -------------------------------------------------
        # VIEW COMPLETE CLEANED CONTENT
        # -------------------------------------------------

        # Create a collapsible section.
        #
        # The user can open this if they want to
        # inspect what our scraper actually collected.
        with st.expander(
            "View DOM Content"
        ):

            # Display the cleaned webpage text
            # inside a text area.
            st.text_area(
                "DOM Content",
                cleaned_content,
                height=300
            )


# ---------------------------------------------------------
# PARSING SECTION
# ---------------------------------------------------------

# Only show the parsing interface if a website
# has already been scraped.
#
# We check session_state because the page reruns
# whenever Streamlit buttons are clicked.
if "dom_content" in st.session_state:


    # -----------------------------------------------------
    # USER'S QUESTION
    # -----------------------------------------------------

    # Ask the user what information they want
    # to extract from the webpage.
    #
    # Example:
    #
    # "What processor is used?"
    #
    # or:
    #
    # "Extract processor, RAM, GPU and storage."
    parse_description = st.text_area(
        "Describe what you want to parse?"
    )


    # -----------------------------------------------------
    # PARSE BUTTON
    # -----------------------------------------------------

    # Run this block when the user clicks
    # "Parse Content".
    if st.button("Parse Content"):


        # Check whether the user entered a question.
        if not parse_description:

            # If nothing was entered, show a warning.
            st.warning(
                "Please describe what you want to find."
            )


        else:

            # -------------------------------------------------
            # STEP 5 — SEMANTIC SEARCH
            # -------------------------------------------------

            # Show a loading message while MiniLM
            # searches for relevant webpage sections.
            with st.spinner(
                "Finding relevant content..."
            ):

                # Search the previously created sections
                # using semantic similarity.
                #
                # The function returns:
                #
                # relevant_content → sections related
                #                    to the user's question
                #
                # scores → similarity scores for those sections
                relevant_content, scores = (
                    retrieve_relevant_content(
                        st.session_state.sections,
                        st.session_state.embeddings,
                        parse_description,
                        top_k=5,
                    )
                )


            # -------------------------------------------------
            # DISPLAY SEMANTIC RELEVANCE SCORES
            # -------------------------------------------------

            # Display a heading for our similarity scores.
            st.subheader("Semantic Relevance")


            # Go through every retrieved section
            # and display its similarity score.
            for i, score in enumerate(scores):

                st.write(
                    f"Section {i + 1}: {score:.3f}"
                )


            # Display the total amount of relevant
            # content that was retrieved.
            st.write(
                f"Relevant content found: "
                f"{len(relevant_content):,} characters"
            )


            # -------------------------------------------------
            # CHECK WHETHER RELEVANT CONTENT EXISTS
            # -------------------------------------------------

            # .strip() removes whitespace.
            #
            # If something remains, we have relevant content
            # that can be sent to Ollama.
            if relevant_content.strip():


                # -------------------------------------------------
                # VIEW RETRIEVED CONTENT
                # -------------------------------------------------

                # Create a collapsible section so the user
                # can inspect exactly what was sent to Ollama.
                with st.expander(
                    "View Relevant Content"
                ):

                    st.text_area(
                        "Relevant Content",
                        relevant_content,
                        height=300
                    )


                # -------------------------------------------------
                # STEP 6 — SEND CONTENT TO OLLAMA
                # -------------------------------------------------

                # Show a loading message while Ollama
                # processes the retrieved content.
                with st.spinner(
                    "Ollama is analyzing the content..."
                ):

                    # Send two things to Ollama:
                    #
                    # 1. relevant_content
                    #    → information retrieved from webpage
                    #
                    # 2. parse_description
                    #    → what the user wants to know
                    #
                    # Ollama then extracts the requested information.
                    result = parse_with_ollama(
                        relevant_content,
                        parse_description
                    )


                # -------------------------------------------------
                # DISPLAY RESULT
                # -------------------------------------------------

                st.subheader("Result")

                try:
                    # Convert Ollama's JSON response into a Python dictionary
                    parsed_result = json.loads(result)

                    # --------------------------------------------------
                    # Convert structured JSON into a natural language
                    # response for the user.
                    # --------------------------------------------------

                    responses = []

                    for key, value in parsed_result.items():

                        # Convert:
                        # refresh_rate -> Refresh Rate
                        # fingerprint_sensor -> Fingerprint Sensor
                        display_key = key.replace(
                            "_", " "
                        ).title()

                        # --------------------------------------------------
                        # Handle missing information
                        # --------------------------------------------------

                        if value is None:

                            responses.append(
                                f"{display_key} is not mentioned "
                                f"on the webpage."
                            )

                        else:

                            responses.append(
                                f"The {display_key.lower()} is {value}."
                            )

                    # Display the natural-language response
                    for response in responses:
                        st.write(response)

                except json.JSONDecodeError:

                    # If Ollama somehow returns invalid JSON,
                    # display the raw response instead.
                    st.write(result)
            # -------------------------------------------------
            # NO RELEVANT CONTENT
            # -------------------------------------------------

            else:

                # If semantic search couldn't find
                # any relevant content, tell the user.
                st.warning(
                    "No relevant content found."
                )