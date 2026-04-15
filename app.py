import streamlit as st
import os
from src.scraper import WebMindScraper
from src.chunker import TextChunker
from src.vector_db import VectorDB
from src.engine import WebMindEngine
from src.utils import is_valid_url # Importing our new safety checker

# Page Configuration
st.set_page_config(
    page_title="WebMind AI", 
    page_icon="🧠", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    .stButton>button { width: 100%; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧠 WebMind AI")
st.caption("Universal Web RAG | Transform any URL into an Interactive Knowledge Base")

# 1. Initialize Backend (Cached to prevent 60s timeout on Streamlit Cloud)
@st.cache_resource(show_spinner="Loading AI Models (This takes a minute on the first run)...")
def load_backend():
    # Initializing these inside the cache so the heavy models load once
    return VectorDB(), TextChunker(), WebMindScraper()

db, chunker, scraper = load_backend()

# Initialize Session State with the loaded resources
if 'db' not in st.session_state:
    st.session_state.db = db
    st.session_state.chunker = chunker
    st.session_state.scraper = scraper
    st.session_state.engine = None
    st.session_state.messages = []
    st.session_state.indexed_urls = []

# 2. Sidebar: Knowledge Management
with st.sidebar:
    st.header("⚙️ Knowledge Base Settings")
    
    # Universal Input
    st.subheader("Data Sources")
    manual_urls_input = st.text_area("Paste URLs to index (one per line):", 
                                     height=150, 
                                     placeholder="https://en.wikipedia.org/wiki/Artificial_intelligence")
    
    # Extract URLs
    final_urls = [u.strip() for u in manual_urls_input.split('\n') if u.strip()]

    # Action Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Build Base"):
            if not final_urls:
                st.error("Add at least one URL!")
            else:
                total_chunks = 0
                progress_bar = st.progress(0)
                status = st.empty()
                
                for i, url in enumerate(final_urls):
                    # SAFETY CHECK: Use utils.py to validate the URL format
                    if not is_valid_url(url):
                        st.warning(f"⚠️ Skipped invalid URL: {url}")
                        continue

                    # Display a shortened version of the URL to keep the UI clean
                    display_name = url.split('/')[-2] if len(url.split('/')) > 3 else url[:30]
                    status.text(f"Scraping: {display_name}...")
                    
                    html = st.session_state.scraper.fetch_page(url)
                    if html:
                        content = st.session_state.scraper.clean_content(html)
                        chunks = st.session_state.chunker.split_text(content)
                        st.session_state.db.add_to_index(chunks, url)
                        total_chunks += len(chunks)
                        
                        if url not in st.session_state.indexed_urls:
                            st.session_state.indexed_urls.append(url)
                            
                    progress_bar.progress((i + 1) / len(final_urls))
                
                # Update/Re-init Engine if we actually indexed data
                if total_chunks > 0:
                    st.session_state.engine = WebMindEngine(st.session_state.db)
                    status.text("✅ Knowledge Base Ready!")
                    st.success(f"Indexed {total_chunks} chunks from {len(st.session_state.indexed_urls)} sources.")
                else:
                    status.text("❌ No text could be extracted.")
    
    with col2:
        if st.button("🗑️ Reset DB"):
            st.session_state.db = VectorDB() # Re-init DB
            st.session_state.indexed_urls = []
            st.session_state.engine = None
            st.rerun()

    # Show what is currently in the "Brain"
    if st.session_state.indexed_urls:
        st.divider()
        st.subheader("📂 Currently Indexed")
        for url in st.session_state.indexed_urls:
            st.caption(f"🔗 {url}")

# 3. Chat Interface
# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask WebMind anything about the indexed sites..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    if st.session_state.engine:
        with st.chat_message("assistant"):
            with st.spinner("Synthesizing from multiple sources..."):
                response = st.session_state.engine.ask(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        st.warning("⚠️ Please build the Knowledge Base in the sidebar to start.")

# Floating Clear Chat Button
if st.session_state.messages:
    if st.button("🧹 Clear Chat Conversation"):
        st.session_state.messages = []
        st.rerun()