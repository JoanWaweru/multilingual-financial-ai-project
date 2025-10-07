# Multilingual Financial Chatbot - Kenya Code-Switching Research

MSc Data Science Thesis Project

## Overview

This project develops deep learning models for detecting and analyzing code-switching patterns in Kenyan financial communication (English-Swahili). The goal is to create an AI chatbot that uses optimal code-switching strategies to improve user engagement in financial education.

## Features

- 🤖 Code-switching detection using fine-tuned BERT
- 💬 Multilingual chatbot with adaptive language mixing
- 📊 Pattern classification for Kenyan-specific code-switching
- 🌐 Web-based demo interface
- 📈 Engagement analysis and A/B testing

## Project Structure
multilingual_finance_chatbot/
├── data/                    # Datasets
├── data_acquisition/        # Download scripts
├── preprocessing/           # Data cleaning
├── models/                  # Model definitions
├── training/               # Training scripts
├── chatbot/                # Chatbot implementation
├── web_app/                # Streamlit interface
└── results/                # Outputs

## Installation
```bash
# Clone repository
git clone [your-repo-url]
cd multilingual_finance_chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy models
python -m spacy download en_core_web_sm

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys