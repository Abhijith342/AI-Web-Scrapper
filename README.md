# 🤖 AI Web Scraper

> An AI-powered web intelligence system that scrapes real-world websites, retrieves relevant information using hybrid search, and answers natural-language questions using Llama 3.2.

---

## 📌 Overview

**AI Web Scraper** is a Python-based web intelligence application that allows users to scrape a website and ask questions about its content using natural language.

Instead of sending an entire webpage directly to an LLM, the system uses a **Retrieval-Augmented Generation (RAG)-style pipeline** to identify and provide only the most relevant sections to the language model.

The system combines:

- 🌐 Selenium
- ⚡ Bright Data Scraping Browser
- 🧹 BeautifulSoup
- 🧠 Sentence Transformers
- 🔎 Keyword Search
- 🔀 Hybrid Retrieval
- 🤖 Llama 3.2
- 🦙 Ollama
- 🎈 Streamlit

The current Version 3 focuses on building a reliable foundation for webpage question answering across different types of websites.

---

# ✨ Features

### 🌐 Intelligent Web Scraping

Scrape webpages using Selenium with Bright Data's browser infrastructure, including dynamically rendered JavaScript websites.

### 🧹 Webpage Cleaning

Removes unnecessary HTML elements such as:

- Scripts
- Styles
- SVGs
- Navigation
- Headers
- Footers
- Iframes

and converts the remaining webpage into clean text.

### 📝 Content Segmentation

Large webpages are divided into smaller sections so that relevant information can be retrieved efficiently.

### 🧠 Semantic Search

Uses:

`all-MiniLM-L6-v2`

to convert webpage sections and user queries into vector embeddings.

This allows the system to find information based on **meaning**, not just exact keywords.

### 🔎 Keyword Search

Traditional keyword-based retrieval is also used to identify sections containing important query terms.

### 🔀 Hybrid Retrieval

The system combines:

**Semantic Search + Keyword Search**

using **Reciprocal Rank Fusion (RRF)**.

This improves retrieval by combining semantic relevance with exact keyword matching.

### 🤖 Local LLM Processing

Relevant webpage content is passed to:

**Llama 3.2 via Ollama**

The LLM is instructed to:

- Use only webpage information
- Avoid outside knowledge
- Never guess missing information
- Extract only requested fields
- Return structured information

### 💬 Natural-Language Answers

Although structured JSON is used internally, the final result is presented to the user as a natural-language response.

Example:

> The processor is AMD Ryzen 7 7445HS.

rather than exposing raw JSON.

### ❌ Missing Information Detection

If the requested information is not explicitly available on the webpage, the system can identify it instead of inventing an answer.

### ⚡ Dynamic Website Support

Selenium allows the scraper to work with websites whose content is dynamically rendered using JavaScript.

---

# 🏗️ System Architecture

```text
                         USER
                           │
                           ▼
                    Enter Website URL
                           │
                           ▼
              ┌────────────────────────┐
              │ Selenium + Bright Data │
              └────────────┬───────────┘
                           │
                           ▼
                       Raw HTML
                           │
                           ▼
                    ┌─────────────┐
                    │ BeautifulSoup│
                    └──────┬──────┘
                           │
                           ▼
                    Cleaned Content
                           │
                           ▼
                   Section Splitting
                           │
                           ▼
              ┌────────────────────────┐
              │ Sentence Transformer   │
              │ all-MiniLM-L6-v2       │
              └────────────┬───────────┘
                           │
                           ▼
                     Embeddings
                           │
                           │
                    USER QUESTION
                           │
                           ▼
              ┌────────────────────────┐
              │   Hybrid Retrieval     │
              │                        │
              │ Semantic Search        │
              │        +               │
              │ Keyword Search         │
              │        ↓               │
              │ Reciprocal Rank Fusion │
              └────────────┬───────────┘
                           │
                           ▼
                  Relevant Content
                           │
                           ▼
                 ┌─────────────────┐
                 │    Llama 3.2    │
                 │     Ollama      │
                 └────────┬────────┘
                          │
                          ▼
                 Structured Response
                          │
                          ▼
                 Natural-Language Answer
                          │
                          ▼
                    Streamlit UI
```

---

# 🔄 How It Works

## 1️⃣ Website Scraping

The user enters a webpage URL.

Selenium connects to the website through Bright Data's Scraping Browser.

```text
URL
 ↓
Selenium
 ↓
Bright Data
 ↓
Rendered Webpage
 ↓
HTML
```

---

## 2️⃣ HTML Extraction

BeautifulSoup extracts the webpage body and removes unnecessary elements.

