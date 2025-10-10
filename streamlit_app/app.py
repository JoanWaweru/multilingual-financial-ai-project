"""
Streamlit Web Interface for Kenyan Financial Chatbot
"""

import streamlit as st
import sys
from pathlib import Path
import plotly.graph_objects as go

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from chatbot.chatbot import KenyanFinancialChatbot

# Page configuration
st.set_page_config(
    page_title="Kenyan Financial Advisor 🇰🇪",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 20%;
    }
    .bot-message {
        background-color: #f5f5f5;
        margin-right: 20%;
    }
    .message-content {
        margin: 0.5rem 0;
    }
    .message-meta {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.5rem;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize chatbot
@st.cache_resource
def load_chatbot():
    """Load chatbot (cached for performance)"""
    return KenyanFinancialChatbot()

# Initialize session state
if 'chatbot' not in st.session_state:
    with st.spinner("Loading Kenyan Financial Advisor... 🤖"):
        st.session_state.chatbot = load_chatbot()
        st.session_state.messages = []
        st.session_state.language_stats = {
            'english': 0,
            'swahili': 0,
            'code_switched': 0
        }

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/49/Flag_of_Kenya.svg", 
             width=100)
    st.title("🇰🇪 Kenyan Financial Advisor")
    
    st.markdown("---")
    
    st.subheader("📊 Your Language Usage")
    
    # Language distribution chart
    if sum(st.session_state.language_stats.values()) > 0:
        fig = go.Figure(data=[go.Pie(
            labels=['English', 'Swahili', 'Code-Switched'],
            values=[
                st.session_state.language_stats['english'],
                st.session_state.language_stats['swahili'],
                st.session_state.language_stats['code_switched']
            ],
            marker=dict(colors=['#2196F3', '#4CAF50', '#FF9800'])
        )])
        fig.update_layout(
            height=250,
            margin=dict(l=20, r=20, t=30, b=20),
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Start chatting to see your language pattern!")
    
    st.markdown("---")
    
    st.subheader("💡 Tips")
    st.markdown("""
    - Mix **English** and **Swahili** freely!
    - Ask about:
        - 💰 Savings (akiba)
        - 📱 M-Pesa
        - 🏦 Banks
        - 👥 Chamas & SACCOs
        - 💵 Loans (mikopo)
    """)
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.session_state.chatbot.clear_history()
        st.session_state.language_stats = {
            'english': 0,
            'swahili': 0,
            'code_switched': 0
        }
        st.rerun()
    
    st.markdown("---")
    st.caption("Built for MSc Thesis - Joan Waweru")

# Main content
st.markdown('<h1 class="main-header">💬 Kenyan Financial Advisor Chatbot</h1>', 
            unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center; margin-bottom: 2rem;'>
    <p style='font-size: 1.1rem;'>
        Ask me anything about <b>savings</b>, <b>M-Pesa</b>, <b>chamas</b>, 
        <b>loans</b>, and more! 🇰🇪
    </p>
    <p style='color: #666;'>
        You can speak in English, Swahili, or mix them (code-switching)!
    </p>
</div>
""", unsafe_allow_html=True)

# Display welcome message if no chat history
if len(st.session_state.messages) == 0:
    welcome_msg = st.session_state.chatbot.get_welcome_message()
    st.info(welcome_msg)
    
    # Example questions
    st.subheader("💡 Try asking:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💰 How do I save money?"):
            st.session_state.example_query = "How do I save money?"
    
    with col2:
        if st.button("📱 What is M-Pesa?"):
            st.session_state.example_query = "What is M-Pesa?"
    
    with col3:
        if st.button("👥 What is a chama?"):
            st.session_state.example_query = "What is a chama?"

# Display chat messages
for message in st.session_state.messages:
    if message['role'] == 'user':
        st.markdown(f"""
        <div class='chat-message user-message'>
            <div style='font-weight: bold;'>👤 You</div>
            <div class='message-content'>{message['content']}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='chat-message bot-message'>
            <div style='font-weight: bold;'>🤖 Financial Advisor</div>
            <div class='message-content'>{message['content']}</div>
            <div class='message-meta'>
                🌐 Language: {message.get('language', 'N/A')} | 
                🎯 Confidence: {message.get('confidence', 0)*100:.1f}% |
                📊 Swahili: {message.get('swahili_ratio', 0)*100:.0f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

# Chat input
user_input = st.chat_input("Type your question here... (e.g., 'Ninataka kuweka pesa')")

# Handle example query
if 'example_query' in st.session_state:
    user_input = st.session_state.example_query
    del st.session_state.example_query

# Process user input
if user_input:
    # Add user message to chat
    st.session_state.messages.append({
        'role': 'user',
        'content': user_input
    })
    
    # Get bot response
    with st.spinner("Thinking... 🤔"):
        response = st.session_state.chatbot.chat(user_input)
    
    # Update language stats
    detected_lang = response['detected_language']
    st.session_state.language_stats[detected_lang] += 1
    
    # Add bot message to chat
    st.session_state.messages.append({
        'role': 'assistant',
        'content': response['response'],
        'language': detected_lang,
        'confidence': response['confidence'],
        'swahili_ratio': response['swahili_ratio']
    })
    
    # Rerun to display new messages
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><b>Kenyan Financial Advisor Chatbot</b></p>
    <p>Adaptive Code-Switching • Multilingual Financial Education • Built with ❤️ in Kenya 🇰🇪</p>
    <p style='font-size: 0.9rem;'>MSc Thesis Project - Joan Waweru</p>
</div>
""", unsafe_allow_html=True)