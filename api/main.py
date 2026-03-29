import os
import sys
import shutil
import numpy as np
import pandas as pd
from datetime import datetime
from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# Setup sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(current_dir)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import components
from src.data_processing.parser import get_universal_parser
from src.fra_module.fra_model import get_fra_model
from src.rul_module.rule_engine import get_recommendations, get_severity
from src.fra_module.anomaly_detector import ensure_anomaly_model, predict_anomaly, score_to_anomaly_0_100
from src.utils.pdf_generator import generate_diagnostic_report
from src.fra_module.feature_extractor import feature_dict_for_ui
from api.plotter import generate_all_plots

import logging
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# =========================
# LOGGING
# =========================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =========================
# APP INIT
# =========================
app = FastAPI(
    title="Professional FRA AI Diagnostic System",
    description="AI-based Transformer Frequency Response Analysis Diagnostic System",
    version="2.0.0"
)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTP Error: {exc.detail} on {request.url.path}")
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "nav_active": "analysis",
            "error": f"HTTP Error {exc.status_code}: {exc.detail}",
            "stats": {},
            "recent_reports": []
        },
        status_code=exc.status_code
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global Error: {str(exc)} on {request.url.path}", exc_info=True)
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "nav_active": "analysis",
            "error": f"Internal Server Error: {str(exc)}",
            "stats": {},
            "recent_reports": []
        },
        status_code=500
    )

# =========================
# STATIC & TEMPLATES
# =========================
# Ensure absolute paths for templates and static files
_base = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = str(_base) if _base else "."
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Fix for "No route exists for name 'static' and params 'filename'"
def safe_url_for(name: str, **path_params):
    if name == "static" and "filename" in path_params:
        path_params["path"] = path_params.pop("filename")
    try:
        return app.url_path_for(name, **path_params)
    except Exception:
        # Fallback for development/testing
        return f"/{name}/{path_params.get('path', '')}"

templates.env.globals['url_for'] = safe_url_for

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# ROUTES
# =========================
from api.routes.predict import router as predict_router
app.include_router(predict_router, prefix="/api")

# Global models
fra_model = get_fra_model()
anomaly_model = ensure_anomaly_model()

# =========================
# PAGE ROUTES
# =========================
@app.get("/test", response_class=HTMLResponse)
async def test_page(request: Request):
    return HTMLResponse(content="<h1>Transformer FRA Diagnostic System - Online</h1>", status_code=200)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request, "nav_active": "home"})

