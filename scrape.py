# --------------------------------------------------
# IMPORT REQUIRED LIBRARIES
# --------------------------------------------------

# re is Python's regular expression library.
#
# We use it to find individual words inside
# the user's query and webpage content.
import re


# Selenium is used to control the browser
# and load websites dynamically.
import selenium.webdriver as webdriver


# SBR_WEBDRIVER contains the Bright Data
# Web Scraper Browser connection details.
from config import SBR_WEBDRIVER


# BeautifulSoup is used to parse HTML
# and extract readable content from it.
from bs4 import BeautifulSoup


# NLTK stopwords contains common English words
# that usually don't provide much meaning
# for searching.
#
# Examples:
#
# "the"
# "is"
# "a"
# "what"
# "are"
from nltk.corpus import stopwords


# WordNetLemmatizer converts words into
# their base/dictionary form.
#
# Examples:
#
# cars → car
# running → running/run depending on context
# processors → processor
from nltk.stem import WordNetLemmatizer


# --------------------------------------------------
# NLP SETUP
# --------------------------------------------------

# Load all English stopwords into a set.
#
# A set is used because checking whether a word
# exists in a set is fast.
STOP_WORDS = set(
    stopwords.words("english")
)


# Create a lemmatizer object.
#
# We will use this to convert words into
# their base forms.
LEMMATIZER = WordNetLemmatizer()


# --------------------------------------------------
# SCRAPING
# --------------------------------------------------

# This function takes a website URL and returns
# the HTML content of that webpage.
#
# Example:
#
# scrape_website("https://example.com")
#
# returns the HTML source of the page.
def scrape_website(website):

    # Print a message in the terminal so that
    # we know the browser is being launched.
    print("Launching chrome browser...")


    # Create Chrome browser options.
    #
    # We can add things such as headless mode,
    # user-agent settings, etc. here.
    options = webdriver.ChromeOptions()


    # Create a remote Selenium browser session.
    #
    # Instead of running Chrome locally,
    # the request is sent through Bright Data's
    # Scraping Browser.
    driver = webdriver.Remote(
        command_executor=SBR_WEBDRIVER,
        options=options
    )


    try:

        # Open the requested website.
        driver.get(website)


        # Display a message after the page
        # has successfully loaded.
        print("Page loaded...")


        # Get the complete HTML source of the
        # currently loaded webpage.
        html = driver.page_source


        # Return the HTML to the calling function.
        return html


    finally:

        # Always close the browser session.
        #
        # This is important because otherwise
        # browser sessions could remain running
        # and consume system resources.
        driver.quit()


# --------------------------------------------------
# EXTRACT BODY
# --------------------------------------------------

# This function extracts only the <body>
# portion of the webpage.
#
# We don't need the complete HTML because
# much of it contains metadata, scripts,
# styles, etc.
def extract_body_content(htmlcontent):


    # Convert the HTML string into a
    # BeautifulSoup object so we can
    # navigate and manipulate the HTML.
    soup = BeautifulSoup(
        htmlcontent,
        "html.parser"
    )


    # Get the <body> element.
    body_content = soup.body


    # Check whether the webpage actually
    # contains a body element.
    if body_content:

        # Convert the body back into a string
        # and return it.
        return str(body_content)


    # If there is no body element,
    # return an empty string.
    return ""


# --------------------------------------------------
# CLEAN HTML
# --------------------------------------------------

# This function removes unnecessary HTML
# elements and converts the remaining content
# into plain readable text.
def clean_body_content(body_content):


    # Parse the body HTML using BeautifulSoup.
    soup = BeautifulSoup(
        body_content,
        "html.parser"
    )


    # --------------------------------------------------
    # REMOVE UNNECESSARY HTML ELEMENTS
    # --------------------------------------------------

    # These elements usually contain information
    # that isn't useful for our AI extraction.
    #
    # script  → JavaScript code
    # style   → CSS
    # noscript → fallback content
    # svg     → graphics/icons
    # iframe  → embedded webpages
    # nav     → navigation menus
    # footer  → footer information
    # header  → header/navigation information
    for element in soup([
        "script",
        "style",
        "noscript",
        "svg",
        "iframe",
        "nav",
        "footer",
        "header"
    ]):

        # Completely remove the element
        # from the BeautifulSoup tree.
        element.decompose()


    # --------------------------------------------------
    # CONVERT HTML TO TEXT
    # --------------------------------------------------

    # Extract all readable text from the HTML.
    #
    # separator="\n" means that different
    # HTML elements will be separated by
    # new lines.
    cleaned_content = soup.get_text(
        separator="\n"
    )


    # --------------------------------------------------
    # REMOVE EMPTY LINES
    # --------------------------------------------------

    # Webpages often contain many unnecessary
    # blank lines.
    #
    # This converts something like:
    #
    # Processor
    #
    #
    #
    # Ryzen 7
    #
    # into:
    #
    # Processor
    # Ryzen 7
    cleaned_content = "\n".join(
        line.strip()
        for line in cleaned_content.splitlines()
        if line.strip()
    )


    # Return the cleaned webpage text.
    return cleaned_content


# --------------------------------------------------
# PROCESS USER QUERY
# --------------------------------------------------

