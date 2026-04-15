import os
import time
from google import genai
from google.genai import errors 
from dotenv import load_dotenv
from src.vector_db import VectorDB
import streamlit as st

# ==========================================
# 🔐 SECURE API KEY LOADER
# ==========================================
load_dotenv() # Tries to load from local .env first

# 1. Check local environment first
api_key = os.getenv("GEMINI_API_KEY")

# 2. If not found locally, try Streamlit Secrets (for the Cloud)
if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

# 3. Final failsafe check
if not api_key:
    print("❌ ERROR: GEMINI_API_KEY not found in .env or Streamlit Secrets.")
    # We don't exit here so the UI can still load and show an error
    api_key = "MISSING_KEY" 

class WebMindEngine:
    def __init__(self, db_instance):
        self.db = db_instance
        self.client = genai.Client(api_key=api_key)
        
        # Using the high-availability model for fast RAG processing
        self.model_id = 'gemini-3-flash-preview'
        print(f"📡 WebMind Engine initialized with model: {self.model_id}")

    def ask(self, user_query, max_retries=3, delay=2):
        """
        Retrieves context from the Vector DB and generates a grounded response.
        """
        if api_key == "MISSING_KEY":
            return "❌ System Error: API Key is missing. Please configure your .env file or Streamlit Secrets."

        # STEP 1: RETRIEVAL
        try:
            # Fetching top 5 results to ensure a broader context for the LLM
            search_results = self.db.query(user_query, limit=5)
            
            context = "\n".join([hit.payload['text'] for hit in search_results])
            sources = list(set([hit.payload['source'] for hit in search_results]))
            
        except Exception as e:
            return f"❌ Database Retrieval Error: {str(e)}"

        # STEP 2: UNIVERSAL GROUNDED PROMPTING
        system_prompt = (
            f"You are WebMind AI, a professional knowledge assistant. "
            f"Your goal is to answer the user's question accurately using ONLY the provided context. "
            f"If the information is not available in the context, politely explain that the "
            f"indexed website does not contain that specific information.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {user_query}"
        )

        # STEP 3: GENERATION WITH AUTO-RETRY
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=system_prompt
                )
                
                answer = response.text
                
                # Append clickable sources if available
                if sources:
                    source_links = "\n".join([f"- {s}" for s in sources])
                    answer += f"\n\n**Verified Sources:**\n{source_links}"
                
                return answer

            except errors.ServerError:
                # Handles 503 errors during traffic spikes
                if attempt < max_retries - 1:
                    print(f"🕒 WebMind: Server busy. Retrying in {delay}s...")
                    time.sleep(delay)
                    continue
                else:
                    return "🕒 The AI servers are currently under high load. Please try again in a few seconds."
            
            except errors.ClientError as e:
                # Handles 429 (Rate Limit) or 404 (Model ID)
                if "429" in str(e):
                    return "🚀 Rate limit reached! Please slow down and wait a moment."
                return f"❌ Client Error: {e}"

            except Exception as e:
                return f"❌ Unexpected Error: {str(e)}"

if __name__ == "__main__":
    db = VectorDB()
    test_data = [
        {"text": "WebMind AI is a universal RAG assistant built in 2026.", "url": "https://webmind.ai/about"},
        {"text": "It uses Gemini 3 Flash and Qdrant for lightning-fast retrieval.", "url": "https://webmind.ai/tech"}
    ]
    for item in test_data:
        db.add_to_index([item["text"]], item["url"])
    
    bot = WebMindEngine(db)
    print("\n--- ✅ WebMind Engine Ready ---")
    print(bot.ask("What technology does WebMind AI use?"))