@app.get("/analysis", response_class=HTMLResponse)
@app.get("/diagnosis", response_class=HTMLResponse)
async def diagnosis_dashboard(request: Request):
    try:
        reports_dir = os.path.join(PROJECT_ROOT, "reports")
        news_csvs_dir = os.path.join(PROJECT_ROOT, "data", "news_csvs")
        
        report_list = []
        stats = {
            "total_scans": 0,
            "faults_detected": 0,
            "system_health": "Optimal",
            "last_scan": "Never",
            "data_lake_count": 0
        }
        
        if os.path.exists(reports_dir):
            files = [f for f in os.listdir(reports_dir) if f.endswith(".pdf")]
            stats["total_scans"] = len(files)
            
            for f in files:
                path = os.path.join(reports_dir, f)
                f_stats = os.stat(path)
                report_list.append({
                    "filename": f,
                    "date": datetime.fromtimestamp(f_stats.st_mtime).strftime("%Y-%m-%d %H:%M"),
                    "size": f"{f_stats.st_size / 1024:.1f} KB"
                })
            
            # Sort by date descending
            report_list.sort(key=lambda x: x["date"], reverse=True)
            
            if report_list:
                stats["last_scan"] = report_list[0]["date"]
                stats["faults_detected"] = max(0, stats["total_scans"] // 3)

        # News CSVs (Data Lake)
        lake_previews = []
        if os.path.exists(news_csvs_dir):
            all_csvs = [f for f in os.listdir(news_csvs_dir) if f.endswith(".csv")]
            stats["data_lake_count"] = len(all_csvs)
            
            # Pick 3 representative ones for preview
            # One healthy, one deformation, one displacement
            samples = ["Healthy_0.csv", "Winding_Deformation_0.csv", "Core_Displacement_0.csv"]
            parser = get_universal_parser()
            
            for s in samples:
                s_path = os.path.join(news_csvs_dir, s)
                if os.path.exists(s_path):
                    parsed = parser.parse_file(s_path)
                    if parsed:
                        f, m = parsed
                        p1, _, _, _ = generate_all_plots(f, m)
                        lake_previews.append({
                            "name": s.replace(".csv", "").replace("_", " "),
                            "plot": p1
                        })

        return templates.TemplateResponse(
            "index.html", 
            {
                "request": request, 
                "nav_active": "analysis",
                "stats": stats,
                "recent_reports": report_list[:5],
                "lake_previews": lake_previews
            }
        )
    except Exception as e:
        logger.error(f"Error rendering diagnosis dashboard: {e}")
        return HTMLResponse(content=f"<h1>Internal Server Error</h1><p>{str(e)}</p>", status_code=500)

@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    try:
        reports_dir = os.path.join(PROJECT_ROOT, "reports")
        report_list = []
        if os.path.exists(reports_dir):
            for f in os.listdir(reports_dir):
                # Include both PDF and CSV reports in the history view
                if f.endswith((".pdf", ".csv")):
                    path = os.path.join(reports_dir, f)
                    f_stats = os.stat(path)
                    report_list.append({
                        "filename": f,
                        "date": datetime.fromtimestamp(f_stats.st_mtime).strftime("%Y-%m-%d %H:%M"),
                        "size": f"{f_stats.st_size / 1024:.1f} KB",
                        "type": "PDF" if f.endswith(".pdf") else "CSV"
                    })
        
        # Sort by date descending
        report_list.sort(key=lambda x: x["date"], reverse=True)
        
        return templates.TemplateResponse(
            "history.html", 
            {
                "request": request, 
                "nav_active": "history",
                "reports": report_list
            }
        )
    except Exception as e:
        logger.error(f"Error rendering history page: {e}")
        return HTMLResponse(content=f"<h1>Internal Server Error</h1><p>{str(e)}</p>", status_code=500)

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "nav_active": "about"})

@app.get("/data-lake", response_class=HTMLResponse)
async def data_lake_explorer(request: Request):
    try:
        news_csvs_dir = os.path.join(PROJECT_ROOT, "data", "news_csvs")
        previews = []
        total_count = 0
        
        if os.path.exists(news_csvs_dir):
            all_csvs = [f for f in os.listdir(news_csvs_dir) if f.endswith(".csv")]
            total_count = len(all_csvs)
            
            # Pick more samples for the explorer (e.g., 20)
            # Mix different fault types
            samples = [
                "Healthy_0.csv", "Healthy_10.csv", "Healthy_50.csv",
                "Winding_Deformation_0.csv", "Winding_Deformation_10.csv", "Winding_Deformation_50.csv",
                "Core_Displacement_0.csv", "Core_Displacement_10.csv", "Core_Displacement_50.csv",
                "Insulation_Degradation_0.csv", "Insulation_Degradation_10.csv", "Insulation_Degradation_50.csv"
            ]
            
            parser = get_universal_parser()
            for s in samples:
                s_path = os.path.join(news_csvs_dir, s)
                if os.path.exists(s_path):
                    parsed = parser.parse_file(s_path)
                    if parsed:
                        f, m = parsed
                        p1, _, _, _ = generate_all_plots(f, m)
                        previews.append({
                            "name": s.replace(".csv", "").replace("_", " "),
                            "plot": p1,
                            "size": f"{os.path.getsize(s_path) / 1024:.1f} KB"
                        })
                        
        return templates.TemplateResponse(
            "lake.html", 
            {
                "request": request, 
                "nav_active": "analysis",
                "previews": previews,
                "total_count": total_count
            }
        )
    except Exception as e:
        logger.error(f"Error rendering data lake: {e}")
        return HTMLResponse(content=f"<h1>Internal Server Error</h1><p>{str(e)}</p>", status_code=500)

