import os
from pathlib import Path
from typing import Dict, Any
from jinja2 import Template

REPORTS_DIR = Path(__file__).resolve().parent.parent.parent / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

HTML_REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SatQuery AI Dossier - {{ job_id }}</title>
    <style>
        @page { size: A4; margin: 20mm; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #0c1017;
            color: #e6edf3;
            margin: 0;
            padding: 24px;
            line-height: 1.5;
        }
        .container { max-width: 960px; margin: 0 auto; }
        .header {
            border-bottom: 2px solid #30363d;
            padding-bottom: 16px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }
        .logo { font-size: 24px; font-weight: 800; color: #58a6ff; letter-spacing: -0.5px; }
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }
        .badge-cyan { background-color: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid #38bdf8; }
        .badge-green { background-color: rgba(52, 211, 153, 0.15); color: #34d399; border: 1px solid #34d399; }
        .card {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        h2 { font-size: 16px; text-transform: uppercase; color: #8b949e; margin-top: 0; margin-bottom: 12px; }
        .query-box { font-size: 18px; font-weight: 600; color: #ffffff; }
        .answer-box { font-size: 16px; color: #e6edf3; margin-top: 8px; line-height: 1.6; }
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
        .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
        .stat-card {
            background-color: #0d1117;
            border: 1px solid #30363d;
            padding: 12px 16px;
            border-radius: 6px;
        }
        .stat-label { font-size: 12px; color: #8b949e; }
        .stat-value { font-size: 20px; font-weight: 700; color: #58a6ff; margin-top: 4px; }
        .trace-table { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 8px; }
        .trace-table th, .trace-table td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #21262d; }
        .trace-table th { color: #8b949e; font-weight: 600; }
        .evidence-img { width: 100%; border-radius: 6px; border: 1px solid #30363d; max-height: 400px; object-fit: contain; background: #000; }
        .footer { margin-top: 40px; font-size: 12px; color: #8b949e; text-align: center; border-top: 1px solid #21262d; padding-top: 16px; }
        @media print {
            body { background: #ffffff; color: #000000; }
            .card, .stat-card { background: #f6f8fa; border-color: #d0d7de; }
            .logo { color: #0969da; }
            .query-box, .answer-box { color: #000000; }
            .stat-value { color: #0969da; }
            .trace-table th, .trace-table td { border-color: #d0d7de; color: #000; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <div class="logo">SATQUERY AI</div>
                <div style="font-size: 13px; color: #8b949e; margin-top: 4px;">Multimodal Remote Sensing Vision-Language Dossier</div>
            </div>
            <div style="text-align: right;">
                <span class="badge badge-cyan">{{ detected_task }}</span>
                <div style="font-size: 12px; color: #8b949e; margin-top: 6px;">Job ID: {{ job_id }}</div>
            </div>
        </div>

        <div class="card">
            <h2>User Query & Grounded Answer</h2>
            <div class="query-box">“{{ query }}”</div>
            <div class="answer-box">{{ answer }}</div>
        </div>

        <div class="grid-3" style="margin-bottom: 20px;">
            <div class="stat-card">
                <div class="stat-label">Aggregated Confidence</div>
                <div class="stat-value">{{ (confidence.final_confidence * 100)|int }}%</div>
                <div style="font-size: 11px; color: #34d399; margin-top: 2px;">{{ confidence.confidence_level }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Selected Specialists</div>
                <div class="stat-value" style="font-size: 16px; color: #e6edf3;">{{ selected_models|join(", ") }}</div>
                <div style="font-size: 11px; color: #8b949e; margin-top: 2px;">Autonomous Tool Selection</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Execution Latency</div>
                <div class="stat-value">{{ total_execution_time_ms|round(1) }} ms</div>
                <div style="font-size: 11px; color: #8b949e; margin-top: 2px;">Total pipeline latency</div>
            </div>
        </div>

        {% if evidence.change_percentage is not none %}
        <div class="card">
            <h2>Bi-Temporal Change Statistics</h2>
            <div class="grid-2">
                <div class="stat-card">
                    <div class="stat-label">Total Surface Transformation</div>
                    <div class="stat-value">+{{ evidence.change_percentage }}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Demarcated Clusters</div>
                    <div class="stat-value">{{ evidence.changed_regions_count or 0 }} regions</div>
                </div>
            </div>
        </div>
        {% endif %}

        <div class="card">
            <h2>Visual & Spatial Evidence</h2>
            <p style="font-size: 14px; color: #8b949e; margin-bottom: 16px;">{{ evidence.textual_evidence }}</p>
            {% if evidence.overlay_url %}
            <div style="margin-top: 12px;">
                <img class="evidence-img" src="{{ evidence.overlay_url }}" alt="Evidence Overlay" />
            </div>
            {% endif %}
        </div>

        <div class="card">
            <h2>Confidence Metric Decomposition</h2>
            <table class="trace-table">
                <thead>
                    <tr>
                        <th>Metric Dimension</th>
                        <th>Score</th>
                        <th>Significance</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Specialist Model Score</td>
                        <td>{{ confidence.model_confidence }}</td>
                        <td>Inference probability distribution</td>
                    </tr>
                    <tr>
                        <td>Input Compatibility</td>
                        <td>{{ confidence.input_compatibility }}</td>
                        <td>CRS & Geographic spatial overlap validation</td>
                    </tr>
                    <tr>
                        <td>Evidence Strength</td>
                        <td>{{ confidence.evidence_strength }}</td>
                        <td>Localized contours, segmentations & bounding boxes</td>
                    </tr>
                    <tr>
                        <td>Answer Consistency</td>
                        <td>{{ confidence.answer_consistency }}</td>
                        <td>Cross-modality contextual verification</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="card">
            <h2>Auditable Execution Trace</h2>
            <table class="trace-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Pipeline Stage</th>
                        <th>Status</th>
                        <th>Details</th>
                        <th>Latency</th>
                    </tr>
                </thead>
                <tbody>
                    {% for step in execution_trace %}
                    <tr>
                        <td>{{ step.step_number }}</td>
                        <td style="font-weight: 600;">{{ step.name }}</td>
                        <td><span style="color: #34d399;">✓ {{ step.status }}</span></td>
                        <td>{{ step.details }}</td>
                        <td>{{ step.duration_ms|round(1) }}ms</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="footer">
            Generated autonomously by SatQuery AI Platform — Earth Observation Vision-Language Intelligence System
        </div>
    </div>
</body>
</html>
"""

def generate_html_report(result_data: Dict[str, Any]) -> str:
    """Renders self-contained scientific report HTML and writes to static reports directory."""
    job_id = result_data["job_id"]
    report_fn = f"report_{job_id}.html"
    report_path = REPORTS_DIR / report_fn

    template = Template(HTML_REPORT_TEMPLATE)
    html_content = template.render(**result_data)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return f"/reports/{report_fn}"
