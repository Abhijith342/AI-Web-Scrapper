import re

import streamlit as st

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


# ============================================================
# NLP SETUP
# ============================================================

# Load English stopwords.
#
# Examples:
# "the", "is", "a", "an", "what", "are", "of"
#
# These words usually don't help us identify the actual
# information the user is looking for.
STOP_WORDS = set(
    stopwords.words("english")
)

# Used to convert related word forms into a common form.
#
# Example:
#
# processors -> processor
# running    -> running
#
# This helps keyword matching.
LEMMATIZER = WordNetLemmatizer()


# ============================================================
# EMBEDDING MODEL
# ============================================================

@st.cache_resource
def load_embedding_model():

    # MiniLM converts text into numerical vectors.
    #
    # device="cpu" means we run the embedding model on CPU.
    return SentenceTransformer(
        "all-MiniLM-L6-v2",
        device="cpu"
    )


# Load the model once.
#
# Streamlit normally reruns the Python file whenever the user
# interacts with the UI.
#
# @st.cache_resource prevents the model from being loaded
# again on every rerun.
model = load_embedding_model()


# ============================================================
# TEXT CHUNKING
# ============================================================

def split_into_sections(
    text,
    section_size=500
):

    # Split the webpage into individual lines.
    lines = text.splitlines()

    sections = []

    current_section = []

    current_length = 0

    for line in lines:

        # Check whether adding this line would make the
        # current section larger than our desired size.
        if current_length + len(line) > section_size:

            # If we already have content, save the section.
            if current_section:

                sections.append(
                    "\n".join(current_section)
                )

            # Start a new section.
            current_section = []

            current_length = 0

        current_section.append(line)

        current_length += len(line)

    # Add the final section.
    if current_section:

        sections.append(
            "\n".join(current_section)
        )

    return sections


# ============================================================
# CREATE EMBEDDINGS
# ============================================================

def create_embeddings(sections):

    # Nothing to embed.
    if not sections:

        return None

    # Convert every section into an embedding.
    embeddings = model.encode(
        sections,
        show_progress_bar=False
    )

    return embeddings


# ============================================================
# PROCESS QUERY FOR KEYWORD SEARCH
# ============================================================

def process_query(query):

    # Convert everything to lowercase.
    query = query.lower()

    # Extract individual words.
    #
    # Example:
    #
    # "What processor is used?"
    #
    # becomes:
    #
    # ["what", "processor", "is", "used"]
    words = re.findall(
        r"\b[a-zA-Z0-9]+\b",
        query
    )

    # Remove common words.
    filtered_words = [
        word
        for word in words
        if word not in STOP_WORDS
    ]

    # Lemmatize the remaining words.
    processed_words = [
        LEMMATIZER.lemmatize(word)
        for word in filtered_words
    ]

    return processed_words


# ============================================================
# KEYWORD RETRIEVAL
# ============================================================

def keyword_retrieve(
    sections,
    query,
    top_k=5
):

    # If there are no sections, there is nothing to search.
    if not sections:

        return [], []

    # Process the user's query.
    query_words = process_query(query)

    # Store:
    #
    # (section_index, keyword_score)
    #
    # for every section.
    section_scores = []

    # --------------------------------------------------------
    # Check every webpage section
    # --------------------------------------------------------

    for index, section in enumerate(sections):

        # Convert section to lowercase.
        section_lower = section.lower()

        # Extract words from the section.
        section_words = re.findall(
            r"\b[a-zA-Z0-9]+\b",
            section_lower
        )

        # Lemmatize the section words.
        section_words = {
            LEMMATIZER.lemmatize(word)
            for word in section_words
        }

        # Count how many query words appear in this section.
        matches = sum(
            1
            for word in query_words
            if word in section_words
        )

        # Store the section and its score.
        section_scores.append(
            (
                index,
                matches
            )
        )

    # --------------------------------------------------------
    # Sort sections by keyword score
    # --------------------------------------------------------

    section_scores.sort(
        key=lambda item: item[1],
        reverse=True
    )

    # --------------------------------------------------------
    # Select top-k sections
    # --------------------------------------------------------

    selected_sections = []

    scores = []

    for index, score in section_scores:

        # Don't include sections with zero keyword matches.
        if score == 0:

            continue

        selected_sections.append(
            sections[index]
        )

        scores.append(score)

        if len(selected_sections) >= top_k:

            break

    return selected_sections, scores


# ============================================================
# SEMANTIC RETRIEVAL
# ============================================================