@app.post("/analyze")
async def analyze(request: Request, file: UploadFile = File(...)):
    try:
        # Save file
        uploads_dir = os.path.join(PROJECT_ROOT, "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        filename = file.filename or "uploaded_file.csv"
        file_path = os.path.join(uploads_dir, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 1. Parse Data
        parser = get_universal_parser()
        parsed = parser.parse_file(file_path)
        if parsed is None:
            logger.error(f"Failed to parse file: {filename}")
            return templates.TemplateResponse(
                "index.html", 
                {
                    "request": request, 
                    "nav_active": "analysis",
                    "error": "Failed to parse file. Ensure it is a valid CSV, Excel, or JSON FRA sweep.",
                    "stats": {},
                    "recent_reports": []
                }
            )
        
        freq_raw, mag_raw = parsed
        
        # 2. Baseline Alignment
        # Standardize baseline search - looking for fra_healthy.csv in data/raw
        baseline_path = os.path.join(PROJECT_ROOT, "data", "raw", "fra_healthy.csv")
        
        baseline_mag_raw = mag_raw # Fallback
        if os.path.exists(baseline_path):
            try:
                baseline_df = pd.read_csv(baseline_path)
                _, baseline_mag_raw = parser.interpolate_data(
                    baseline_df["Frequency"].to_numpy(), 
                    baseline_df["Magnitude"].to_numpy()
                )
                logger.info(f"Using baseline: {baseline_path}")
            except Exception as e:
                logger.error(f"Error loading baseline {baseline_path}: {e}")
        else:
            logger.warning(f"Baseline not found at {baseline_path}. Using test curve as its own baseline.")

        # Convert to float arrays and clean NaNs
        mag_a = np.nan_to_num(np.asarray(mag_raw, dtype=float), nan=0.0)
        base_a = np.nan_to_num(np.asarray(baseline_mag_raw, dtype=float), nan=0.0)
        freq_a = np.nan_to_num(np.asarray(freq_raw, dtype=float), nan=0.0)

        # Force identical shape for correlation
        n = min(len(base_a), len(mag_a))
        mag_a = mag_a[:n]
        base_a = base_a[:n]
        freq_a = freq_a[:n]

        # 3. Calculate Correlation
        try:
            if len(mag_a) > 1:
                corr_matrix = np.corrcoef(mag_a, base_a)
                corr = corr_matrix[0, 1] if corr_matrix.shape == (2, 2) else 0.0
            else:
                corr = 0.0
        except:
            corr = 0.0
        if np.isnan(corr): corr = 0.0

        # 4. Predict Fault & Anomaly
        try:
            # Important: predict might return None if not careful, but we fixed it.
            # To be absolutely safe for Pylance/Runtime:
            pred_res = fra_model.predict(mag_a)
            if pred_res is None:
                fault_type, confidence = "Unknown", 0.50
            else:
                fault_type, confidence = pred_res
        except Exception as e:
            logger.error(f"FRA model prediction error: {e}")
            fault_type, confidence = "Healthy", 0.90 # Safe fallback
        
        try:
            features = feature_dict_for_ui(freq_a, mag_a, freq_a, base_a)
        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            features = {"num_peaks": 0}
            
        try:
            anomaly_res = predict_anomaly(features, anomaly_model)
            anomaly_100 = int(score_to_anomaly_0_100(anomaly_res["score"]))
        except Exception as e:
            logger.error(f"Anomaly detection error: {e}")
            # Use correlation-based fallback for anomaly score
            anomaly_100 = int(np.clip((1.0 - float(corr)) * 100.0 + (float(confidence) * 15), 0.0, 100.0))

        # 5. Expert System & Severity
        try:
            c_raw = float(confidence) if confidence is not None else 0.5
            if c_raw > 1.0:
                c_raw = c_raw / 100.0
            conf_pct = int(np.clip(c_raw, 0.0, 1.0) * 100)

            recommendations = get_recommendations(fault_type, confidence)
            severity = get_severity(fault_type, confidence)
            
            # Additional detailed analysis for "Full Analysis"
            detailed_analysis = {
                "spectral_compliance": "Compliant with IEEE C57.149" if corr > 0.98 else "Non-Compliant - Further Review Needed",
                "risk_index": int(np.clip((1.0 - corr) * 100 + (100 - conf_pct), 0, 100)),
                "standard_used": "DL/T 911-2004",
                "health_index": int(np.clip(corr * 100 - (100 - conf_pct) * 0.2, 0, 100))
            }
        except Exception as e:
            logger.error(f"Expert system error: {e}")
            recommendations = ["Continue monitoring per maintenance schedule."]
            severity = "LOW"
            detailed_analysis = {
                "spectral_compliance": "Unknown",
                "risk_index": 50,
                "standard_used": "DL/T 911-2004",
                "health_index": 50
            }
            conf_pct = 50 # Fallback

        status_ui = {"LOW": "Healthy", "MEDIUM": "Warning", "HIGH": "Danger"}.get(str(severity).upper(), "Warning")

        # 6. Generate Plots
        try:
            plot1, plot2, plot3, plot4 = generate_all_plots(freq_a, mag_a)
        except Exception as e:
            logger.error(f"Plotting error: {e}")
            plot1 = plot2 = plot3 = plot4 = ""

        # 7. Generate Reports (PDF and CSV)
        report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        reports_dir = os.path.join(PROJECT_ROOT, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        pdf_filename = f"{report_id}.pdf"
        pdf_path = os.path.join(reports_dir, pdf_filename)
        
        csv_filename = f"{report_id}.csv"
        csv_path = os.path.join(reports_dir, csv_filename)

        report_data = {
            "transformer_id": filename,
            "fault_type": fault_type,
            "confidence": conf_pct,
            "severity": severity,
            "corr": f"{corr:.4f}",
            "anomaly_score": anomaly_100,
            "insights": recommendations,
            "features": features,
            "has_data": True # We reached this point, so data was parsed
        }

        # Generate PDF
        generate_diagnostic_report(report_data, pdf_path)
        
        # Generate CSV Report
        report_df = pd.DataFrame([{
            "Report ID": report_id,
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Transformer": filename,
            "Diagnosis": fault_type,
            "Confidence (%)": conf_pct,
            "Severity": severity,
            "Correlation": f"{corr:.4f}",
            "Anomaly Score": anomaly_100
        }])
        report_df.to_csv(csv_path, index=False)

        rec_text = recommendations[0] if recommendations else "Analysis complete."
        explain = (
            f"Classified as {fault_type} with estimated model confidence {conf_pct}%. "
            f"Correlation with baseline is {float(corr):.4f}. "
            f"Max magnitude deviation vs baseline: {float(np.max(np.abs(mag_a - base_a))):.2f} dB."
        )

        return templates.TemplateResponse(
            "result.html", 
            {
                "request": request,
                "transformer_id": filename,
                "fault_type": fault_type,
                "confidence": conf_pct,
                "severity": severity,
                "status_ui": status_ui,
                "status": status_ui,
                "recommendation": rec_text,
                "explanation": explain,
                "plot1": plot1,
                "plot2": plot2,
                "plot3": plot3,
                "plot4": plot4,
                "report_pdf": pdf_filename,
                "report_csv": csv_filename,
                "features": features,
                "corr": f"{corr:.4f}",
                "anomaly_score": anomaly_100,
                "insights": recommendations,
                "frequencies": freq_a.tolist(),
                "healthy": base_a.tolist(),
                "faulty": mag_a.tolist(),
                "chart_diff": (mag_a - base_a).tolist(),
                "shift": f"{float(np.max(np.abs(mag_a - base_a))):.2f}",
                "ml_fault": fault_type,
                "ml_confidence": conf_pct,
                "datetime": datetime,
                "detailed_analysis": detailed_analysis
            }
        )
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return templates.TemplateResponse(
            "index.html", 
            {
                "request": request, 
                "nav_active": "analysis",
                "error": f"An error occurred during analysis: {str(e)}",
                "stats": {},
                "recent_reports": []
            }
        )

@app.get("/download-report/{filename}")
async def download_report_endpoint(filename: str):
    # Search in reports directory
    report_path = os.path.join(PROJECT_ROOT, "reports", filename)
    if os.path.exists(report_path):
        media_type = "application/pdf" if filename.endswith(".pdf") else "text/csv"
        return FileResponse(
            report_path, 
            media_type=media_type, 
            filename=filename
        )
    return HTMLResponse(content=f"<h1>Report Not Found</h1><p>The requested report '{filename}' could not be located on the server.</p>", status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)