```text
Raw HTML
   ↓
BeautifulSoup
   ↓
Remove scripts/styles/navigation/etc.
   ↓
Clean text
```

---

## 3️⃣ Content Splitting

The cleaned webpage is divided into smaller sections.

This prevents the LLM from processing the entire webpage unnecessarily.

```text
Cleaned Webpage
      ↓
Section 1
Section 2
Section 3
Section 4
...
```

---

## 4️⃣ Embedding Generation

Each section is converted into a vector using:

```text
all-MiniLM-L6-v2
```

These vectors represent the semantic meaning of each section.

---

## 5️⃣ User Query

The user asks a natural-language question.

Example:

```text
What processor is used?
```

The question is also converted into an embedding.

---

## 6️⃣ Hybrid Retrieval

Two retrieval strategies are used.

### Semantic Retrieval

Finds sections that are semantically similar to the query.

### Keyword Retrieval

Finds sections containing relevant query terms.

The two rankings are combined using:

```text
Reciprocal Rank Fusion (RRF)
```

The most relevant sections are then selected.

---

## 7️⃣ LLM Extraction

Only the relevant content is passed to Llama 3.2.

The model extracts the requested information while following strict rules.

Example:

```text
User:
What processor is used?

Relevant Content:
AMD Ryzen 7 7445HS
16GB RAM
512GB SSD
144Hz Display
```

The system internally produces:

```json
{
  "processor": "AMD Ryzen 7 7445HS"
}
```

---

## 8️⃣ Natural-Language Response

The structured response is converted into a user-friendly answer:

```text
The processor is AMD Ryzen 7 7445HS.
```

---

# 🧪 Example Queries

### Single-field extraction

```text
What processor is used?
```

### Multi-field extraction

```text
What processor, RAM and storage does it have?
```

### Missing information

```text
Does it have a fingerprint sensor?
```

### Product information

```text
What is the battery capacity?
```

### Information websites

```text
What is artificial intelligence?
```

More advanced query types such as comparisons, calculations, aggregation, and complex list queries are part of the ongoing Version 3 development.

---

# 🌍 Tested Website Types

| Website Type | Example | Status |
|---|---|---|
| 🛒 E-commerce | Amazon | ✅ Tested |
| 🛒 E-commerce | Flipkart | ✅ Tested |
| 📚 Information | Wikipedia | ✅ Tested |
| ⚡ Dynamic JavaScript | Sports/statistics website | ✅ Tested |
| 📖 Documentation | — | 🚧 Planned |
| 📰 News/Articles | — | 🚧 Planned |

---

# 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | Core programming language |
| **Streamlit** | Web interface |
| **Selenium** | Browser automation and dynamic webpage scraping |
| **Bright Data** | Scraping Browser infrastructure |
| **BeautifulSoup** | HTML parsing and cleaning |
| **NLTK** | Text preprocessing |
| **Sentence Transformers** | Semantic embeddings |
| **all-MiniLM-L6-v2** | Embedding model |
| **Scikit-learn** | Cosine similarity |
| **LangChain** | LLM pipeline |
| **Ollama** | Local LLM runtime |
| **Llama 3.2** | Language model |

---

# 📂 Project Structure

```text
AI-Web-Scraper/
│
├── main.py              # Streamlit application
├── scrape.py            # Website scraping and HTML processing
├── retrieve.py          # Semantic, keyword and hybrid retrieval
├── parse.py             # Llama-based information extraction
├── config.py            # Local configuration
│
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
├── .gitignore           # Ignored files
│
└── ...
```

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

Move into the project directory:

```bash
cd AI-Web-Scraper
```

---

## 2. Create a Virtual Environment

```bash
python -m venv venv
```

---

## 3. Activate the Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🤖 Ollama Setup

The project uses **Llama 3.2 through Ollama**.

Install Ollama on your system and download the model:

```bash
ollama pull llama3.2
```

Verify that the model is available:

```bash
ollama list
```

You should see:

```text
llama3.2
```

Make sure Ollama is running before using the application.

---

# 🔐 Bright Data Configuration

The scraper uses Bright Data's Scraping Browser.

You need to configure your Bright Data WebDriver connection before running the application.

Your credentials should **never be committed to GitHub**.

Use environment variables or a local configuration file that is excluded from Git.

Example:

```text
.env
```

Make sure sensitive files are included in `.gitignore`.

---

# ▶️ Running the Application

Activate the virtual environment:

```bash
venv\Scripts\activate
```

Start Streamlit:

```bash
streamlit run main.py
```

The application will open in your browser.