# This function prepares the user's question
# before performing keyword-based searching.
#
# Example:
#
# "What processors are used in this laptop?"
#
# might become:
#
# ["processor", "used", "laptop"]
def process_query(query):


    # Convert the entire query to lowercase.
    #
    # This makes searching case-insensitive.
    #
    # "Processor" and "processor"
    # will be treated as the same word.
    query = query.lower()


    # --------------------------------------------------
    # EXTRACT WORDS
    # --------------------------------------------------

    # Use a regular expression to extract words
    # and numbers from the query.
    #
    # Example:
    #
    # "What is the RTX 3050 GPU?"
    #
    # becomes approximately:
    #
    # ["what", "is", "the", "rtx", "3050", "gpu"]
    words = re.findall(
        r"\b[a-zA-Z0-9]+\b",
        query
    )


    # --------------------------------------------------
    # REMOVE STOPWORDS
    # --------------------------------------------------

    # Remove common English words that usually
    # don't provide useful search information.
    #
    # For example:
    #
    # "What is the processor?"
    #
    # could become:
    #
    # ["processor"]
    filtered_words = [
        word
        for word in words
        if word not in STOP_WORDS
    ]


    # --------------------------------------------------
    # LEMMATIZATION
    # --------------------------------------------------

    # Convert words into their base form.
    #
    # This helps match slightly different
    # versions of the same word.
    #
    # Example:
    #
    # processors → processor
    processed_words = [
        LEMMATIZER.lemmatize(word)
        for word in filtered_words
    ]


    # Return the processed query words.
    return processed_words


# --------------------------------------------------
# FIND RELEVANT CONTENT
# --------------------------------------------------

# This function performs keyword-based retrieval.
#
# It receives:
#
# dom_content:
#     The cleaned webpage text.
#
# parse_description:
#     The question entered by the user.
#
# It then searches the webpage for lines
# containing words related to the query.
def find_relevant_content(
    dom_content,
    parse_description
):


    # Process the user's question first.
    #
    # Example:
    #
    # "What processors are used?"
    #
    # becomes something like:
    #
    # ["processor", "used"]
    query_words = process_query(
        parse_description
    )


    # Print the processed query in the terminal.
    #
    # This is useful for debugging and
    # understanding what the NLP system
    # is actually searching for.
    print(
        "Processed query:",
        query_words
    )


    # Split the webpage into individual lines.
    lines = dom_content.splitlines()


    # This list will store lines that contain
    # words matching the user's query.
    relevant_lines = []


    # --------------------------------------------------
    # SEARCH THROUGH EVERY WEBPAGE LINE
    # --------------------------------------------------

    # Go through each line of the webpage.
    #
    # enumerate() gives us:
    #
    # i    → line number/index
    # line → actual text
    for i, line in enumerate(lines):


        # Convert the current line to lowercase
        # so our comparison is case-insensitive.
        line_lower = line.lower()


        # --------------------------------------------------
        # EXTRACT WORDS FROM CURRENT LINE
        # --------------------------------------------------

        # Extract individual words from the webpage line.
        #
        # Example:
        #
        # "AMD Ryzen 7 7445HS Processor"
        #
        # becomes approximately:
        #
        # {"amd", "ryzen", "7", "7445hs", "processor"}
        line_words = set(
            re.findall(
                r"\b[a-zA-Z0-9]+\b",
                line_lower
            )
        )


        # --------------------------------------------------
        # LEMMATIZE WEBPAGE WORDS
        # --------------------------------------------------

        # Convert webpage words to their
        # base/dictionary forms.
        #
        # This allows:
        #
        # processor
        #
        # and:
        #
        # processors
        #
        # to be treated similarly.
        line_words = {
            LEMMATIZER.lemmatize(word)
            for word in line_words
        }


        # --------------------------------------------------
        # COUNT MATCHING WORDS
        # --------------------------------------------------

        # Count how many words from the user's
        # query are present in the current webpage line.
        #
        # Example:
        #
        # Query:
        # ["processor", "gpu"]
        #
        # Line:
        # "Processor: Ryzen 7"
        #
        # processor → match
        # gpu       → no match
        #
        # matches = 1
        matches = sum(
            1
            for word in query_words
            if word in line_words
        )


        # --------------------------------------------------
        # IF A MATCH IS FOUND
        # --------------------------------------------------

        # If at least one query word appears
        # in the current webpage line...
        if matches > 0:


            # --------------------------------------------------
            # INCLUDE SURROUNDING CONTEXT
            # --------------------------------------------------

            # Instead of taking only the matching line,
            # we also include three lines before it.
            #
            # This is useful because webpages often
            # separate labels and values.
            #
            # Example:
            #
            # Processor
            # AMD Ryzen 7
            # Architecture
            # Zen 4
            #
            # If "processor" matches, surrounding
            # lines help preserve the actual value.
            start = max(
                0,
                i - 3
            )


            # Include three lines after the matching line.
            #
            # max/min are used to prevent the index
            # from going outside the webpage.
            end = min(
                len(lines),
                i + 4
            )


            # Add the surrounding lines to our
            # relevant content.
            relevant_lines.extend(
                lines[start:end]
            )


    # --------------------------------------------------
    # REMOVE DUPLICATE LINES
    # --------------------------------------------------

    # The same line may be added multiple times
    # because several nearby lines can match.
    #
    # We therefore create a new list containing
    # only unique lines.
    unique_lines = []


    # Go through all retrieved lines.
    for line in relevant_lines:


        # Add the line only if we haven't
        # already added it.
        if line not in unique_lines:

            unique_lines.append(line)


    # --------------------------------------------------
    # RETURN RELEVANT CONTENT
    # --------------------------------------------------

    # Join all unique lines into one string
    # separated by new lines.
    return "\n".join(unique_lines)