import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import sys
import json
import numpy as np
from datetime import datetime
import time

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from chatbot.chatbot_engine import MultilingualFinancialChatbot
from config.settings import PROCESSED_DATA_DIR, MODELS_DIR

# Page configuration
st.set_page_config(
    page_title="Multilingual Financial AI",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourproject',
        'Report a bug': "https://github.com/yourproject/issues",
        'About': "Multilingual Financial AI System for East Africa"
    }
)

# Custom CSS for styling
st.markdown("""
    <style>
    /* Main styling */
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1f77b4 0%, #2ca02c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        padding: 1rem;
    }
    
    .sub-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        animation: fadeIn 0.5s;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20%;
    }
    
    .bot-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        margin-right: 20%;
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 0.5rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .info-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
    
    .success-box {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4caf50;
        margin: 1rem 0;
    }
    
    .warning-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff9800;
        margin: 1rem 0;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None
    st.session_state.chatbot_loading = False

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.df = None

if 'show_stats' not in st.session_state:
    st.session_state.show_stats = False

# Helper functions
@st.cache_data
def load_data():
    """Load and cache the analyzed data"""
    try:
        data_path = PROCESSED_DATA_DIR / "tweets_analyzed.csv"
        if data_path.exists():
            df = pd.read_csv(data_path)
            return df, None
        else:
            return None, "Data file not found. Please run data collection and preprocessing first."
    except Exception as e:
        return None, f"Error loading data: {str(e)}"

@st.cache_data
def load_evaluation_metrics():
    """Load evaluation metrics if available"""
    try:
        metrics_path = MODELS_DIR / "evaluation" / "metrics.json"
        if metrics_path.exists():
            with open(metrics_path, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        return None

def initialize_chatbot():
    """Initialize chatbot with loading animation"""
    if st.session_state.chatbot is None and not st.session_state.chatbot_loading:
        st.session_state.chatbot_loading = True
        with st.spinner("🤖 Initializing AI Chatbot... This may take a moment."):
            try:
                st.session_state.chatbot = MultilingualFinancialChatbot()
                st.success("✅ Chatbot initialized successfully!")
                time.sleep(1)
            except Exception as e:
                st.error(f"❌ Error initializing chatbot: {str(e)}")
                st.session_state.chatbot = None
            finally:
                st.session_state.chatbot_loading = False

# Sidebar
with st.sidebar:
    st.markdown("## 📊 Navigation")
    
    page = st.radio(
        "Choose a page:",
        ["🤖 Chatbot", "📈 Data Analysis", "🔍 Model Performance", "📚 Documentation", "ℹ️ About"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Page-specific sidebar content
    if page == "🤖 Chatbot":
        st.markdown("### ⚙️ Chatbot Settings")
        
        if st.button("🔄 Reset Conversation", use_container_width=True):
            if st.session_state.chatbot:
                st.session_state.chatbot.reset_conversation()
                st.session_state.messages = []
                st.success("✅ Conversation reset!")
                time.sleep(1)
                st.rerun()
        
        if st.button("📊 Toggle Stats", use_container_width=True):
            st.session_state.show_stats = not st.session_state.show_stats
            st.rerun()
        
        if st.session_state.show_stats and st.session_state.chatbot:
            st.markdown("#### 📈 Statistics")
            stats = st.session_state.chatbot.get_conversation_stats()
            st.metric("Messages", stats['total_messages'])
            st.metric("Topics", len(stats['topics_discussed']))
            st.write(f"**Level:** {stats['experience_level']}")
            st.write(f"**Language:** {stats['language_preference']}")
    
    elif page == "📈 Data Analysis":
        st.markdown("### 🎛️ Analysis Filters")
        
        if st.session_state.data_loaded and st.session_state.df is not None:
            df = st.session_state.df
            
            # Country filter
            countries = ['All'] + list(df['country'].unique())
            selected_country = st.selectbox("Country", countries)
            
            # Code-switching filter
            cs_filter = st.radio("Code-Switching", ["All", "Yes", "No"])
            
            st.markdown("---")
            st.markdown(f"**Filtered Data:** {len(df)} tweets")
    
    st.markdown("---")
    st.markdown("### 🔗 Quick Links")
    st.markdown("- [GitHub Repository](#)")
    st.markdown("- [Research Paper](#)")
    st.markdown("- [Documentation](#)")
    st.markdown("- [Report Issues](#)")
    
    st.markdown("---")
    st.markdown("**Version:** 1.0.0")
    st.markdown("**Updated:** Sep 2025")
    st.markdown("**Status:** 🟢 Active")

# Main content based on selected page
if page == "🤖 Chatbot":
    st.markdown('<div class="main-header">💬 Multilingual Financial Chatbot</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <strong>🌍 Welcome!</strong> Ask me anything about savings, investments, budgeting, or M-Pesa in 
    <strong>English</strong>, <strong>Swahili</strong>, or <strong>mix them</strong>!
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize chatbot
    initialize_chatbot()
    
    if st.session_state.chatbot is None:
        st.error("❌ Chatbot not available. Please check the error message above.")
        st.stop()
    
    # Example questions in expandable section
    with st.expander("💡 Example Questions & Topics", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**💰 Savings (Akiba)**")
            st.markdown("- How can I save money?")
            st.markdown("- Nisaidie na akiba")
            st.markdown("- Tell me about chamas")
            st.markdown("- Emergency fund tips")
        
        with col2:
            st.markdown("**📈 Investment (Uwekezaji)**")
            st.markdown("- Where should I invest?")
            st.markdown("- Nataka kuwekeza pesa")
            st.markdown("- Explain stock market")
            st.markdown("- Government bonds info")
        
        with col3:
            st.markdown("**📊 Budgeting (Bajeti)**")
            st.markdown("- How do I budget?")
            st.markdown("- Nisaidie na bajeti")
            st.markdown("- 50/30/20 rule")
            st.markdown("- Track expenses")
    
    st.markdown("---")
    
    # Chat display area
    chat_container = st.container()
    
    with chat_container:
        if len(st.session_state.messages) == 0:
            st.markdown("""
            <div class="success-box">
            👋 <strong>Habari! Hello!</strong> I'm your multilingual financial assistant. 
            I can help you with savings, investments, budgeting, loans, M-Pesa, business, and more!
            </div>
            """, unsafe_allow_html=True)
        else:
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(
                        f'<div class="chat-message user-message">👤 <strong>You:</strong><br>{message["content"]}</div>', 
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div class="chat-message bot-message">🤖 <strong>Bot:</strong><br>{message["content"]}</div>', 
                        unsafe_allow_html=True
                    )
    
    # Chat input
    st.markdown("---")
    user_input = st.chat_input("💬 Type your message here... (e.g., 'How can I save pesa?')")
    
    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Get bot response
        with st.spinner("🤔 Thinking..."):
            try:
                response = st.session_state.chatbot.chat(user_input)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        st.rerun()
    
    # Quick action buttons
    st.markdown("---")
    st.markdown("### 🎯 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💰 Savings Tips", use_container_width=True):
            user_input = "Give me savings tips"
            st.session_state.messages.append({"role": "user", "content": user_input})
            response = st.session_state.chatbot.chat(user_input)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col2:
        if st.button("📈 Investment Advice", use_container_width=True):
            user_input = "Tell me about investment"
            st.session_state.messages.append({"role": "user", "content": user_input})
            response = st.session_state.chatbot.chat(user_input)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col3:
        if st.button("📊 Budget Help", use_container_width=True):
            user_input = "Help me with budgeting"
            st.session_state.messages.append({"role": "user", "content": user_input})
            response = st.session_state.chatbot.chat(user_input)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col4:
        if st.button("🤝 Explain Chama", use_container_width=True):
            user_input = "What is a chama?"
            st.session_state.messages.append({"role": "user", "content": user_input})
            response = st.session_state.chatbot.chat(user_input)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

elif page == "📈 Data Analysis":
    st.markdown('<div class="main-header">📊 Data Analysis Dashboard</div>', unsafe_allow_html=True)
    
    # Load data
    if not st.session_state.data_loaded:
        with st.spinner("Loading data..."):
            df, error = load_data()
            if df is not None:
                st.session_state.df = df
                st.session_state.data_loaded = True
            else:
                st.error(error)
                st.info("""
                **To generate data:**
```bash
                python main.py --step collect
                python main.py --step preprocess
                """)
            st.stop()

df = st.session_state.df

# Overview metrics
st.markdown("## 📋 Dataset Overview")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Tweets", f"{len(df):,}", help="Total number of tweets collected")

with col2:
    code_switched = df['has_code_switching'].sum()
    cs_percentage = (code_switched/len(df)*100)
    st.metric("Code-Switched", f"{code_switched:,}", 
             delta=f"{cs_percentage:.1f}%", help="Tweets with code-switching")

with col3:
    if 'likes' in df.columns:
        avg_engagement = (df['likes'].mean() + df['retweets'].mean())
        st.metric("Avg Engagement", f"{avg_engagement:.1f}", help="Average likes + retweets")
    else:
        st.metric("Avg Engagement", "N/A")

with col4:
    countries = df['country'].nunique()
    st.metric("Countries", countries, help="Number of countries covered")

with col5:
    if 'word_count' in df.columns:
        avg_length = df['word_count'].mean()
        st.metric("Avg Length", f"{avg_length:.1f}", help="Average words per tweet")
    else:
        st.metric("Avg Length", "N/A")

st.markdown("---")

# Tabs for different analyses
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌍 Geographic", 
    "🔀 Code-Switching", 
    "📊 Engagement", 
    "📝 Text Analysis",
    "🔍 Deep Dive"
])

with tab1:
    st.markdown('<div class="sub-header">🌍 Geographic Distribution</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Country distribution bar chart
        country_counts = df['country'].value_counts()
        fig = px.bar(
            x=country_counts.index,
            y=country_counts.values,
            labels={'x': 'Country', 'y': 'Number of Tweets'},
            title='Tweet Distribution by Country',
            color=country_counts.values,
            color_continuous_scale='viridis',
            text=country_counts.values
        )
        fig.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Country pie chart
        fig = px.pie(
            values=country_counts.values,
            names=country_counts.index,
            title='Country Distribution (%)',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Code-switching rate by country
    st.markdown("### 🔀 Code-Switching Rate by Country")
    
    cs_by_country = df.groupby('country')['has_code_switching'].agg(['sum', 'count'])
    cs_by_country['rate'] = (cs_by_country['sum'] / cs_by_country['count'] * 100)
    cs_by_country = cs_by_country.sort_values('rate', ascending=False)
    
    fig = px.bar(
        x=cs_by_country.index,
        y=cs_by_country['rate'],
        labels={'x': 'Country', 'y': 'Code-Switching Rate (%)'},
        title='Code-Switching Rate by Country',
        color=cs_by_country['rate'],
        color_continuous_scale='RdYlGn',
        text=cs_by_country['rate'].round(1)
    )
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    fig.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.markdown("### 📊 Country Statistics")
    country_stats = df.groupby('country').agg({
        'has_code_switching': ['sum', 'count'],
        'word_count': 'mean'
    }).round(2)
    country_stats.columns = ['Code-Switched', 'Total', 'Avg Words']
    country_stats['CS Rate %'] = (country_stats['Code-Switched'] / country_stats['Total'] * 100).round(1)
    st.dataframe(country_stats, use_container_width=True)

with tab2:
    st.markdown('<div class="sub-header">🔀 Code-Switching Patterns</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Code-switching prevalence
        cs_counts = df['has_code_switching'].value_counts()
        fig = px.pie(
            values=cs_counts.values,
            names=['No Code-Switching', 'Code-Switching'],
            title='Code-Switching Prevalence',
            color_discrete_sequence=['#3498db', '#e74c3c'],
            hole=0.3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label+value')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Switching type distribution
        if 'switching_type' in df.columns:
            switching_types = df['switching_type'].value_counts()
            fig = px.pie(
                values=switching_types.values,
                names=switching_types.index,
                title='Distribution of Switching Types',
                hole=0.3,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Switching type data not available")
    
    # Language balance
    st.markdown("### 🌐 Language Balance in Code-Switched Tweets")
    
    if 'english_ratio' in df.columns and 'swahili_ratio' in df.columns:
        cs_tweets = df[df['has_code_switching'] == True]
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=cs_tweets['english_ratio'],
            name='English Ratio',
            opacity=0.7,
            marker_color='#3498db',
            nbinsx=20
        ))
        fig.add_trace(go.Histogram(
            x=cs_tweets['swahili_ratio'],
            name='Swahili Ratio',
            opacity=0.7,
            marker_color='#e74c3c',
            nbinsx=20
        ))
        fig.update_layout(
            title='Language Ratio Distribution',
            xaxis_title='Ratio',
            yaxis_title='Frequency',
            barmode='overlay',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Avg English Ratio", f"{cs_tweets['english_ratio'].mean():.2f}")
        with col2:
            st.metric("Avg Swahili Ratio", f"{cs_tweets['swahili_ratio'].mean():.2f}")
        with col3:
            balanced = cs_tweets[
                (cs_tweets['english_ratio'] > 0.3) & 
                (cs_tweets['english_ratio'] < 0.7)
            ]
            st.metric("Balanced Mix", f"{len(balanced)/len(cs_tweets)*100:.1f}%")

with tab3:
    st.markdown('<div class="sub-header">📊 Engagement Analysis</div>', unsafe_allow_html=True)
    
    if all(col in df.columns for col in ['likes', 'retweets', 'replies']):
        # Calculate total engagement
        df['total_engagement'] = df['likes'] + df['retweets'] + df['replies'] + df.get('quotes', 0)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Engagement comparison
            engagement_comparison = df.groupby('has_code_switching')['total_engagement'].mean()
            
            fig = go.Figure(data=[
                go.Bar(
                    x=['No Code-Switching', 'Code-Switching'],
                    y=[engagement_comparison[False], engagement_comparison[True]],
                    marker_color=['#3498db', '#e74c3c'],
                    text=[f'{engagement_comparison[False]:.1f}', f'{engagement_comparison[True]:.1f}'],
                    textposition='auto',
                    marker=dict(
                        line=dict(color='#000000', width=2)
                    )
                )
            ])
            fig.update_layout(
                title='Average Engagement Comparison',
                yaxis_title='Average Total Engagement',
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate improvement
            improvement = ((engagement_comparison[True] - engagement_comparison[False]) / 
                          engagement_comparison[False] * 100)
            
            if improvement > 0:
                st.markdown(f"""
                <div class="success-box">
                ✅ <strong>Code-switched tweets show {improvement:.1f}% higher engagement!</strong>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="info-box">
                Code-switched tweets show {improvement:.1f}% engagement difference
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Engagement by switching type
            if 'switching_type' in df.columns:
                engagement_by_type = df.groupby('switching_type')['total_engagement'].mean().sort_values(ascending=False)
                
                fig = px.bar(
                    x=engagement_by_type.values,
                    y=engagement_by_type.index,
                    orientation='h',
                    title='Average Engagement by Switching Type',
                    labels={'x': 'Average Engagement', 'y': 'Switching Type'},
                    color=engagement_by_type.values,
                    color_continuous_scale='viridis',
                    text=engagement_by_type.values.round(1)
                )
                fig.update_traces(texttemplate='%{text}', textposition='outside')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Engagement distribution box plot
        st.markdown("### 📦 Engagement Distribution")
        
        fig = go.Figure()
        fig.add_trace(go.Box(
            y=df[df['has_code_switching']==False]['total_engagement'],
            name='No Code-Switching',
            marker_color='#3498db',
            boxmean='sd'
        ))
        fig.add_trace(go.Box(
            y=df[df['has_code_switching']==True]['total_engagement'],
            name='Code-Switching',
            marker_color='#e74c3c',
            boxmean='sd'
        ))
        fig.update_layout(
            title='Engagement Distribution by Code-Switching Status',
            yaxis_title='Total Engagement',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Engagement breakdown
        st.markdown("### 📊 Engagement Breakdown")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_likes = df.groupby('has_code_switching')['likes'].mean()
            st.metric("Likes (No CS)", f"{avg_likes[False]:.1f}")
            st.metric("Likes (CS)", f"{avg_likes[True]:.1f}", 
                     delta=f"{(avg_likes[True]-avg_likes[False])/avg_likes[False]*100:.1f}%")
        
        with col2:
            avg_retweets = df.groupby('has_code_switching')['retweets'].mean()
            st.metric("Retweets (No CS)", f"{avg_retweets[False]:.1f}")
            st.metric("Retweets (CS)", f"{avg_retweets[True]:.1f}",
                     delta=f"{(avg_retweets[True]-avg_retweets[False])/avg_retweets[False]*100:.1f}%")
        
        with col3:
            avg_replies = df.groupby('has_code_switching')['replies'].mean()
            st.metric("Replies (No CS)", f"{avg_replies[False]:.1f}")
            st.metric("Replies (CS)", f"{avg_replies[True]:.1f}",
                     delta=f"{(avg_replies[True]-avg_replies[False])/avg_replies[False]*100:.1f}%")
        
        with col4:
            if 'quotes' in df.columns:
                avg_quotes = df.groupby('has_code_switching')['quotes'].mean()
                st.metric("Quotes (No CS)", f"{avg_quotes[False]:.1f}")
                st.metric("Quotes (CS)", f"{avg_quotes[True]:.1f}",
                         delta=f"{(avg_quotes[True]-avg_quotes[False])/avg_quotes[False]*100:.1f}%")
    
    else:
        st.warning("⚠️ Engagement data not available in the dataset")

with tab4:
    st.markdown('<div class="sub-header">📝 Text Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Word count distribution
        if 'word_count' in df.columns:
            fig = px.histogram(
                df, x='word_count',
nbins=50,
title='Word Count Distribution',
labels={'word_count': 'Number of Words', 'count': 'Frequency'},
color_discrete_sequence=['#3498db'],
marginal='box'
)
fig.update_layout(height=400, showlegend=False)
st.plotly_chart(fig, use_container_width=True)
# Word count statistics
st.markdown("**📊 Word Count Statistics:**")
col_a, col_b, col_c = st.columns(3)
with col_a:
                st.metric("Mean", f"{df['word_count'].mean():.1f}")
with col_b:
                st.metric("Median", f"{df['word_count'].median():.1f}")
with col_c:
                st.metric("Max", f"{df['word_count'].max():.0f}")
    
with col2:
        # Language detection
        if 'detected_language' in df.columns:
            lang_counts = df['detected_language'].value_counts().head(10)
            fig = px.bar(
                x=lang_counts.index,
                y=lang_counts.values,
                title='Detected Languages (Top 10)',
                labels={'x': 'Language Code', 'y': 'Count'},
                color=lang_counts.values,
                color_continuous_scale='blues',
                text=lang_counts.values
            )
            fig.update_traces(texttemplate='%{text:,}', textposition='outside')
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Word count by code-switching status
st.markdown("### 📏 Text Length by Code-Switching Status")
    
if 'word_count' in df.columns:
        fig = go.Figure()
        fig.add_trace(go.Violin(
            y=df[df['has_code_switching']==False]['word_count'],
            name='No Code-Switching',
            box_visible=True,
            meanline_visible=True,
            fillcolor='#3498db',
            opacity=0.6,
            x0='No CS'
        ))
        fig.add_trace(go.Violin(
            y=df[df['has_code_switching']==True]['word_count'],
            name='Code-Switching',
            box_visible=True,
            meanline_visible=True,
            fillcolor='#e74c3c',
            opacity=0.6,
            x0='CS'
        ))
        fig.update_layout(
            title='Word Count Distribution Comparison',
            yaxis_title='Word Count',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Sample tweets viewer
st.markdown("### 📄 Sample Tweets Explorer")
    
col1, col2 = st.columns([1, 3])
    
with col1:
        sample_type = st.selectbox(
            "Select sample type:",
            ["Code-Switched", "No Code-Switching", "Random", "High Engagement"]
        )
        
        num_samples = st.slider("Number of samples", 3, 10, 5)
    
with col2:
        if sample_type == "Code-Switched":
            sample_df = df[df['has_code_switching'] == True].sample(
                n=min(num_samples, len(df[df['has_code_switching'] == True]))
            )
        elif sample_type == "No Code-Switching":
            sample_df = df[df['has_code_switching'] == False].sample(
                n=min(num_samples, len(df[df['has_code_switching'] == False]))
            )
        elif sample_type == "High Engagement":
            if 'total_engagement' in df.columns:
                sample_df = df.nlargest(num_samples, 'total_engagement')
            else:
                sample_df = df.sample(n=min(num_samples, len(df)))
        else:
            sample_df = df.sample(n=min(num_samples, len(df)))
        
        for idx, row in sample_df.iterrows():
            with st.expander(f"📝 Tweet from {row['country']} - {'✅ CS' if row['has_code_switching'] else '❌ No CS'}"):
                st.markdown(f"**Text:** {row['cleaned_text']}")
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    if 'word_count' in row:
                        st.write(f"**Words:** {row['word_count']}")
                with col_b:
                    if 'switching_type' in row:
                        st.write(f"**Type:** {row['switching_type']}")
                with col_c:
                    if 'total_engagement' in df.columns:
                        engagement = row.get('likes', 0) + row.get('retweets', 0) + row.get('replies', 0)
                        st.write(f"**Engagement:** {engagement}")

with tab5:
        st.markdown('<div class="sub-header">🔍 Deep Dive Analysis</div>', unsafe_allow_html=True)
    
    # Correlation heatmap
if all(col in df.columns for col in ['word_count', 'english_ratio', 'swahili_ratio', 'switching_score']):
        st.markdown("### 🔥 Feature Correlation Heatmap")
        
        numeric_cols = ['word_count', 'english_ratio', 'swahili_ratio', 'switching_score']
        if 'total_engagement' in df.columns:
            numeric_cols.append('total_engagement')
        
        corr_matrix = df[numeric_cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))
        fig.update_layout(
            title='Feature Correlation Matrix',
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Advanced filters
st.markdown("### 🎯 Advanced Data Exploration")
    
col1, col2, col3 = st.columns(3)
    
with col1:
        country_filter = st.multiselect(
            "Filter by Country",
            options=df['country'].unique(),
            default=df['country'].unique()
        )
    
with col2:
        if 'switching_type' in df.columns:
            type_filter = st.multiselect(
                "Filter by Switching Type",
                options=df['switching_type'].unique(),
                default=df['switching_type'].unique()
            )
        else:
            type_filter = None
    
with col3:
        if 'word_count' in df.columns:
            word_range = st.slider(
                "Word Count Range",
                int(df['word_count'].min()),
                int(df['word_count'].max()),
                (int(df['word_count'].min()), int(df['word_count'].max()))
            )
        else:
            word_range = None
    
    # Apply filters
filtered_df = df[df['country'].isin(country_filter)]
if type_filter and 'switching_type' in df.columns:
        filtered_df = filtered_df[filtered_df['switching_type'].isin(type_filter)]
if word_range and 'word_count' in df.columns:
        filtered_df = filtered_df[
            (filtered_df['word_count'] >= word_range[0]) & 
            (filtered_df['word_count'] <= word_range[1])
        ]
    
st.info(f"📊 Filtered dataset: {len(filtered_df):,} tweets ({len(filtered_df)/len(df)*100:.1f}% of total)")
    
    # Scatter plot
if 'switching_score' in filtered_df.columns and 'total_engagement' in filtered_df.columns:
        st.markdown("### 📈 Switching Score vs Engagement")
        
        fig = px.scatter(
            filtered_df,
            x='switching_score',
            y='total_engagement',
            color='country',
            size='word_count' if 'word_count' in filtered_df.columns else None,
            hover_data=['cleaned_text'],
            title='Code-Switching Score vs Total Engagement',
            labels={
                'switching_score': 'Code-Switching Score',
                'total_engagement': 'Total Engagement'
            },
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
elif page == "🔍 Model Performance":
    st.markdown('<div class="main-header">🎯 Model Performance</div>', unsafe_allow_html=True)
# Load evaluation metrics
metrics = load_evaluation_metrics()

if metrics:
    st.markdown("""
    <div class="success-box">
    ✅ <strong>Evaluation Complete!</strong> Model metrics loaded successfully.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("## 📊 Classification Metrics")
    
    # Main metrics with colored cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        accuracy = metrics['accuracy'] * 100
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1.5rem; border-radius: 1rem; color: white; text-align: center;'>
            <h3 style='margin: 0; font-size: 2rem;'>{accuracy:.2f}%</h3>
            <p style='margin: 0.5rem 0 0 0;'>Accuracy</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        precision = metrics['precision'] * 100
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 1.5rem; border-radius: 1rem; color: white; text-align: center;'>
            <h3 style='margin: 0; font-size: 2rem;'>{precision:.2f}%</h3>
            <p style='margin: 0.5rem 0 0 0;'>Precision</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        recall = metrics['recall'] * 100
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 1.5rem; border-radius: 1rem; color: white; text-align: center;'>
            <h3 style='margin: 0; font-size: 2rem;'>{recall:.2f}%</h3>
            <p style='margin: 0.5rem 0 0 0;'>Recall</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        f1 = metrics['f1_score'] * 100
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); 
                    padding: 1.5rem; border-radius: 1rem; color: white; text-align: center;'>
            <h3 style='margin: 0; font-size: 2rem;'>{f1:.2f}%</h3>
            <p style='margin: 0.5rem 0 0 0;'>F1-Score</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Advanced metrics
    st.markdown("## 📈 Advanced Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("ROC-AUC", f"{metrics['roc_auc']:.4f}", help="Area Under ROC Curve")
    
    with col2:
        st.metric("PR-AUC", f"{metrics['pr_auc']:.4f}", help="Area Under Precision-Recall Curve")
    
    with col3:
        st.metric("Specificity", f"{metrics['specificity']*100:.2f}%", help="True Negative Rate")
    
    with col4:
        st.metric("Sensitivity", f"{metrics['sensitivity']*100:.2f}%", help="True Positive Rate (Recall)")
    
    st.markdown("---")
    
    # Confusion Matrix
    st.markdown("## 🔢 Confusion Matrix")
    
    cm = np.array(metrics['confusion_matrix'])
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = go.Figure(data=go.Heatmap(
            z=cm,
            x=['Predicted: No CS', 'Predicted: CS'],
            y=['Actual: No CS', 'Actual: CS'],
            colorscale='Blues',
            text=cm,
            texttemplate='<b>%{text}</b>',
            textfont={"size": 20},
            showscale=True,
            colorbar=dict(title="Count")
        ))
        
        fig.update_layout(
            title='Confusion Matrix',
            height=400,
            xaxis_title='Predicted Label',
            yaxis_title='True Label'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Matrix Breakdown")
        tn, fp, fn, tp = cm.ravel()
        
        st.metric("True Negatives (TN)", f"{tn:,}", help="Correctly identified no CS")
        st.metric("False Positives (FP)", f"{fp:,}", help="Incorrectly predicted CS")
        st.metric("False Negatives (FN)", f"{fn:,}", help="Missed CS")
        st.metric("True Positives (TP)", f"{tp:,}", help="Correctly identified CS")
        
        # Calculate error rate
        error_rate = (fp + fn) / (tn + fp + fn + tp) * 100
        st.metric("Error Rate", f"{error_rate:.2f}%")
    
    st.markdown("---")
    
    # Visualizations
    st.markdown("## 📈 Performance Visualizations")
    
    eval_dir = MODELS_DIR / "evaluation"
    
    if eval_dir.exists():
        tab1, tab2, tab3 = st.tabs(["ROC Curve", "Precision-Recall", "Performance Summary"])
        
        with tab1:
            roc_path = eval_dir / "roc_curve.png"
            if roc_path.exists():
                st.image(str(roc_path), caption="ROC Curve - Receiver Operating Characteristic", use_container_width=True)
                st.markdown(f"""
                <div class="info-box">
                <strong>ROC-AUC Score: {metrics['roc_auc']:.4f}</strong><br>
                The ROC curve shows the trade-off between true positive rate and false positive rate. 
                An AUC of {metrics['roc_auc']:.4f} indicates {'excellent' if metrics['roc_auc'] > 0.9 else 'very good' if metrics['roc_auc'] > 0.8 else 'good'} classification performance.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("ROC curve visualization not found")
        
        with tab2:
            pr_path = eval_dir / "precision_recall_curve.png"
            if pr_path.exists():
                st.image(str(pr_path), caption="Precision-Recall Curve", use_container_width=True)
                st.markdown(f"""
                <div class="info-box">
                <strong>PR-AUC Score: {metrics['pr_auc']:.4f}</strong><br>
                The Precision-Recall curve is particularly useful for imbalanced datasets. 
                Higher values indicate better performance in identifying positive cases.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("Precision-Recall curve not found")
        
        with tab3:
            perf_path = eval_dir / "performance_metrics.png"
            if perf_path.exists():
                st.image(str(perf_path), caption="Performance Metrics Summary", use_container_width=True)
            else:
                st.warning("Performance summary not found")
    
    st.markdown("---")
    
    # Per-class metrics
    st.markdown("## 📋 Per-Class Performance")
    
    if 'classification_report' in metrics:
        report = metrics['classification_report']
        
        # Create DataFrame for better display
        report_data = []
        for class_name in ['No Code-Switching', 'Code-Switching']:
            if class_name in report:
                report_data.append({
                    'Class': class_name,
                    'Precision': f"{report[class_name]['precision']:.4f}",
                    'Recall': f"{report[class_name]['recall']:.4f}",
                    'F1-Score': f"{report[class_name]['f1-score']:.4f}",
                    'Support': report[class_name]['support']
                })
        
        report_df = pd.DataFrame(report_data)
        st.dataframe(report_df, use_container_width=True, hide_index=True)
        
        # Weighted averages
        if 'weighted avg' in report:
            st.markdown("### 📊 Weighted Averages")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Precision", f"{report['weighted avg']['precision']:.4f}")
            with col2:
                st.metric("Recall", f"{report['weighted avg']['recall']:.4f}")
            with col3:
                st.metric("F1-Score", f"{report['weighted avg']['f1-score']:.4f}")
    
    # Model interpretation
    st.markdown("---")
    st.markdown("## 🧠 Model Interpretation")
    
    if metrics['accuracy'] >= 0.90:
        interpretation = "🌟 Excellent"
        color = "success"
    elif metrics['accuracy'] >= 0.85:
        interpretation = "✅ Very Good"
        color = "success"
    elif metrics['accuracy'] >= 0.80:
        interpretation = "👍 Good"
        color = "info"
    elif metrics['accuracy'] >= 0.75:
        interpretation = "⚠️ Acceptable"
        color = "warning"
    else:
        interpretation = "❌ Needs Improvement"
        color = "warning"
    
    st.markdown(f"""
    <div class="{color}-box">
    <strong>Overall Assessment: {interpretation}</strong><br>
    The model achieves {metrics['accuracy']*100:.2f}% accuracy in detecting code-switching patterns.
    </div>
    """, unsafe_allow_html=True)
    
    # Balanced accuracy
    balanced_acc = (metrics['sensitivity'] + metrics['specificity']) / 2
    st.metric("Balanced Accuracy", f"{balanced_acc:.4f}", 
             help="Average of sensitivity and specificity")
    
    # Recommendations
    st.markdown("### 💡 Recommendations")
    
    recommendations = []
    
    if metrics['precision'] < metrics['recall']:
        recommendations.append("• Model has more false positives - consider adjusting classification threshold")
    elif metrics['recall'] < metrics['precision']:
        recommendations.append("• Model has more false negatives - may benefit from additional training data")
    
    if metrics['accuracy'] < 0.85:
        recommendations.append("• Consider collecting more diverse training data")
        recommendations.append("• Try data augmentation techniques")
        recommendations.append("• Experiment with different model architectures or hyperparameters")
    
    tn, fp, fn, tp = cm.ravel()
    if fp > fn:
        recommendations.append("• Many false positives - consider tightening classification threshold")
    elif fn > fp:
        recommendations.append("• Many false negatives - consider lowering classification threshold")
    
    if recommendations:
        for rec in recommendations:
            st.markdown(rec)
    else:
        st.success("✅ Model performance is excellent! No immediate recommendations.")