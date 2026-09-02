# ---------------------------------------------------------
# IMPORT REQUIRED LIBRARIES
# ---------------------------------------------------------

# Streamlit is used here mainly for its caching feature.
# @st.cache_resource allows us to load the embedding model
# only once instead of loading it every time Streamlit
# reruns the application.
import streamlit as st


# SentenceTransformer provides pre-trained models
# that convert text into numerical vectors called
# embeddings.
#
# We use these embeddings to compare the meaning of
# the user's question with the webpage sections.
from sentence_transformers import SentenceTransformer


# cosine_similarity calculates how similar two
# embedding vectors are.
#
# A higher similarity score means the texts are
# semantically more similar.
from sklearn.metrics.pairwise import cosine_similarity


# ---------------------------------------------------------
# LOAD EMBEDDING MODEL
# ---------------------------------------------------------

# @st.cache_resource tells Streamlit to load this model
# only once and reuse it.
#
# Without caching, Streamlit could reload the model
# whenever the user interacts with the application,
# which would make the application much slower.
@st.cache_resource
def load_embedding_model():

    # Load the pre-trained MiniLM model.
    #
    # all-MiniLM-L6-v2 is a lightweight sentence
    # embedding model.
    #
    # It converts text into numerical vectors that
    # represent the meaning of the text.
    #
    # device="cpu" means we run this model on the CPU.
    # This is useful because your GPU has limited VRAM
    # and Ollama already uses the GPU.
    return SentenceTransformer(
        "all-MiniLM-L6-v2",
        device="cpu"
    )


# Load the embedding model.
#
# Because of @st.cache_resource, this model will be
# reused instead of being loaded again on every
# Streamlit interaction.
model = load_embedding_model()


# ---------------------------------------------------------
# SPLIT WEBPAGE INTO SECTIONS
# ---------------------------------------------------------

# This function takes the cleaned webpage text
# and divides it into smaller sections.
#
# Why?
#
# A complete webpage might contain:
#
# 12,000 characters
#
# Sending all of that to the LLM is inefficient.
#
# Instead we create smaller sections:
#
# Webpage
#    ↓
# Section 1
# Section 2
# Section 3
# Section 4
# ...
#
# Later we can search these sections individually.
def split_into_sections(text, section_size=500):

    # Split the complete text into individual lines.
    #
    # Example:
    #
    # "Processor: Ryzen 7"
    # "RAM: 16 GB"
    # "Storage: 512 GB"
    #
    # becomes separate lines.
    lines = text.splitlines()


    # This list will contain the final sections.
    sections = []


    # Temporarily stores lines belonging to
    # the current section.
    current_section = []


    # Keeps track of how many characters
    # are currently in the section.
    current_length = 0


    # Go through every line of the webpage.
    for line in lines:


        # Check whether adding the next line would
        # make the section larger than section_size.
        #
        # By default:
        #
        # section_size = 500
        #
        # So each section will contain roughly
        # 500 characters.
        if current_length + len(line) > section_size:


            # Make sure the current section isn't empty.
            if current_section:

                # Join all lines in the current section
                # into one string.
                sections.append(
                    "\n".join(current_section)
                )


            # Start a new section.
            current_section = []


            # Reset the character counter.
            current_length = 0


        # Add the current line to the section.
        current_section.append(line)


        # Increase the character count by the
        # length of the current line.
        current_length += len(line)


    # After the loop finishes, there may still be
    # a final section that hasn't been added yet.
    if current_section:

        sections.append(
            "\n".join(current_section)
        )


    # Return all the sections.
    return sections


# ---------------------------------------------------------
# CREATE EMBEDDINGS
# ---------------------------------------------------------

# This function converts every webpage section
# into an embedding.
#
# Example:
#
# "AMD Ryzen 7 7445HS Processor"
#
# might become something like:
#
# [0.12, -0.43, 0.81, ...]
#
# The actual embedding contains many numerical
# values representing the semantic meaning of
# the text.
def create_embeddings(sections):


    # If there are no sections, there is nothing
    # to convert into embeddings.
    if not sections:

        return None


    # Convert every section into an embedding.
    #
    # show_progress_bar=False prevents MiniLM
    # from displaying a progress bar in Streamlit.
    embeddings = model.encode(
        sections,
        show_progress_bar=False
    )


    # Return the generated embeddings.
    return embeddings


# ---------------------------------------------------------
# FIND RELEVANT CONTENT
# ---------------------------------------------------------

# This is the most important function in this file.
#
# It performs semantic search.
#
# It receives:
#
# sections:
#     The webpage divided into smaller sections.
#
# embeddings:
#     The numerical representation of every section.
#
# query:
#     The user's question.
#
# top_k:
#     The maximum number of relevant sections
#     we want to retrieve.
def retrieve_relevant_content(
    sections,
    embeddings,
    query,
    top_k=5
):


    # Make sure we actually have webpage sections
    # and embeddings before continuing.
    if not sections or embeddings is None:

        return "", []


    # -----------------------------------------------------
    # CREATE QUERY EMBEDDING
    # -----------------------------------------------------

    # Convert the user's question into an embedding.
    #
    # Example:
    #
    # User asks:
    # "What processor is used?"
    #
    # This question is converted into a numerical
    # vector representing its meaning.
    query_embedding = model.encode(
        [query]
    )


    # -----------------------------------------------------
    # CALCULATE SIMILARITY
    # -----------------------------------------------------

    # Compare the user's question embedding
    # against every webpage section embedding.
    #
    # cosine_similarity returns a similarity score
    # for each section.
    #
    # Example:
    #
    # Section 1 → 0.536
    # Section 2 → 0.521
    # Section 3 → 0.471
    # Section 4 → 0.455
    #
    # Higher score = more semantically similar.
    similarities = cosine_similarity(
        query_embedding,
        embeddings
    )[0]


    # -----------------------------------------------------
    # RANK SECTIONS
    # -----------------------------------------------------

    # Get the indexes of sections sorted according
    # to their similarity score.
    #
    # [::-1] reverses the order so that the
    # highest similarity comes first.
    #
    # Example:
    #
    # Original:
    # [0.21, 0.53, 0.31, 0.76]
    #
    # Ranked indexes:
    # [3, 1, 2, 0]
    ranked_indexes = similarities.argsort()[::-1]


    # This will store the sections that we
    # decide to send to Ollama.
    relevant_sections = []


    # This will store the similarity score
    # for each selected section.
    #
    # We use these scores in main.py to show
    # "Semantic Relevance" to the user.
    scores = []


    # -----------------------------------------------------
    # SELECT TOP-K SECTIONS
    # -----------------------------------------------------

    # Go through the sections from highest
    # similarity to lowest similarity.
    for index in ranked_indexes:


        # Convert the NumPy similarity value
        # into a normal Python float.
        score = float(similarities[index])


        # Add the corresponding webpage section
        # to our relevant sections.
        relevant_sections.append(
            sections[index]
        )


        # Store its similarity score.
        scores.append(score)


        # Stop once we have collected the
        # required number of sections.
        #
        # With:
        #
        # top_k = 5
        #
        # we retrieve at most five sections.
        if len(relevant_sections) >= top_k:

            break


    # -----------------------------------------------------
    # CHECK WHETHER WE FOUND ANYTHING
    # -----------------------------------------------------

    # This is a safety check.
    #
    # Normally relevant_sections should contain
    # something if sections were provided.
    if not relevant_sections:

        return "", []


    # -----------------------------------------------------
    # RETURN RESULTS
    # -----------------------------------------------------

    # Join all retrieved sections together.
    #
    # "\n\n" gives two line breaks between sections
    # so that Ollama can distinguish them more easily.
    #
    # We return BOTH:
    #
    # 1. relevant content
    # 2. similarity scores
    return (
        "\n\n".join(relevant_sections),
        scores
    )