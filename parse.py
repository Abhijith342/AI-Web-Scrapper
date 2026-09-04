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

The user may request one or multiple pieces of information.

You MUST identify exactly what information the user is requesting.

IMPORTANT:

If the user asks for ONE piece of information:
- Return ONLY that one field.
- Do NOT return other information merely because it appears
  in the webpage content.

If the user asks for MULTIPLE pieces of information:
- Return ONLY those requested fields.
- Process each requested field independently.

For EACH requested field:

1. Identify the exact field requested by the user.
2. Search the ENTIRE webpage content for that field.
3. Find the exact value associated with that field.
4. Return only that requested field.
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
SINGLE-FIELD EXTRACTION EXAMPLES
============================================================

USER REQUEST:
"What processor is used?"

If the webpage contains:

"AMD Ryzen 7 7445HS"
"16GB RAM"
"512GB SSD"
"144Hz"

Return ONLY:

{{"processor": "AMD Ryzen 7 7445HS"}}

Do NOT return RAM, storage, refresh rate, GPU,
battery, or any other fields.


USER REQUEST:
"What is the refresh rate?"

Return ONLY:

{{"refresh_rate": "144Hz"}}


USER REQUEST:
"How much RAM does it have?"

Return ONLY:

{{"ram": "16GB"}}


USER REQUEST:
"What processor and RAM are used?"

Return ONLY:

{{"processor": "AMD Ryzen 7 7445HS", "ram": "16GB"}}

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
FINAL OUTPUT FORMAT
============================================================

Your response MUST contain ONLY the JSON object.

DO NOT write:
- explanations
- reasoning
- introductions
- conclusions
- notes
- comments
- markdown
- code fences
- sentences before the JSON
- sentences after the JSON

BAD RESPONSE:

I searched the webpage and found that the fingerprint
sensor is not mentioned.

{{"fingerprint_sensor": null}}

GOOD RESPONSE:

{{"fingerprint_sensor": null}}

Return ONLY the JSON object and NOTHING ELSE.
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

    # --------------------------------------------------------
    # CLEAN LLM RESPONSE
    # --------------------------------------------------------
    #
    # Llama may sometimes return:
    #
    # "Here is the answer:
    #  {\"ram\": \"24 GB\"}"
    #
    # instead of returning only:
    #
    # {"ram": "24 GB"}
    #
    # We remove unnecessary text before returning the result.
    # --------------------------------------------------------

    response = response.strip()

    # Remove markdown code fences if the model adds them.
    response = response.replace("```json", "")
    response = response.replace("```", "")
    response = response.strip()

    # --------------------------------------------------------
    # FIND JSON OBJECT
    # --------------------------------------------------------

    start = response.find("{")
    end = response.rfind("}")

    # If JSON was found, return only the JSON portion.
    if start != -1 and end != -1 and start < end:
        response = response[start:end + 1]

    return response