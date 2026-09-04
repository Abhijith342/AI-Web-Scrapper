# AI Web Scraper

An AI-powered web scraping and question-answering system that extracts information from real websites and answers user queries using semantic search, keyword search, and Llama 3.2.

## 🚀 Overview

This project combines web scraping, Natural Language Processing, semantic retrieval, and Large Language Models to allow users to ask questions about scraped webpages.

The system does not simply send the entire webpage to an LLM. Instead, it:

1. Scrapes the website
2. Cleans the webpage content
3. Splits the content into sections
4. Creates semantic embeddings
5. Retrieves relevant sections using hybrid search
6. Sends only relevant information to the LLM
7. Generates a natural-language answer

## 🏗️ Architecture

```text
User enters URL
       ↓
Selenium + Bright Data
       ↓
Raw HTML
       ↓
BeautifulSoup
       ↓
Cleaned Content
       ↓
Section Splitting
       ↓
MiniLM Embeddings
       ↓
User Query
       ↓
Hybrid Retrieval
(Semantic + Keyword)
       ↓
Relevant Content
       ↓
Llama 3.2
       ↓
Structured Response
       ↓
Natural Language Answer
       ↓
Streamlit UI

✨ Current Features
🌐 Web scraping using Selenium
⚡ Bright Data Scraping Browser
🧹 HTML cleaning using BeautifulSoup
📝 Webpage content segmentation
🧠 Semantic search using Sentence Transformers
🔎 Keyword-based retrieval
🔀 Hybrid retrieval using Reciprocal Rank Fusion (RRF)
🤖 Llama 3.2 integration through Ollama
📦 Structured JSON extraction
💬 Natural-language responses
❌ Missing-information detection
🛒 Tested on e-commerce websites
📚 Tested on information websites
⚡ Support for dynamic JavaScript websites


🛠️ Technologies Used
Python
Streamlit
Selenium
Bright Data
BeautifulSoup
NLTK
Sentence Transformers
all-MiniLM-L6-v2
Scikit-learn
LangChain
Ollama
Llama 3.2

📂 Project Structure

AI-Web-Scraper/
│
├── main.py
├── scrape.py
├── retrieve.py
├── parse.py
├── config.py
├── requirements.txt
├── README.md
├── .gitignore
└── ...

⚙️ Installation
1. Clone the repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd AI-Web-Scraper
2. Create a virtual environment
python -m venv venv
3. Activate the virtual environment
Windows: venv\Scripts\activate
4. Install dependencies
pip install -r requirements.txt

🤖 Ollama Setup

Install Ollama and make sure the required model is available.
ollama pull llama3.2
Check that the model is available:
ollama list

🔐 Configuration

The project uses Bright Data for browser-based web scraping.
Create your configuration according to your local setup.
Do not commit API keys, passwords, or other credentials to GitHub.
Use environment variables or a local configuration file that is excluded using .gitignore.

▶️ How to Run

Activate the virtual environment:
venv\Scripts\activate
Start the Streamlit application:
streamlit run main.py
The application will open in your browser.

💡 Example Queries

For a product webpage:
What processor is used?
How much RAM and storage does it have?
Does it have a fingerprint sensor?
The system extracts only the requested information and returns a natural-language response.

👨‍💻 Project Status

Version: 3 — In Development

The core scraping, cleaning, embedding, hybrid retrieval, and LLM extraction pipeline is currently functional. Additional query capabilities are being developed and tested.
