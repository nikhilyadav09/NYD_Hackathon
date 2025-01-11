import streamlit as st
import sys
import os
from pathlib import Path
import asyncio
import logging
logging.basicConfig(level=logging.INFO)

# Add the parent directory (src) to the Python path
src_path = str(Path(__file__).parent.parent)
sys.path.append(src_path)

from main_pipeline import EnhancedRAGPipeline

# Page config
st.set_page_config(
    page_title="Ancient Wisdom Explorer 🕉️",
    page_icon="🕉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .answer-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
    .verse-details {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border: 1px solid #e1e4e8;
    }
    .detail-row {
        margin: 0.8rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #eaecef;
    }
    .detail-label {
        font-weight: bold;
        color: #1f77b4;
    }
    .sanskrit {
        font-style: italic;
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'rag_pipeline' not in st.session_state:
    st.session_state.rag_pipeline = EnhancedRAGPipeline()

def display_header():
    st.title("🕉️ Ancient Wisdom Explorer")
    st.markdown("Discover insights from the Bhagavad Gita and Yoga Sutras")
    st.divider()

def display_verse_details(verse_data):
    st.markdown(f"""
    <div class='verse-details'>
        <div class='detail-row'>
            <span class='detail-label'>Book:</span> {verse_data['book']}
        </div>
        <div class='detail-row'>
            <span class='detail-label'>Chapter:</span> {verse_data['chapter']} | 
            <span class='detail-label'>Verse:</span> {verse_data['verse']}
        </div>
        <div class='detail-row'>
            <span class='detail-label'>Sanskrit:</span>
            <div class='sanskrit'>{verse_data['sanskrit']}</div>
        </div>
        <div class='detail-row'>
            <span class='detail-label'>Translation:</span>
            <div>{verse_data['translation']}</div>
        </div>
        <div class='detail-row'>
            <span class='detail-label'>Explanation:</span>
            <div>{verse_data['explanation']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_wisdom_response(response_data):
    # Display AI-generated answer first
    st.markdown(f"""
    <div class='answer-box'>
        {response_data["response"]["summary"]}
    </div>
    """, unsafe_allow_html=True)
    
    # Add collapsible section for verse details
    with st.expander("📚 View Source Verse Details", expanded=False):
        display_verse_details(response_data["verse"])

def display_chat_message(role, content):
    with st.chat_message(role):
        if isinstance(content, str):
            st.markdown(content)
        elif isinstance(content, dict):
            if content.get("type") == "greeting":
                st.markdown(content["response"]["summary"])
            elif content.get("type") == "wisdom_response":
                display_wisdom_response(content)

def display_sidebar():
    with st.sidebar:
        st.markdown("### 🎯 About")
        st.markdown("""
        Ask questions and receive wisdom from:
        - Bhagavad Gita
        - Yoga Sutras
        """)
        
        st.markdown("### 💡 Example Questions")
        st.markdown("""
        - What is the nature of the mind?
        - How to find inner peace?
        - What is true happiness?
        """)
        
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

def main():
    display_header()
    display_sidebar()
    
    # Display chat history
    for message in st.session_state.messages:
        display_chat_message(message["role"], message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about ancient wisdom..."):
        # Display user message
        display_chat_message("user", prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get response from RAG pipeline
        with st.spinner("🤔 Consulting the ancient texts..."):
            try:
                # Run async code in sync context
                response = asyncio.run(st.session_state.rag_pipeline.process_query(prompt))
                
                if "error" in response:
                    error_message = f"❌ Error: {response['error']}"
                    display_chat_message("assistant", error_message)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_message
                    })
                else:
                    # Display response
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

if __name__ == "__main__":
    main()
