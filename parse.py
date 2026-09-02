# ---------------------------------------------------------
# IMPORT REQUIRED LIBRARIES
# ---------------------------------------------------------

# OllamaLLM allows us to communicate with our
# locally running Ollama model.
from langchain_ollama import OllamaLLM

# ChatPromptTemplate is used to create a prompt
# containing variables such as {dom_content}
# and {parse_description}.
from langchain_core.prompts import ChatPromptTemplate


# ---------------------------------------------------------
# PROMPT TEMPLATE
# ---------------------------------------------------------

# This is the instruction that will be sent to Ollama.
#
# We are telling the LLM:
#
# "Here is some webpage content.
#  Here is what the user wants.
#  Extract only the requested information."
#
# {dom_content} and {parse_description} are variables.
# Their actual values are supplied later inside
# chain.invoke().
template = """
You are a strict information extraction system.

Your ONLY source of truth is the webpage content provided below.

WEBPAGE CONTENT:
{dom_content}

USER REQUEST:
{parse_description}

RULES:

1. Use ONLY information explicitly present in the webpage content.
2. NEVER use your own knowledge.
3. NEVER guess or infer missing values.
4. NEVER use information from other products or websites.
5. If a requested value is not explicitly present, return null.
6. If the webpage says "up to", preserve "up to".
7. Do not convert or modify values.
8. Return ONLY valid JSON.
9. Do not provide explanations.
10. Do not use markdown code fences.

Return the requested information as JSON.
"""


# ---------------------------------------------------------
# LOAD OLLAMA MODEL
# ---------------------------------------------------------

# Create an Ollama LLM object.
#
# "llama3.2" is the model that Ollama will use
# to analyze the webpage content.
#
# Since Ollama is running locally, the request
# does not need to go to an external AI API.
model = OllamaLLM(
    model="llama3.2"
)


# ---------------------------------------------------------
# PARSE FUNCTION
# ---------------------------------------------------------

# This function receives:
#
# dom_content:
#     The relevant webpage content retrieved
#     by our semantic search.
#
# parse_description:
#     The question/instruction entered by the user.
#
# Example:
#
# dom_content:
#     "Processor: AMD Ryzen 7 7445HS..."
#
# parse_description:
#     "What processor is used?"
#
# The function then asks Ollama to extract
# the requested information.
def parse_with_ollama(
    dom_content,
    parse_description
):


    # -----------------------------------------------------
    # CREATE PROMPT
    # -----------------------------------------------------

    # Convert our template into a LangChain prompt.
    #
    # LangChain recognizes:
    #
    # {dom_content}
    # {parse_description}
    #
    # as variables that will be filled in later.
    prompt = ChatPromptTemplate.from_template(
        template
    )


    # -----------------------------------------------------
    # CREATE AI CHAIN
    # -----------------------------------------------------

    # The "|" operator connects the prompt to the model.
    #
    # So the flow becomes:
    #
    # Prompt
    #   ↓
    # Ollama
    #
    # When we invoke the chain, the prompt is first
    # filled with our webpage content and user request,
    # then sent to Llama 3.2.
    chain = prompt | model


    # -----------------------------------------------------
    # SEND DATA TO OLLAMA
    # -----------------------------------------------------

    # Provide the actual values for the variables
    # used inside our prompt.
    #
    # "dom_content" replaces:
    #
    # {dom_content}
    #
    # "parse_description" replaces:
    #
    # {parse_description}
    response = chain.invoke({
        "dom_content": dom_content,
        "parse_description": parse_description
    })


    # -----------------------------------------------------
    # RETURN OLLAMA RESPONSE
    # -----------------------------------------------------

    # Ollama's response is returned to main.py.
    #
    # main.py will then use json.loads()
    # to convert the JSON string into a Python dictionary.
    return response