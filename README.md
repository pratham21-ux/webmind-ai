# 🧠 WebMind AI

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://webmind-ai-lybsngfxqia8ayrp294mmn.streamlit.app)

WebMind AI is a Universal Web RAG (Retrieval-Augmented Generation) pipeline. It allows users to paste any URL, instantly scrape and index the text, and chat with an AI assistant that grounds its answers strictly in the provided website content.

## ✨ Features
* **Universal Scraping:** Extracts clean text from any valid web URL using BeautifulSoup4.
* **Smart Chunking:** Processes text efficiently for vector embedding to ensure highly relevant context retrieval.
* **Vector Database:** Uses Qdrant for lightning-fast semantic search and memory management.
* **Enterprise Security:** Securely manages API keys with cloud-native fallback methods to prevent accidental exposure.
* **Optimized Deployment:** Utilizes Streamlit resource caching to handle heavy AI models and bypass cloud server boot timeouts.

## 🛠️ Tech Stack
* **Frontend UI:** Streamlit
* **AI Engine:** Google Gemini 3 Flash (via Google GenAI SDK)
* **Vector DB:** Qdrant (Local/Memory)
* **Language:** Python 3.x

## 🚀 How to Run Locally

1. **Clone the repository:**
   git clone https://github.com/pratham21-ux/webmind-ai.git
   cd webmind-ai

2. **Set up a Virtual Environment (Optional but Recommended):**
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

3. **Install dependencies:**
   pip install -r requirements.txt

4. **Set up Environment Variables:**
   Create a .env file in the root directory and add your Google Gemini API key:
   GEMINI_API_KEY=your_actual_api_key_here

5. **Run the App:**
   streamlit run app.py

## 🌐 Live Demo
The application is currently live and deployed via Streamlit Community Cloud. 
**[Try WebMind AI Here](https://webmind-ai-lybsngfxqia8ayrp294mmn.streamlit.app)**

## 📝 License
This project is open-source and available for educational and personal use.