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
