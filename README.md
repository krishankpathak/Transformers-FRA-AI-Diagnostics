# Transformer FRA AI Diagnostic System v2.0.0

## 🌟 Overview
A professional-grade, high-resolution diagnostic platform for transformer health assessment using **Frequency Response Analysis (FRA)**. This project leverages state-of-the-art machine learning ensembles and expert system logic to detect mechanical and electrical faults in power transformers with extreme precision.

Developed with **hard work and deep domain expertise**, this system bridges the gap between raw spectral data and actionable maintenance intelligence.

---

## 🚀 Key Features
- **Triple Ensemble AI Engine**: Combines **Random Forest**, **XGBoost**, and **CatBoost** for a robust classification accuracy of 97%+.
- **3D Spectral Visualization**: High-quality 3D frequency response surfaces for spatial analysis of winding and core behavior.
- **Expert Diagnostic Logic**: Automated compliance checks against **IEEE C57.149** and **DL/T 911-2004** standards.
- **Data Lake Intelligence**: Real-time monitoring and exploration of a 1,500+ sample labeled training dataset.
- **Automated Reporting**: One-click generation of professional PDF diagnostic summaries and raw CSV data exports.
- **Bulletproof Stability**: Global error handling and data integrity validation to ensure zero-crash performance.

---

## 🏗 Project Structure
```text
.
├── api/                    # FastAPI Backend & Web Logic
│   ├── routes/             # API Endpoints (Prediction, Analysis)
│   ├── static/             # Frontend Assets (CSS, JS, Images)
│   ├── templates/          # Jinja2 HTML Templates (Dashboard, Results)
│   ├── main.py             # Main Entry Point & Server Config
│   └── plotter.py          # High-Res Matplotlib & 3D Visualization
├── src/                    # Core AI & Logic Modules
│   ├── fra_module/         # FRA Analysis, Models, & Anomaly Detection
│   ├── rul_module/         # Remaining Useful Life & Expert Rules
│   └── utils/              # PDF Generation & Data Parsing
├── data/                   # Data Infrastructure
│   ├── news_csvs/          # Data Lake (1,500+ Training Samples)
│   ├── raw/                # Baseline & Healthy Reference Data
│   └── processed/          # ML-Ready Feature Datasets
├── models/                 # Pre-trained ML Models (PKL, JSON, CBM)
├── reports/                # Generated Diagnostic Reports (PDF/CSV)
├── README.md               # Project Documentation
└── requirements.txt        # Essential System Dependencies
```

---

## 🛠 Diagnostic Pipeline Flow
1. **Data Ingest**: Upload raw FRA sweep data (.csv, .xlsx).
2. **Preprocessing**: Automated frequency alignment and baseline normalization.
3. **Feature Extraction**: Capturing resonance peaks, Q-factors, and spectral shifts.
4. **Triple Ensemble Inference**: Parallel processing by RF, XGB, and CatBoost models.
5. **Expert System Analysis**: Correlation coefficient calculation and standard compliance checks.
6. **Visualization**: Real-time rendering of Comparison, Difference, and 3D Surface plots.
7. **Report Generation**: Final diagnostic summary output in PDF/CSV formats.

---

## 📊 Data Lake Information
The intelligence of this system is built upon a vast **Data Lake** of over **1,500 high-fidelity FRA curves**. 
- **Healthy Base**: 500+ baseline reference scans.
- **Winding Deformation**: 300+ samples of radial and axial shifts.
- **Core Displacement**: 300+ samples of mechanical core movement.
- **Insulation Degradation**: 400+ samples of dielectric property changes.

---

## ⚙ Installation & Usage
1. **Clone & Setup**:
   ```bash
   git clone https://github.com/krishankpathak/Transformers-FRA-AI-Diagnostics.git
   cd Transformers-FRA-AI-Diagnostics
   pip install -r requirements.txt
   ```
2. **Run System**:
   ```bash
   python api/main.py
   ```
3. **Access Dashboard**: Open [http://localhost:8000/analysis](http://localhost:8000/analysis)

---

## 📝 Authors & Contact
- **Krishank Pathak** (krishankpathak)
- **Email**: anandprakashpathak07469@gmail.com
- **LinkedIn**: [Krishank Pathak](https://www.linkedin.com/in/krishankpathak/)

---
*This system represents a significant advancement in automated transformer diagnostics, combining modern AI with traditional electrical engineering principles.*
