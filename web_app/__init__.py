"""
Web application module for Multilingual Financial AI System
Streamlit-based interactive interface
"""

import logging

logger = logging.getLogger(__name__)

# Module version
__version__ = "1.0.0"

# Module description
__doc__ = """
Web Application Module
======================

This module provides a Streamlit-based web interface for:
- Interactive chatbot
- Data analysis dashboard
- Model performance visualization
- Documentation and guides

Pages:
1. Chatbot: Interactive financial assistant
2. Data Analysis: Visualizations and statistics
3. Model Performance: Evaluation metrics
4. Documentation: Usage guides and API reference
5. About: Project information

Usage:
    streamlit run web_app/app.py

Features:
- Real-time chat interface
- Interactive visualizations (Plotly)
- Comprehensive analytics
- Model performance tracking
- Responsive design

Requirements:
- streamlit>=1.25.0
- plotly>=5.15.0
- pandas>=2.0.3

Access:
- Local: http://localhost:8501
- Network: http://<your-ip>:8501
"""

# App configuration
APP_CONFIG = {
    'title': 'Multilingual Financial AI',
    'icon': '💬',
    'layout': 'wide',
    'version': '1.0.0',
    'theme': 'light',
    'pages': [
        '🤖 Chatbot',
        '📈 Data Analysis',
        '🔍 Model Performance',
        '📚 Documentation',
        'ℹ️ About'
    ]
}

def get_app_info() -> dict:
    """Get web application information"""
    return APP_CONFIG

logger.info(f"Web app module initialized - Version {__version__}")