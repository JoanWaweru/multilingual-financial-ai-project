"""
Jupyter notebooks for data exploration and analysis
Interactive notebooks for research and experimentation
"""

# Module version
__version__ = "1.0.0"

# Module description
__doc__ = """
Notebooks Module
================

This directory contains Jupyter notebooks for:
- Data exploration and visualization
- Model experimentation
- Results analysis
- Research documentation

Available Notebooks:

1. data_exploration.ipynb
   - Dataset overview
   - Statistical analysis
   - Visualization of patterns
   - Quality assessment

2. model_testing.ipynb
   - Model training experiments
   - Hyperparameter tuning
   - Performance comparison
   - Error analysis

3. results_visualization.ipynb
   - Publication-ready plots
   - Comprehensive analysis
   - Thesis figures
   - Statistical tests

4. code_switching_analysis.ipynb
   - Pattern analysis
   - Language mixing patterns
   - Engagement correlation
   - Country-specific trends

Usage:
    jupyter notebook notebooks/
    
    or
    
    jupyter lab notebooks/

Requirements:
- jupyter>=1.0.0
- matplotlib>=3.7.0
- seaborn>=0.12.0
- pandas>=2.0.0
"""

# Notebook metadata
NOTEBOOKS = {
    'data_exploration': {
        'title': 'Data Exploration and Analysis',
        'description': 'Comprehensive dataset analysis',
        'difficulty': 'Beginner',
        'estimated_time': '30 minutes'
    },
    'model_testing': {
        'title': 'Model Training and Testing',
        'description': 'ML model experiments',
        'difficulty': 'Intermediate',
        'estimated_time': '45 minutes'
    },
    'results_visualization': {
        'title': 'Results Visualization',
        'description': 'Publication-ready figures',
        'difficulty': 'Intermediate',
        'estimated_time': '20 minutes'
    },
    'code_switching_analysis': {
        'title': 'Code-Switching Pattern Analysis',
        'description': 'Deep dive into linguistic patterns',
        'difficulty': 'Advanced',
        'estimated_time': '60 minutes'
    }
}

def list_notebooks() -> dict:
    """List available notebooks with metadata"""
    return NOTEBOOKS