def semantic_retrieve(
    sections,
    embeddings,
    query,
    top_k=5
):

    # Make sure we actually have content.
    if not sections or embeddings is None:

        return [], []

    # Convert the user's query into an embedding.
    query_embedding = model.encode(
        [query]
    )

    # Compare the query embedding against every section.
    similarities = cosine_similarity(
        query_embedding,
        embeddings
    )[0]

    # Sort section indexes from highest similarity
    # to lowest similarity.
    ranked_indexes = similarities.argsort()[::-1]

    selected_sections = []

    scores = []

    for index in ranked_indexes:

        score = float(
            similarities[index]
        )

        selected_sections.append(
            sections[index]
        )

        scores.append(score)

        if len(selected_sections) >= top_k:

            break

    return selected_sections, scores

def keyword_retrieve_with_indexes(sections, query, top_k=5):
    """
    Keyword-based retrieval.

    Returns:
        (section_index, keyword_score)

    We return the INDEX of each section because hybrid
    retrieval needs to know which exact sections were selected.
    """

    if not sections:
        return []

    query_words = process_query(query)

    section_scores = []

    for index, section in enumerate(sections):

        # Convert section into lowercase words
        section_words = re.findall(
            r"\b[a-zA-Z0-9]+\b",
            section.lower()
        )

        # Lemmatize the words in the section
        section_words = {
            LEMMATIZER.lemmatize(word)
            for word in section_words
        }

        # Count how many query words appear
        # in this section
        matches = sum(
            1
            for word in query_words
            if word in section_words
        )

        section_scores.append(
            (index, matches)
        )

    # Highest keyword score first
    section_scores.sort(
        key=lambda item: item[1],
        reverse=True
    )

    # Only keep sections that actually matched
    return [
        (index, score)
        for index, score in section_scores[:top_k]
        if score > 0
    ]


def semantic_retrieve_with_indexes(
    sections,
    embeddings,
    query,
    top_k=5
):
    """
    Semantic retrieval.

    Returns:
        (section_index, similarity_score)
    """

    if not sections or embeddings is None:
        return []

    # Convert the user query into an embedding
    query_embedding = model.encode(
        [query]
    )

    # Compare query embedding with every section
    similarities = cosine_similarity(
        query_embedding,
        embeddings
    )[0]

    # Sort from highest similarity to lowest
    ranked_indexes = similarities.argsort()[::-1]

    results = []

    for index in ranked_indexes[:top_k]:

        results.append(
            (
                int(index),
                float(similarities[index])
            )
        )

    return results


def hybrid_retrieve(
    sections,
    embeddings,
    query,
    top_k=5,
    rrf_k=60
):
    """
    Hybrid retrieval combines:

        1. Semantic search
        2. Keyword search

    using Reciprocal Rank Fusion (RRF).

    RRF does not directly compare the semantic score
    with the keyword score.

    Instead, it compares their rankings.

    Example:

    Semantic:
        section 4 -> rank 1
        section 2 -> rank 2

    Keyword:
        section 2 -> rank 1
        section 7 -> rank 2

    RRF combines these rankings and gives sections
    that perform well in both searches a higher score.
    """

    # --------------------------------------------------
    # 1. Run semantic retrieval
    # --------------------------------------------------

    semantic_results = semantic_retrieve_with_indexes(
        sections,
        embeddings,
        query,
        top_k
    )

    # --------------------------------------------------
    # 2. Run keyword retrieval
    # --------------------------------------------------

    keyword_results = keyword_retrieve_with_indexes(
        sections,
        query,
        top_k
    )

    # --------------------------------------------------
    # 3. Store the combined RRF scores
    # --------------------------------------------------

    rrf_scores = {}

    # --------------------------------------------------
    # 4. Add semantic rankings
    # --------------------------------------------------

    for rank, (index, score) in enumerate(
        semantic_results,
        start=1
    ):

        rrf_scores[index] = (
            rrf_scores.get(index, 0)
            + 1 / (rrf_k + rank)
        )

    # --------------------------------------------------
    # 5. Add keyword rankings
    # --------------------------------------------------

    for rank, (index, score) in enumerate(
        keyword_results,
        start=1
    ):

        rrf_scores[index] = (
            rrf_scores.get(index, 0)
            + 1 / (rrf_k + rank)
        )

    # --------------------------------------------------
    # 6. Sort sections by final RRF score
    # --------------------------------------------------

    ranked_sections = sorted(
        rrf_scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    # --------------------------------------------------
    # 7. Select the top sections
    # --------------------------------------------------

    selected_sections = []
    scores = []

    for index, score in ranked_sections[:top_k]:

        selected_sections.append(
            sections[index]
        )

        scores.append(
            score
        )

    return selected_sections, scores


def retrieve_relevant_content(
    sections,
    embeddings,
    query,
    top_k=5
):
    """
    Main retrieval function used by main.py.

    Previously:
        Semantic retrieval only

    Now:
        Hybrid retrieval
        = Semantic + Keyword + RRF
    """

    selected_sections, scores = hybrid_retrieve(
        sections,
        embeddings,
        query,
        top_k
    )

    relevant_content = "\n\n".join(
        selected_sections
    )

    return (
        relevant_content,
        scores
    )