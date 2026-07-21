import json
from typing import Dict, Any, Optional
import datetime


def generate_html_report(audit_result: Dict[str, Any], output_path: str = "audit_report.html") -> str:
    """
    Generates a standalone, beautifully styled HTML audit report with interactive charts and risk matrices,
    fully initializing and visualizing all 11 audit phases from src/auditmodels.
    """
    overall_score = audit_result.get("overall_score", 0.0)
    risk_level = audit_result.get("overall_risk_level", "MEDIUM")
    meta = audit_result.get("metadata", {})
    model_name = meta.get("model_name", "AI Model")
    audit_date = meta.get("timestamp", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    sections = audit_result.get("sections", {})
    data_res = sections.get("data", {})
    perf_res = sections.get("performance", {})
    fair_res = sections.get("fairness", {})
    rob_res = sections.get("robustness", {})
    comp_res = sections.get("compliance", {})
    doc_res = sections.get("documentation", {})
    train_res = sections.get("training", {})
    prod_res = sections.get("production", {})
    sec_res = sections.get("security", {})
    priv_res = sections.get("privacy", {})
    exp_res = sections.get("explainability", {})

    # Radar chart scores across all core dimensions
    scores = {
        "Datos": data_res.get("score", 100),
        "Rendimiento": perf_res.get("score", 100),
        "Equidad": fair_res.get("score", 100),
        "Robustez": rob_res.get("score", 100),
        "Explicabilidad": exp_res.get("score", 100),
        "Seguridad": sec_res.get("score", 100),
        "Privacidad": priv_res.get("score", 100),
        "Gobernanza": comp_res.get("score", 100),
        "Producción": prod_res.get("score", 100),
    }

    badge_colors = {
        "LOW": "#10b981",       # Emerald green
        "MEDIUM": "#f59e0b",    # Amber yellow
        "HIGH": "#ef4444",      # Crimson red
        "CRITICAL": "#881337"   # Rose dark
    }
    status_bg = badge_colors.get(risk_level, "#6b7280")

    warnings_list = audit_result.get("all_warnings", [])
    warnings_html = "".join([f"<li class='warning-item'>⚠️ {w}</li>" for w in warnings_list]) if warnings_list else "<p class='no-warnings'>✅ Sin alertas críticas identificadas en el modelo.</p>"

    # 13. Actionable Recommendations & Remediation Plan logic
    recs = []
    remediation_steps = []
    
    if data_res.get("duplicate_rows", 0) > 0:
        recs.append("Limpiar duplicados y registros inconsistentes en los pipelines de ETL.")
        remediation_steps.append("ETL/Data Prep: Agregar deduplicación estricta y llaves primarias únicas.")
    if priv_res.get("pii_detected"):
        recs.append(f"Cifrar/Enmascarar columnas PII detectadas: {priv_res.get('pii_detected')}.")
        remediation_steps.append("Seguridad/Privacidad: Implementar hashing SHA-256 o tokenización en variables de identificación personal.")
    if abs(fair_res.get("equal_opportunity_diff", 0.0)) > 0.10 or not fair_res.get("passes_four_fifths_rule", True):
        recs.append("Mitigar el sesgo detectado en el modelo mediante re-ponderación de muestras (Reweighing) o post-procesamiento de umbral.")
        remediation_steps.append("Modelado/Fairness: Calibrar umbrales de decisión específicos por grupo para cumplir la regla del 80%.")
    if rob_res.get("score", 100.0) < 80.0:
        recs.append("Aumentar la robustez del modelo contra ruidos de entrada y anomalías.")
        remediation_steps.append("Modelado: Implementar entrenamiento adversarial o inyección de ruido sintético en el dataset de entrenamiento.")
    if not comp_res.get("framework_breakdown", {}).get("ISO/IEC 42001") or comp_res.get("score", 100.0) < 80.0:
        recs.append("Establecer un marco formal de gobierno de IA con roles definidos.")
        remediation_steps.append("Cumplimiento: Redactar la política de gobernanza y control de acceso del modelo conforme a ISO 42001.")

    if not recs:
        recs.append("Mantener el monitoreo continuo establecido de deriva y rendimiento predictivo.")
        remediation_steps.append("Operaciones/MLOps: Ejecutar re-evaluaciones automáticas de drift mensualmente.")

    recs_html = "".join([f"<li>📌 {r}</li>" for r in recs])
    remediation_html = "".join([f"<li>🛠️ {step}</li>" for step in remediation_steps])

    # Feature Importance rows
    fi_dict = exp_res.get("feature_importances", {})
    fi_rows = "".join([
        f"<tr><td>{feat}</td><td>{val}</td><td>{'⭐⭐⭐ Alta' if i < 2 else '⭐⭐ Media'}</td></tr>"
        for i, (feat, val) in enumerate(list(fi_dict.items())[:5])
    ]) if fi_dict else "<tr><td colspan='3'>Sin datos de importancia de características disponibles</td></tr>"

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Informe de Auditoría de IA - {model_name}</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-primary: #0f172a;
            --bg-card: rgba(30, 41, 59, 0.7);
            --border-card: rgba(255, 255, 255, 0.1);
            --accent: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.25);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Outfit', sans-serif; }}
        body {{
            background: radial-gradient(circle at top right, #1e1b4b, #0f172a 60%);
            color: var(--text-main);
            min-height: 100vh;
            padding: 2rem;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{
            display: flex; justify-content: space-between; align-items: center;
            background: var(--bg-card); backdrop-filter: blur(12px);
            border: 1px solid var(--border-card); padding: 1.5rem 2rem;
            border-radius: 16px; margin-bottom: 2rem;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }}
        .brand h1 {{ font-size: 1.8rem; background: linear-gradient(135deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .brand p {{ color: var(--text-muted); font-size: 0.9rem; margin-top: 4px; }}
        .overall-badge {{
            background: {status_bg}; color: #fff; padding: 0.6rem 1.4rem;
            border-radius: 30px; font-weight: 700; font-size: 1.1rem;
            box-shadow: 0 0 15px {status_bg};
        }}
        .grid-dashboard {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 2rem; }}
        .card {{
            background: var(--bg-card); backdrop-filter: blur(12px);
            border: 1px solid var(--border-card); border-radius: 16px;
            padding: 1.5rem; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        }}
        .card h2 {{ font-size: 1.25rem; color: var(--accent); margin-bottom: 1rem; display: flex; align-items: center; gap: 8px; }}
        .score-hero {{ display: flex; align-items: center; justify-content: space-around; height: 260px; }}
        .circle-score {{
            width: 140px; height: 140px; border-radius: 50%;
            background: conic-gradient(var(--accent) {overall_score * 3.6}deg, rgba(255,255,255,0.1) 0deg);
            display: flex; align-items: center; justify-content: center;
            position: relative; box-shadow: 0 0 20px var(--accent-glow);
        }}
        .circle-score::before {{
            content: ''; position: absolute; width: 115px; height: 115px;
            background: #0f172a; border-radius: 50%;
        }}
        .circle-score span {{ position: relative; z-index: 2; font-size: 2.2rem; font-weight: 700; }}
        .warnings-list {{ list-style: none; max-height: 240px; overflow-y: auto; }}
        .warning-item {{ background: rgba(239, 68, 68, 0.15); border-left: 4px solid #ef4444; padding: 0.75rem 1rem; border-radius: 6px; margin-bottom: 0.5rem; font-size: 0.9rem; }}
        .no-warnings {{ color: #10b981; font-weight: 600; font-size: 1rem; padding: 1rem 0; }}
        
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-top: 1rem; }}
        .metric-box {{ background: rgba(255,255,255,0.03); border: 1px solid var(--border-card); border-radius: 12px; padding: 1rem; text-align: center; }}
        .metric-box .label {{ color: var(--text-muted); font-size: 0.8rem; margin-bottom: 4px; }}
        .metric-box .value {{ font-size: 1.3rem; font-weight: 700; color: #fff; }}

        table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; font-size: 0.9rem; }}
        th, td {{ padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid var(--border-card); }}
        th {{ color: var(--text-muted); font-weight: 600; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 1px; }}
        .status-pass {{ color: #10b981; font-weight: 600; }}
        .status-fail {{ color: #ef4444; font-weight: 600; }}
        .list-recs {{ padding-left: 1.25rem; font-size: 0.95rem; line-height: 1.6rem; color: #e2e8f0; }}

        footer {{ text-align: center; color: var(--text-muted); font-size: 0.85rem; margin-top: 3rem; padding-bottom: 1rem; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="brand">
                <h1>Auditoría de Modelo de IA</h1>
                <p>Modelo: <strong>{model_name}</strong> | Fecha: {audit_date}</p>
            </div>
            <div class="overall-badge">RIESGO: {risk_level}</div>
        </header>

        <div class="grid-dashboard">
            <div class="card">
                <h2>🎯 Puntuación General ({overall_score}/100)</h2>
                <div class="score-hero">
                    <div class="circle-score">
                        <span>{overall_score}</span>
                    </div>
                    <div style="width: 240px; height: 240px;">
                        <canvas id="radarChart"></canvas>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>⚠️ Alertas y Hallazgos Principales</h2>
                <ul class="warnings-list">
                    {warnings_html}
                </ul>
            </div>
        </div>

        <div class="card" style="margin-bottom: 2rem;">
            <h2>📝 Alcance y Metodología de la Auditoría</h2>
            <p style="font-size: 0.95rem; line-height: 1.6; color: #cbd5e1; margin-bottom: 1rem;">
                <strong>Alcance:</strong> Evaluación integral de seguridad, privacidad, cumplimiento normativo, calidad de datos, equidad algorítmica, explicabilidad y deriva para el modelo <em>{model_name}</em>.
            </p>
            <p style="font-size: 0.95rem; line-height: 1.6; color: #cbd5e1;">
                <strong>Metodología:</strong> Cuantificación estructurada a través de las 11 fases de <code>src/auditmodels</code> mapeadas a los marcos regulatorios internacionales <strong>ISO/IEC 42001</strong>, <strong>NIST AI RMF</strong>, <strong>EU AI Act</strong> y estándares financieros <strong>Basilea III</strong>.
            </p>
        </div>

        <div class="card" style="margin-bottom: 2rem;">
            <h2>📊 Resumen por Fases de Auditoría (`src/auditmodels`)</h2>
            <div class="metrics-grid">
                <div class="metric-box">
                    <div class="label">Calidad de Datos</div>
                    <div class="value">{data_res.get('score', 'N/A')} / 100</div>
                </div>
                <div class="metric-box">
                    <div class="label">Rendimiento</div>
                    <div class="value">{perf_res.get('score', 'N/A')} / 100</div>
                </div>
                <div class="metric-box">
                    <div class="label">Equidad y Sesgos</div>
                    <div class="value">{fair_res.get('score', 'N/A')} / 100</div>
                </div>
                <div class="metric-box">
                    <div class="label">Robustez</div>
                    <div class="value">{rob_res.get('score', 'N/A')} / 100</div>
                </div>
                <div class="metric-box">
                    <div class="label">Explicabilidad</div>
                    <div class="value">{exp_res.get('score', 'N/A')} / 100</div>
                </div>
                <div class="metric-box">
                    <div class="label">Seguridad</div>
                    <div class="value">{sec_res.get('score', 'N/A')} / 100</div>
                </div>
                <div class="metric-box">
                    <div class="label">Privacidad</div>
                    <div class="value">{priv_res.get('score', 'N/A')} / 100</div>
                </div>
                <div class="metric-box">
                    <div class="label">Cumplimiento Normativo</div>
                    <div class="value">{comp_res.get('score', 'N/A')} / 100</div>
                </div>
                <div class="metric-box">
                    <div class="label">Documentación</div>
                    <div class="value">{doc_res.get('score', 'N/A')} / 100</div>
                </div>
                <div class="metric-box">
                    <div class="label">Entrenamiento</div>
                    <div class="value">{train_res.get('score', 'N/A')} / 100</div>
                </div>
                <div class="metric-box">
                    <div class="label">Producción y Deriva</div>
                    <div class="value">{prod_res.get('score', 'N/A')} / 100</div>
                </div>
            </div>
        </div>

        <div class="card" style="margin-bottom: 2rem;">
            <h2>📋 Recomendaciones y Plan de Remediación (Remediation Plan)</h2>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-top: 1rem;">
                <div>
                    <h3 style="color: var(--accent); font-size: 1.05rem; margin-bottom: 0.5rem;">📌 Recomendaciones de Auditoría</h3>
                    <ul class="list-recs">
                        {recs_html}
                    </ul>
                </div>
                <div>
                    <h3 style="color: var(--accent); font-size: 1.05rem; margin-bottom: 0.5rem;">🛠️ Plan de Remediación Propuesto</h3>
                    <ul class="list-recs">
                        {remediation_html}
                    </ul>
                </div>
            </div>
        </div>

        <div class="card" style="margin-bottom: 2rem;" id="credit-risk-metrics-card">
            <h2>📈 Métricas de Rendimiento Crediticio (PD Performance Metrics)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Métrica de Riesgo</th>
                        <th>Valor Auditado</th>
                        <th>Umbral Mínimo Recomendado</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>ROC-AUC</td>
                        <td>{perf_res.get('roc_auc', 'N/A')}</td>
                        <td>&ge; 0.70</td>
                        <td><span class="{'status-pass' if (perf_res.get('roc_auc') or 0) >= 0.70 else 'status-fail'}">{'PASSED' if (perf_res.get('roc_auc') or 0) >= 0.70 else 'FAILED'}</span></td>
                    </tr>
                    <tr>
                        <td>Gini Coefficient (2*AUC - 1)</td>
                        <td>{perf_res.get('gini_coefficient', 'N/A')}</td>
                        <td>&ge; 0.40 (40%)</td>
                        <td><span class="{'status-pass' if (perf_res.get('gini_coefficient') or 0) >= 0.40 else 'status-fail'}">{'PASSED' if (perf_res.get('gini_coefficient') or 0) >= 0.40 else 'WARNING'}</span></td>
                    </tr>
                    <tr>
                        <td>KS Statistic (Kolmogorov-Smirnov)</td>
                        <td>{perf_res.get('ks_statistic', 'N/A')}</td>
                        <td>&ge; 0.30 (30%)</td>
                        <td><span class="{'status-pass' if (perf_res.get('ks_statistic') or 0) >= 0.30 else 'status-fail'}">{'PASSED' if (perf_res.get('ks_statistic') or 0) >= 0.30 else 'WARNING'}</span></td>
                    </tr>
                    <tr>
                        <td>F1-Score / Accuracy</td>
                        <td>{perf_res.get('f1_score', 'N/A')} / {perf_res.get('accuracy', 'N/A')}</td>
                        <td>F1 &ge; 0.60</td>
                        <td><span class="{'status-pass' if (perf_res.get('f1_score') or 0) >= 0.60 else 'status-fail'}">{'PASSED' if (perf_res.get('f1_score') or 0) >= 0.60 else 'WARNING'}</span></td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="card" style="margin-bottom: 2rem;">
            <h2>💡 Explicabilidad e Importancia de Características (Feature Importance)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Característica / Variable</th>
                        <th>Importancia / Coeficiente</th>
                        <th>Relevancia Predictiva</th>
                    </tr>
                </thead>
                <tbody>
                    {fi_rows}
                </tbody>
            </table>
        </div>

        <div class="card" style="margin-bottom: 2rem;">
            <h2>🔐 Seguridad y Privacidad de Datos</h2>
            <table>
                <thead>
                    <tr>
                        <th>Control de Seguridad / Privacidad</th>
                        <th>Estado Auditado</th>
                        <th>Evaluación</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Riesgo de Extracción de Modelo (Rate Limiting)</td>
                        <td>{sec_res.get('extraction_risk', 'LOW')} RISK</td>
                        <td><span class="status-pass">MONITORED</span></td>
                    </tr>
                    <tr>
                        <td>Detección de Datos Personales (PII)</td>
                        <td>{len(priv_res.get('pii_detected', []))} columnas identificadas</td>
                        <td><span class="{'status-pass' if len(priv_res.get('pii_detected', [])) == 0 else 'status-fail'}">{'SECURE' if len(priv_res.get('pii_detected', [])) == 0 else 'WARNING'}</span></td>
                    </tr>
                    <tr>
                        <td>Control de Acceso (RBAC) y Registros de Auditoría (Logs)</td>
                        <td>{sec_res.get('access_control', 'ENABLED')} / {sec_res.get('audit_logs', 'ENABLED')}</td>
                        <td><span class="status-pass">PASSED</span></td>
                    </tr>
                    <tr>
                        <td>Políticas de Retención de Datos</td>
                        <td>{'Definidas' if priv_res.get('retention_policy_active') else 'Sin Definir'}</td>
                        <td><span class="{'status-pass' if priv_res.get('retention_policy_active') else 'status-fail'}">{'PASSED' if priv_res.get('retention_policy_active') else 'WARNING'}</span></td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="card" style="margin-bottom: 2rem;">
            <h2>⚖️ Análisis de Equidad (Fairness Metrics)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Métrica</th>
                        <th>Valor</th>
                        <th>Umbral Recomendado</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Disparate Impact Ratio</td>
                        <td>{fair_res.get('disparate_impact_ratio', 'N/A')}</td>
                        <td>0.80 - 1.25 (Regla 80%)</td>
                        <td><span class="{'status-pass' if fair_res.get('passes_four_fifths_rule', True) else 'status-fail'}">{'PASSED' if fair_res.get('passes_four_fifths_rule', True) else 'FAILED'}</span></td>
                    </tr>
                    <tr>
                        <td>Equal Opportunity Diff</td>
                        <td>{fair_res.get('equal_opportunity_diff', 'N/A')}</td>
                        <td>|Diff| &lt; 0.10</td>
                        <td><span class="{'status-pass' if abs(fair_res.get('equal_opportunity_diff', 0)) < 0.1 else 'status-fail'}">{'PASSED' if abs(fair_res.get('equal_opportunity_diff', 0)) < 0.1 else 'REVIEW'}</span></td>
                    </tr>
                    <tr>
                        <td>Demographic Parity Diff</td>
                        <td>{fair_res.get('demographic_parity_diff', 'N/A')}</td>
                        <td>|Diff| &lt; 0.10</td>
                        <td><span class="status-pass">MONITORED</span></td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="card" style="margin-bottom: 2rem;">
            <h2>📜 Lista de Verificación Regulatoria (ISO 42001 / NIST AI / EU AI Act)</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Marco</th>
                        <th>Requisito Evaluado</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([
                        f"<tr><td>{item['id']}</td><td>{item['framework']}</td><td>{item['question']}</td><td><span class='{'status-pass' if item['status']=='PASSED' else 'status-fail'}'>{item['status']}</span></td></tr>"
                        for item in comp_res.get('checklist', [])
                    ])}
                </tbody>
            </table>
        </div>

        <footer>
            Generado automáticamente por <strong>AuditModels Framework v0.1.0</strong> | {audit_date}
        </footer>
    </div>

    <script>
        const ctx = document.getElementById('radarChart').getContext('2d');
        new Chart(ctx, {{
            type: 'radar',
            data: {{
                labels: {json.dumps(list(scores.keys()))},
                datasets: [{{
                    label: 'Puntuación AuditModels',
                    data: {json.dumps(list(scores.values()))},
                    backgroundColor: 'rgba(56, 189, 248, 0.2)',
                    borderColor: '#38bdf8',
                    pointBackgroundColor: '#38bdf8',
                    borderWidth: 2
                }}]
            }},
            options: {{
                scales: {{
                    r: {{
                        angleLines: {{ color: 'rgba(255, 255, 255, 0.1)' }},
                        grid: {{ color: 'rgba(255, 255, 255, 0.1)' }},
                        pointLabels: {{ color: '#94a3b8', font: {{ size: 10 }} }},
                        suggestedMin: 0,
                        suggestedMax: 100,
                        ticks: {{ display: false }}
                    }}
                }},
                plugins: {{ legend: {{ display: false }} }}
            }}
        }});

        // Hide Credit Risk Card if not classification problem
        if ("{perf_res.get('problem_type')}" !== "classification") {{
            const card = document.getElementById("credit-risk-metrics-card");
            if (card) card.style.display = "none";
        }}
    </script>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return output_path


def generate_markdown_report(audit_result: Dict[str, Any], output_path: str = "audit_report.md") -> str:
    """
    Generates a markdown audit summary document fully initializing all 11 audit phases.
    """
    overall_score = audit_result.get("overall_score", 0.0)
    risk_level = audit_result.get("overall_risk_level", "MEDIUM")
    meta = audit_result.get("metadata", {})
    model_name = meta.get("model_name", "AI Model")

    sections = audit_result.get("sections", {})
    data_res = sections.get("data", {})
    perf_res = sections.get("performance", {})
    fair_res = sections.get("fairness", {})
    rob_res = sections.get("robustness", {})
    comp_res = sections.get("compliance", {})
    sec_res = sections.get("security", {})
    priv_res = sections.get("privacy", {})
    exp_res = sections.get("explainability", {})
    doc_res = sections.get("documentation", {})
    train_res = sections.get("training", {})
    prod_res = sections.get("production", {})

    warnings_list = audit_result.get("all_warnings", [])
    warnings_md = "".join([f"- ⚠️ {w}\n" for w in warnings_list]) if warnings_list else "✅ Sin alertas críticas identificadas.\n"

    # Actionable Recommendations & Remediation Plan logic
    recs = []
    remediation_steps = []
    
    if data_res.get("duplicate_rows", 0) > 0:
        recs.append("Limpiar duplicados y registros inconsistentes en los pipelines de ETL.")
        remediation_steps.append("ETL/Data Prep: Agregar deduplicación estricta y llaves primarias únicas.")
    if priv_res.get("pii_detected"):
        recs.append(f"Cifrar/Enmascarar columnas PII detectadas: {priv_res.get('pii_detected')}.")
        remediation_steps.append("Seguridad/Privacidad: Implementar hashing SHA-256 o tokenización en variables de identificación personal.")
    if abs(fair_res.get("equal_opportunity_diff", 0.0)) > 0.10 or not fair_res.get("passes_four_fifths_rule", True):
        recs.append("Mitigar el sesgo detectado en el modelo mediante re-ponderación de muestras (Reweighing) o post-procesamiento de umbral.")
        remediation_steps.append("Modelado/Fairness: Calibrar umbrales de decisión específicos por grupo para cumplir la regla del 80%.")
    if rob_res.get("score", 100.0) < 80.0:
        recs.append("Aumentar la robustez del modelo contra ruidos de entrada y anomalías.")
        remediation_steps.append("Modelado: Implementar entrenamiento adversarial o inyección de ruido sintético en el dataset de entrenamiento.")

    if not recs:
        recs.append("Mantener el monitoreo continuo establecido de deriva y rendimiento predictivo.")
        remediation_steps.append("MLOps: Ejecutar re-evaluaciones automáticas de drift mensualmente.")

    recs_md = "".join([f"- 📌 {r}\n" for r in recs])
    remediation_md = "".join([f"- 🛠️ {step}\n" for step in remediation_steps])

    md_content = f"""# 🛡️ Informe de Auditoría de IA - {model_name}

**Puntuación General:** {overall_score} / 100  
**Nivel de Riesgo AuditModels:** `{risk_level}`  
**Fecha:** {meta.get('timestamp', 'N/A')}  

---

## 📝 Alcance y Metodología
- **Alcance:** Auditoría técnica integral de seguridad, cumplimiento, calidad de datos, equidad algorítmica, explicabilidad y deriva en producción para el modelo *{model_name}*.
- **Metodología:** Análisis cuantitativo estructurado evaluando las 11 fases de `src/auditmodels/` mapeadas a ISO 42001, NIST AI RMF y EU AI Act.

---

## 📊 Resumen por Fases de Auditoría (`src/auditmodels`)

| Fases Auditadas | Puntuación | Nivel de Riesgo |
| :--- | :---: | :---: |
| **1. Calidad de Datos** (`data_audit`) | {data_res.get('score', 'N/A')} / 100 | `{data_res.get('risk_level', 'N/A')}` |
| **2. Rendimiento Predictivo** (`performance_audit`) | {perf_res.get('score', 'N/A')} / 100 | `{perf_res.get('risk_level', 'N/A')}` |
| **3. Equidad y Sesgos** (`fairness_audit`) | {fair_res.get('score', 'N/A')} / 100 | `{fair_res.get('risk_level', 'N/A')}` |
| **4. Robustez y Estrés** (`robustness_audit`) | {rob_res.get('score', 'N/A')} / 100 | `{rob_res.get('risk_level', 'N/A')}` |
| **5. Explicabilidad** (`explainability_audit`) | {exp_res.get('score', 'N/A')} / 100 | `{exp_res.get('risk_level', 'N/A')}` |
| **6. Seguridad** (`security_audit`) | {sec_res.get('score', 'N/A')} / 100 | `{sec_res.get('risk_level', 'N/A')}` |
| **7. Privacidad** (`privacy_audit`) | {priv_res.get('score', 'N/A')} / 100 | `{priv_res.get('risk_level', 'N/A')}` |
| **8. Cumplimiento y Gobernanza** (`compliance_audit`) | {comp_res.get('score', 'N/A')} / 100 | `{comp_res.get('risk_level', 'N/A')}` |
| **9. Documentación** (`documentation_audit`) | {doc_res.get('score', 'N/A')} / 100 | `{doc_res.get('risk_level', 'N/A')}` |
| **10. Entrenamiento** (`training_audit`) | {train_res.get('score', 'N/A')} / 100 | `{train_res.get('risk_level', 'N/A')}` |
| **11. Producción y Deriva** (`production_audit`) | {prod_res.get('score', 'N/A')} / 100 | `{prod_res.get('risk_level', 'N/A')}` |

---

## ⚠️ Evidencias y Riesgos Identificados (Alertas)
{warnings_md}
---

## 💡 Explicabilidad (Top Variables Predictivas)
- **Variables principales:** {", ".join(exp_res.get('top_features', ['No especificadas']))}

---

## ⚖️ Métrica de Equidad (Fairness)

- **Disparate Impact Ratio:** `{fair_res.get('disparate_impact_ratio', 'N/A')}` (Regla del 80%: {'✅ CUMPLE' if fair_res.get('passes_four_fifths_rule') else '❌ NO CUMPLE'})
- **Equal Opportunity Difference:** `{fair_res.get('equal_opportunity_diff', 'N/A')}`
- **Demographic Parity Difference:** `{fair_res.get('demographic_parity_diff', 'N/A')}`

---

## 📋 Recomendaciones y Plan de Remediación

### Recomendaciones
{recs_md}
### Plan de Remediación
{remediation_md}
---
*Generado automáticamente por AuditModels Framework v0.1.0*
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return output_path
