# Transformer-FRA-AI-Diagnostics

## Overview
A professional, high-resolution diagnostic system for transformer health assessment using **Frequency Response Analysis (FRA)**. The system combines multiple machine learning models and an expert diagnostic logic to provide deep insights into transformer mechanical integrity.

## Features
- **Triple Ensemble Model**: Combines Random Forest, XGBoost, and CatBoost for high-accuracy (97%+) fault classification.
- **Advanced 3D Visualization**: Generates 3D frequency response surfaces for better spatial analysis of spectral shifts.
- **Expert Diagnostic Engine**: Implements IEEE C57.149 and DL/T 911-2004 standards for technical compliance checks.
- **Automated Reporting**: Generates professional PDF diagnostic reports and raw CSV exports.
- **Data Lake Intelligence**: Built-in dashboard to monitor and preview large-scale training datasets.

## Core Fault Detection
- **Healthy**: Normal baseline response.
- **Winding Deformation**: Radial or axial displacement of windings.
- **Core Displacement**: Mechanical shifts in the transformer core.
- **Insulation Degradation**: Changes in dielectric properties.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/krishankpathak/Transformer-FRA-AI-Diagnostics.git
   cd Transformer-FRA-AI-Diagnostics
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the system:
   ```bash
   python api/main.py
   ```

## Technology Stack
- **Backend**: FastAPI (Python)
- **Frontend**: Jinja2 Templates, Tailwind CSS, Lucide Icons
- **Machine Learning**: Scikit-learn, XGBoost, CatBoost
- **Visualization**: Matplotlib, Plotly (3D rendering)
- **Reporting**: ReportLab (PDF engine)

## Authors
- **Krishank Pathak** (krishankpathak)
- Email: anandprakashpathak07469@gmail.com
