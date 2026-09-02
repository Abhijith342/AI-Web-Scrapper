from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate


# ============================================================
# EXTRACTION PROMPT
# ============================================================

template = """
You are a strict information extraction system.

Your ONLY source of truth is the webpage content provided below.

WEBPAGE CONTENT:
{dom_content}

USER REQUEST:
{parse_description}


============================================================
EXTRACTION INSTRUCTIONS
============================================================

The user may request multiple pieces of information.

You MUST process EVERY requested piece of information
independently.

For EACH requested field:

1. Search the ENTIRE webpage content.
2. Find the exact value associated with that field.
3. Map that value to the requested field.
4. Do NOT stop after finding other fields.
5. If the value is not explicitly present, return null.
6. Never guess or infer a value.
7. Never use your own knowledge.


============================================================
IMPORTANT MAPPING RULES
============================================================

Use the meaning of the webpage text when mapping values.

Examples:

"AMD Ryzen 7 7445HS"
→ processor

"16GB RAM"
→ ram

"512GB SSD"
→ storage

"RTX 3050-4GB"
→ gpu

"144Hz"
→ refresh_rate

"48Whrs"
→ battery


============================================================
STRICT RULES
============================================================

1. Use ONLY information explicitly present in the webpage
   content.

2. NEVER use outside knowledge.

3. NEVER guess missing values.

4. NEVER combine information from unrelated products.

5. If a requested value is not explicitly present,
   return null.

6. Preserve the original value as much as possible.

7. If the webpage says "up to", preserve "up to".

8. Do not convert units.

9. Do not calculate values.

10. Process EVERY requested field.

11. Return ONLY valid JSON.

12. Do NOT use markdown code fences.

13. Do NOT provide explanations.

14. Do NOT add fields that were not requested.


============================================================
FINAL CHECK
============================================================

Before returning the answer, verify:

- Did I process every requested field?
- Did I search the entire supplied content?
- Did I avoid guessing?
- Did I return null for genuinely missing information?
- Is the result valid JSON?


Return ONLY the JSON object.
"""


# ============================================================
# OLLAMA MODEL
# ============================================================

model = OllamaLLM(
    model="llama3.2"
)


# ============================================================
# PARSE CONTENT
# ============================================================

def parse_with_ollama(
    dom_content,
    parse_description
):

    # Create the prompt template.
    prompt = ChatPromptTemplate.from_template(
        template
    )

    # Connect the prompt to Ollama.
    chain = prompt | model

    # Send the webpage content and user's request.
    response = chain.invoke({

        "dom_content": dom_content,

        "parse_description": parse_description

    })

    return response