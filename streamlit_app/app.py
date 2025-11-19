"""
Enhanced Streamlit Web Interface with Real-Time Market Data
"""

import streamlit as st
import sys
from pathlib import Path
import plotly.graph_objects as go
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from chatbot.financial_chatbot import KenyanFinancialChatbot

# Page configuration
st.set_page_config(
    page_title="🇰🇪 Kenyan Financial Advisor (Live)",
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
    .live-badge {
        background-color: #4CAF50;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .static-badge {
        background-color: #9E9E9E;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-size: 0.8rem;
    }
    .market-card {
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.3rem;
    }
    .stock-item {
        padding: 0.5rem;
        margin: 0.3rem 0;
        background-color: white;
        border-radius: 0.3rem;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Streamlit version compatibility
def rerun():
    """Backwards-compatible rerun"""
    if hasattr(st, 'rerun'):
        st.rerun()
    else:
        st.experimental_rerun()

# Initialize chatbot
@st.cache_resource
def load_chatbot():
    """Load chatbot with live data enabled (cached for performance)"""
    return KenyanFinancialChatbot(use_live_data=True)

# Initialize session state
if 'chatbot' not in st.session_state:
    with st.spinner("🚀 Loading Enhanced Financial Advisor with Live Data..."):
        st.session_state.chatbot = load_chatbot()
        st.session_state.messages = []
        st.session_state.language_stats = {
            'english': 0,
            'swahili': 0,
            'code_switched': 0
        }
        st.session_state.live_data_count = 0

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/49/Flag_of_Kenya.svg", 
             width=100)
    st.title("🇰🇪 Kenyan Financial Advisor")
    
    # Live data status
    try:
        market_status = st.session_state.chatbot.get_market_status()
        st.success(f"📊 LIVE MODE: {market_status}")
    except:
        st.warning("📊 Static Mode (Live data unavailable)")
    
    st.markdown("---")
    
    # Real-time Market Data Section
    st.subheader("📈 Live Market Data")
    
    try:
        # Get live market summary
        market_fetcher = st.session_state.chatbot.market_fetcher
        market_summary = market_fetcher.get_market_summary()
        
        # Market sentiment
        sentiment_color = {
            'BULLISH': '#4CAF50',
            'NEUTRAL': '#FFC107',
            'BEARISH': '#F44336'
        }.get(market_summary['sentiment'], '#9E9E9E')
        
        st.markdown(f"""
        <div class="market-card">
            <h4 style='margin:0; color:{sentiment_color};'>{market_summary['emoji']} {market_summary['sentiment']}</h4>
            <p style='margin:0.3rem 0; font-size:0.9rem;'>
                Gainers: <b>{market_summary['gainers']}</b> | 
                Losers: <b>{market_summary['losers']}</b>
            </p>
            <p style='margin:0; font-size:0.8rem; color:#666;'>
                Avg Change: {market_summary['avg_change']:+.2f}%
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Top NSE Stocks
        with st.expander("📊 NSE Top Stocks", expanded=False):
            nse_stocks = market_fetcher.get_nse_stocks(['SCOM', 'EQTY', 'KCB'])
            for symbol, data in nse_stocks.items():
                change_color = '#4CAF50' if data['change'] > 0 else '#F44336'
                arrow = "📈" if data['change'] > 0 else "📉"
                
                st.markdown(f"""
                <div class="stock-item">
                    <b>{data['name']}</b> ({symbol})<br>
                    <span style='font-size:1.1rem;'>KSh {data['price']}</span>
                    <span style='color:{change_color}; font-size:0.9rem;'>
                        {arrow} {data['change']:+.2f} ({data['change_percent']:+.2f}%)
                    </span><br>
                    <span style='font-size:0.8rem; background-color:#e3f2fd; padding:0.1rem 0.3rem; border-radius:0.2rem;'>
                        {data['signal']}
                    </span>
                </div>
                """, unsafe_allow_html=True)
        
        # Top MMFs
        with st.expander("💰 Money Market Funds", expanded=False):
            mmf_rates = market_fetcher.get_mmf_rates()
            # Show top 3
            sorted_mmfs = sorted(mmf_rates.items(), 
                               key=lambda x: x[1]['current_rate'], 
                               reverse=True)[:3]
            
            for name, data in sorted_mmfs:
                st.markdown(f"""
                <div class="stock-item">
                    <b>{name}</b><br>
                    <span style='font-size:1.1rem; color:#1f77b4;'>{data['current_rate']}%</span>
                    <span style='font-size:0.8rem;'> (Min: KSh {data['minimum']:,})</span><br>
                    <span style='font-size:0.8rem; color:#4CAF50;'>{data['recommendation']}</span>
                </div>
                """, unsafe_allow_html=True)
        
        # Global Stocks (sample)
        with st.expander("🌍 Global Market Snapshot", expanded=False):
            try:
                for symbol in ['AAPL', 'TSLA']:
                    global_stock = market_fetcher.get_global_stock(symbol)
                    if global_stock:
                        change_color = '#4CAF50' if global_stock['change'] > 0 else '#F44336'
                        arrow = "📈" if global_stock['change'] > 0 else "📉"
                        
                        st.markdown(f"""
                        <div class="stock-item">
                            <b>{global_stock['name']}</b> ({symbol})<br>
                            <span style='font-size:1.1rem;'>${global_stock['price']}</span>
                            <span style='color:{change_color}; font-size:0.9rem;'>
                                {arrow} {global_stock['change']:+.2f} ({global_stock['change_percent']:+.2f}%)
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
            except:
                st.info("Global data loading...")
        
        # Last update time
        st.caption(f"🕒 Updated: {market_summary['last_update'].strftime('%H:%M:%S')}")
        
    except Exception as e:
        st.info("📊 Live data unavailable. Using static knowledge.")
    
    st.markdown("---")
    
    # Language Usage Stats
    st.subheader("📊 Your Language Usage")
    
    if sum(st.session_state.language_stats.values()) > 0:
        fig = go.Figure(data=[go.Pie(
            labels=['English', 'Swahili', 'Code-Switched'],
            values=[
                st.session_state.language_stats['english'],
                st.session_state.language_stats['swahili'],
                st.session_state.language_stats['code_switched']
            ],
            marker=dict(colors=['#2196F3', '#4CAF50', '#FF9800']),
            hole=0.3
        )])
        fig.update_layout(
            height=200,
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Stats
        total = sum(st.session_state.language_stats.values())
        st.caption(f"Total messages: {total} | Live data used: {st.session_state.live_data_count}")
    else:
        st.info("Start chatting to see your language pattern!")
    
    st.markdown("---")
    
    # Tips
    st.subheader("💡 Ask About")
    st.markdown("""
    - 💰 **Investment advice** (with amounts!)
    - 📈 **Stock recommendations** (live NSE data)
    - 💵 **Best MMF rates** (real-time)
    - 📱 **M-Pesa** operations
    - 👥 **Chamas & SACCOs**
    - 🌍 **Global stocks** (Apple, Tesla, etc.)
    """)
    
    st.markdown("---")
    
    # Controls
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.session_state.chatbot.clear_history()
        st.session_state.language_stats = {
            'english': 0,
            'swahili': 0,
            'code_switched': 0
        }
        st.session_state.live_data_count = 0
        rerun()
    
    if st.button("🔄 Refresh Market Data"):
        # Clear cache to force refresh
        st.cache_resource.clear()
        st.success("Market data refreshed!")
        rerun()
    
    st.markdown("---")
    st.caption("💡 **Live Mode**: Real-time NSE, MMF, and global stock data")
    st.caption("Built for MSc Thesis - Joan Waweru")

# Main content
st.markdown('<h1 class="main-header">💬 Kenyan Financial Advisor (Live Edition)</h1>', 
            unsafe_allow_html=True)

# Feature badges
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<span class="live-badge">📊 LIVE NSE DATA</span>', unsafe_allow_html=True)
with col2:
    st.markdown('<span class="live-badge">💰 REAL MMF RATES</span>', unsafe_allow_html=True)
with col3:
    st.markdown('<span class="live-badge">🌍 GLOBAL STOCKS</span>', unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center; margin: 1rem 0 2rem 0;'>
    <p style='font-size: 1.1rem;'>
        Get <b>real-time</b> investment advice with <b>live market data</b>! 🚀
    </p>
    <p style='color: #666; font-size: 0.9rem;'>
        Ask in English, Swahili, or mix them (code-switching) • Powered by AI + Live Data
    </p>
</div>
""", unsafe_allow_html=True)

# Display welcome message if no chat history
if len(st.session_state.messages) == 0:
    welcome_msg = st.session_state.chatbot.get_welcome_message()
    st.info(welcome_msg)
    
    # Example questions with live data emphasis
    st.subheader("💡 Try these (with real-time data!):")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📈 Which stocks should I buy today?"):
            st.session_state.example_query = "Which stocks should I buy today?"
            rerun()
    
    with col2:
        if st.button("💰 Best MMF right now?"):
            st.session_state.example_query = "Which MMF has the best rates right now?"
            rerun()
    
    with col3:
        if st.button("🇰🇪 I have 100k, invest wapi?"):
            st.session_state.example_query = "niko na 100k, niweke wapi?"
            rerun()

# Display chat messages
for message in st.session_state.messages:
    if message['role'] == 'user':
        st.markdown(f"""
        <div class='chat-message user-message'>
            <div style='font-weight: bold;'>👤 You</div>
            <div style='margin: 0.5rem 0;'>{message['content']}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Determine if response used live data
        live_badge = ""
        if message.get('used_live_data'):
            live_badge = '<span class="live-badge">🔴 LIVE DATA</span> '
        else:
            live_badge = '<span class="static-badge">📚 Knowledge Base</span> '
        
        st.markdown(f"""
        <div class='chat-message bot-message'>
            <div style='font-weight: bold;'>🤖 Financial Advisor {live_badge}</div>
            <div style='margin: 0.5rem 0;'>{message['content']}</div>
            <div style='font-size: 0.8rem; color: #666; margin-top: 0.5rem;'>
                🌐 {message.get('language', 'N/A')} | 
                🎯 {message.get('confidence', 0)*100:.1f}% | 
                📊 Swahili: {message.get('swahili_ratio', 0)*100:.0f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

# Chat input
user_input = st.chat_input("Ask me anything! (e.g., 'niko na 50k, best investment?')")

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
    with st.spinner("🤔 Analyzing with live market data..."):
        response = st.session_state.chatbot.chat(user_input)
    
    # Update stats
    detected_lang = response['detected_language']
    st.session_state.language_stats[detected_lang] += 1
    
    if response.get('used_live_data'):
        st.session_state.live_data_count += 1
    
    # Add bot message to chat
    st.session_state.messages.append({
        'role': 'assistant',
        'content': response['response'],
        'language': detected_lang,
        'confidence': response['confidence'],
        'swahili_ratio': response['swahili_ratio'],
        'used_live_data': response.get('used_live_data', False)
    })
    
    # Rerun to display new messages
    rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p><b>🚀 Enhanced Kenyan Financial Advisor with Real-Time Data</b></p>
    <p style='font-size: 0.9rem;'>
        Live NSE Prices • Real MMF Rates • Global Stocks • Adaptive Code-Switching • AI-Powered
    </p>
    <p style='font-size: 0.85rem;'>
        MSc Data Science Thesis Project • University of Debrecen, Hungary 🇭🇺 | Built with ❤️ for Kenya 🇰🇪
    </p>
</div>
""", unsafe_allow_html=True)