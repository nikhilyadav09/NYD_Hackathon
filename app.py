# src/app.py
import streamlit as st
import sys
from pathlib import Path
import asyncio
import logging
import time
from typing import Dict, List
import json

# Configure logging
logging.basicConfig(level=logging.INFO)

# Add the parent directory to Python path
src_path = str(Path(__file__).parent.parent)
sys.path.append(src_path)

from src.core.pipeline import VedicWisdomPipeline

# Page configuration
st.set_page_config(
    page_title="DHARMA - Divine Healing And Reflective Mindfulness Assistant",
    page_icon="🕉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with improved styling
st.markdown("""
<style>
    /* Main container styling */
    .main-container {
        max-width: 1200px;
        margin: auto;
    }
    
    /* Enhanced answer box */
    .answer-box {
        background-color: #f5f0e6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #FF9933;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Verse details styling */
    .verse-details {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border: 1px solid #e1e4e8;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Detail row styling */
    .detail-row {
        margin: 0.8rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #eaecef;
    }
    
    /* Labels styling */
    .detail-label {
        font-weight: bold;
        color: #FF9933;
        font-size: 0.9rem;
    }
    
    /* Sanskrit text styling */
    .sanskrit {
        font-style: italic;
        color: #1E1E1E;
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 0.3rem;
        font-family: 'Sanskrit Text', serif;
    }
    
    /* Source citation styling */
    .source-citation {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    /* Confidence score styling */
    .confidence-score {
        font-size: 0.8rem;
        color: #28a745;
        margin-top: 0.5rem;
    }

    /* Header styling */
    .dharma-header {
        background: linear-gradient(135deg, #FF9933 0%, #FF8C00 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        margin-bottom: 2rem;
    }

    .dharma-subtitle {
        color: #ffffff;
        font-size: 1.2rem;
        margin-top: 0.5rem;
        font-weight: 300;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
def init_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'pipeline' not in st.session_state:
        st.session_state.pipeline = VedicWisdomPipeline()
    if 'feedback' not in st.session_state:
        st.session_state.feedback = {}

def display_header():
    """Display application header with improved styling"""
    st.markdown("""
    <div class='dharma-header'>
        <h1>🕉️ DHARMA</h1>
        <div class='dharma-subtitle'>
            Divine Healing And Reflective Mindfulness Assistant
        </div>
        <p style='margin-top: 1rem; font-size: 1rem;'>
            Explore the timeless wisdom of Bhagavad Gita and Yoga Sutras through divine guidance
        </p>
    </div>
    """, unsafe_allow_html=True)

def format_source_citation(source: str) -> str:
    """Format a single source citation cleanly"""
    source = source.strip()
    parts = source.split()
    if len(parts) >= 2:
        book = ' '.join(parts[:-1])
        reference = parts[-1]
        return f"{book} {reference}"
    return source

def display_wisdom_response(response_data: Dict):
    """Display wisdom response with improved formatting and source handling"""
    sources = response_data["response"].get("sources", [])
    formatted_sources = []
    seen_sources = set()
    
    for source in sources:
        formatted = format_source_citation(source)
        if formatted not in seen_sources:
            formatted_sources.append(formatted)
            seen_sources.add(formatted)
    
    source_citation = ', '.join(formatted_sources)
    
    st.markdown(f"""
    <div class='answer-box'>
        {response_data["response"]["summary"]}
        <div class='source-citation'>
            Sources: {source_citation}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if response_data.get("verse"):
        with st.expander("📚 View Source Verse Details", expanded=False):
            display_verse_details(response_data["verse"])

def display_verse_details(verse_data: Dict):
    """Display verse details with enhanced styling and validation"""
    if not verse_data:
        st.warning("Source verse details not available")
        return
        
    confidence_score = verse_data.get('confidence_score')
    confidence_html = (
        f"<div class='confidence-score'>Relevance Score: {confidence_score:.2%}</div>"
        if confidence_score is not None and isinstance(confidence_score, (int, float))
        else ""
    )
    
    verse_location = (
        f"Chapter {verse_data.get('chapter', '?')}, "
        f"Verse {verse_data.get('verse', '?')}"
    )
    
    st.markdown(f"""
    <div class='verse-details'>
        <div class='detail-row'>
            <span class='detail-label'>Source:</span> {verse_data.get('book', 'Unknown')}
        </div>
        <div class='detail-row'>
            <span class='detail-label'>Location:</span> {verse_location}
        </div>
        <div class='detail-row'>
            <span class='detail-label'>Sanskrit:</span>
            <div class='sanskrit'>{verse_data.get('sanskrit', 'Not available')}</div>
        </div>
        <div class='detail-row'>
            <span class='detail-label'>Translation:</span>
            <div>{verse_data.get('translation', 'Not available')}</div>
        </div>
        <div class='detail-row'>
            <span class='detail-label'>Explanation:</span>
            <div>{verse_data.get('explanation', 'Not available')}</div>
        </div>
        {confidence_html}
    </div>
    """, unsafe_allow_html=True)

def display_chat_message(role: str, content: Dict):
    """Display chat messages with enhanced styling"""
    with st.chat_message(role):
        if isinstance(content, str):
            st.markdown(content)
        elif isinstance(content, dict):
            if content.get("type") == "wisdom_response":
                display_wisdom_response(content)
            elif content.get("type") == "clarification":
                st.warning(content["response"]["summary"])

def display_sidebar():
    with st.sidebar:
        st.markdown("### 🎯 About DHARMA")
        st.markdown("""
        Your spiritual guide to ancient wisdom from:
        - 📚 Bhagavad Gita
        - 🧘‍♂️ Patanjali Yoga Sutras
        """)
        
        st.markdown("### 💡 Sample Questions")
        st.markdown("""
        <div class="example-text">
            • What is the path to inner peace?
        </div>
        <div class="example-text">
            • How can I understand my true nature?
        </div>
        <div class="example-text">
            • What is the meaning of dharma?
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <p style='font-size: 0.8em; color: #666;'>
            (Click any question to explore)
        </p>
        """, unsafe_allow_html=True)
        
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

def process_query(prompt: str):
    """Process user query and update chat"""
    display_chat_message("user", prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.spinner("🕉️ Channeling divine wisdom..."):
        try:
            response = asyncio.run(st.session_state.pipeline.process_query(prompt))
            
            if "error" in response:
                error_message = f"❌ Error: {response['error']}"
                display_chat_message("assistant", error_message)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message
                })
            else:
                display_chat_message("assistant", response)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
        
        except Exception as e:
            error_message = f"❌ An error occurred: {str(e)}"
            display_chat_message("assistant", error_message)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_message
            })

def main():
    """Main application function"""
    init_session_state()
    display_header()
    display_sidebar()
    
    # Display chat history
    for message in st.session_state.messages:
        display_chat_message(message["role"], message["content"])
    
    # Chat input
    if prompt := st.chat_input("Seek divine guidance..."):
        process_query(prompt)

if __name__ == "__main__":
    main()