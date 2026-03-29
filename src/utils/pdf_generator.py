import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch

def generate_diagnostic_report(data, output_path):
    """
    Generates a professional PDF diagnostic report for FRA analysis.
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Custom Styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=20,
        alignment=1 # Center
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor("#38bdf8"),
        spaceBefore=12,
        spaceAfter=10
    )

    # 1. Title
    story.append(Paragraph("FRA Diagnostic Report", title_style))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 0.25 * inch))

    # Data Integrity Check
    has_data = data.get("has_data", True)
    integrity_text = "PASSED: File contains proper FRA sweep data." if has_data else "FAILED: File data is incomplete or corrupted."
    integrity_color = colors.green if has_data else colors.red
    
    story.append(Paragraph("Data Integrity Check", header_style))
    story.append(Paragraph(integrity_text, ParagraphStyle('Integrity', parent=styles['Normal'], textColor=integrity_color, fontWeight='bold')))
    story.append(Spacer(1, 0.2 * inch))

    # 2. Summary Table
    story.append(Paragraph("Diagnostic Summary", header_style))
    summary_data = [
        ["Field", "Value"],
        ["Transformer ID", data.get("transformer_id", "Unknown")],
        ["Diagnosis", data.get("fault_type", "Healthy")],
        ["Confidence", f"{data.get('confidence', 0)}%"],
        ["Severity", data.get("severity", "LOW")],
        ["Correlation", data.get("corr", "0.0000")],
        ["Anomaly Score", str(data.get("anomaly_score", 0))]
    ]
    
    t = Table(summary_data, colWidths=[2 * inch, 3 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0"))
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3 * inch))

    # 3. Expert Recommendations
    story.append(Paragraph("Maintenance Recommendations", header_style))
    insights = data.get("insights", [])
    if isinstance(insights, list):
        for rec in insights:
            story.append(Paragraph(f"• {rec}", styles['Normal']))
    else:
        story.append(Paragraph(f"• {insights}", styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))

    # 4. Features
    story.append(Paragraph("Extracted Features", header_style))
    feat_data = [["Feature", "Value"]]
    features = data.get("features", {})
    for k, v in features.items():
        if isinstance(v, float):
            val = f"{v:.4f}"
        elif isinstance(v, list):
            val = f"{len(v)} points"
        else:
            val = str(v)
        feat_data.append([k.replace("_", " ").title(), val])
        
    ft = Table(feat_data, colWidths=[2.5 * inch, 2.5 * inch])
    ft.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 8)
    ]))
    story.append(ft)

    doc.build(story)
    return output_path