---

# 🖥️ Application Workflow

```text
1. Enter Website URL
          ↓
2. Click "Scrape the Site"
          ↓
3. Website is scraped
          ↓
4. Content is cleaned
          ↓
5. Sections are created
          ↓
6. Embeddings are generated
          ↓
7. Enter your question
          ↓
8. Relevant content is retrieved
          ↓
9. Llama 3.2 analyzes the content
          ↓
10. Natural-language answer is displayed
```

---

# 🚧 Version 3 Roadmap

The project is currently being developed toward a more general-purpose webpage intelligence system.

## ✅ Completed

- [x] Web scraping
- [x] Dynamic webpage scraping
- [x] HTML extraction
- [x] HTML cleaning
- [x] Content segmentation
- [x] Sentence Transformer embeddings
- [x] Semantic retrieval
- [x] Keyword retrieval
- [x] Hybrid retrieval
- [x] Reciprocal Rank Fusion
- [x] Llama 3.2 integration
- [x] Structured extraction
- [x] Single-field extraction
- [x] Multi-field extraction
- [x] Missing-field handling
- [x] Natural-language output

## 🔨 In Development

- [ ] Query classification
- [ ] Robust list extraction
- [ ] Comparison engine
- [ ] Multi-entity comparison
- [ ] Calculation engine
- [ ] Aggregation
- [ ] General webpage question answering
- [ ] More robust error handling
- [ ] Expanded website testing
- [ ] Performance optimization

---

# 🧠 Planned Query Engine

The final Version 3 architecture will classify the user's question before processing it.

```text
                     USER QUERY
                         │
                         ▼
                  QUERY ANALYZER
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
       FACT/LIST     COMPARISON     CALCULATION
          │              │              │
          ▼              ▼              ▼
      Extraction     Retrieval       Python
          │          + Python        Logic
          │          Comparison          │
          └──────────────┬───────────────┘
                         │
                         ▼
                   GENERAL QA
                         │
                         ▼
                 ANSWER GENERATOR
                         │
                         ▼
                 NATURAL LANGUAGE
```

The goal is to use the LLM for **language understanding and extraction**, while using deterministic Python logic whenever accuracy is important.

---

# 🎯 Project Goals

The final system aims to provide:

- Reliable webpage information extraction
- Semantic understanding of user queries
- Accurate retrieval of relevant webpage content
- Reduced dependency on sending entire webpages to an LLM
- Support for dynamic websites
- Structured information extraction
- Deterministic calculations and comparisons
- Natural-language answers
- A modular architecture that can be extended to different query types

---

# 📊 Why Hybrid Retrieval?

Pure keyword search can fail when the user uses different words with the same meaning.

For example:

```text
Query:
How much memory does the laptop have?
```

The webpage might say:

```text
16GB RAM
```

Semantic retrieval can recognize that **memory** and **RAM** are related.

However, keyword search is useful when exact terms matter.

Therefore:

```text
Semantic Search
      +
Keyword Search
      ↓
Hybrid Retrieval
      ↓
Reciprocal Rank Fusion
```

provides a stronger retrieval mechanism than relying on only one method.

---

# 🔒 Information Grounding

The LLM is instructed to use the scraped webpage as its source of truth.

The extraction pipeline follows rules such as:

```text
Use webpage content only
        ↓
Do not use outside knowledge
        ↓
Do not guess
        ↓
Do not invent missing values
        ↓
Return only requested information
```

This helps reduce hallucinations during information extraction.

---

# 🚀 Future Vision

The long-term goal is to evolve this project from an AI web scraper into a **general-purpose Web Intelligence System**.

Users should eventually be able to ask questions such as:

```text
What processor does this laptop use?
```

```text
Which laptop is cheaper?
```

```text
Who has more career goals?
```

```text
What are the main applications of AI?
```

```text
What is the average price of these products?
```

```text
Compare these two products.
```

without needing to know how the underlying webpage is structured.

---

# 📌 Project Status

**Current Version:** `V3 — In Development`

The core scraping, cleaning, embedding, hybrid retrieval, and LLM extraction pipeline is functional.

The remaining Version 3 work focuses on building a robust query-processing layer capable of handling comparisons, calculations, lists, aggregations, and general webpage questions.

---

# 👨‍💻 Author

**Abhijith**

B.Tech — Artificial Intelligence & Data Science

---

## ⭐ Project Philosophy

```text
Scrape → Retrieve → Understand → Answer
```

The objective is not simply to scrape webpages, but to build an intelligent system that can **understand what information the user is asking for and retrieve it accurately from the web content**.
