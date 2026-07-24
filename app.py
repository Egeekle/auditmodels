import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(
    page_title="AuditModels | Presentación Interactiva de Resultados",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Design Aesthetics
st.markdown("""
<style>
    /* Main Theme Overrides */
    .stApp {
        background-color: #0e1117;
        color: #e0e6ed;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header Card */
    .hero-container {
        background: linear-gradient(135deg, #1e2640 0%, #0d1527 100%);
        border: 1px solid #2a365c;
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }
    
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #60a5fa 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        color: #94a3b8;
        line-height: 1.5;
    }

    /* Metric Cards */
    .metric-card {
        background: #161e31;
        border: 1px solid #24304f;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        border-color: #3b82f6;
    }
    .metric-val {
        font-size: 2rem;
        font-weight: 700;
        margin: 5px 0;
    }

    /* Badges */
    .badge-low {
        background-color: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid #22c55e;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-medium {
        background-color: rgba(234, 179, 8, 0.15);
        color: #facc15;
        border: 1px solid #eab308;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-high {
        background-color: rgba(249, 115, 22, 0.15);
        color: #fb923c;
        border: 1px solid #f97316;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-critical {
        background-color: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid #ef4444;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }

    /* Alert Items */
    .alert-item {
        background: #1e2538;
        border-left: 4px solid #f59e0b;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 4px;
        font-size: 0.92rem;
    }
</style>
""", unsafe_allow_html=True)

# Data Definition for the 3 Empirical Tests
DIMENSIONS = [
    "Calidad de Datos", "Rendimiento Predictivo", "Equidad y Sesgos",
    "Robustez y Estrés", "Seguridad de la IA", "Privacidad de Datos",
    "Explicabilidad", "Cumplimiento Regulatorio", "Documentación",
    "Proceso Entrenamiento", "Producción y Deriva"
]

WEIGHTS = {
    "Calidad de Datos": 0.10,
    "Rendimiento Predictivo": 0.15,
    "Equidad y Sesgos": 0.10,
    "Robustez y Estrés": 0.10,
    "Seguridad de la IA": 0.10,
    "Privacidad de Datos": 0.15,
    "Explicabilidad": 0.10,
    "Cumplimiento Regulatorio": 0.10,
    "Documentación": 0.05,
    "Proceso Entrenamiento": 0.05,
    "Producción y Deriva": 0.05
}

TEST_DATA = {
    "Prueba 1: Riesgo Crediticio (GBDT)": {
        "score": 100.0,
        "risk_level": "LOW",
        "description": "Modelo Gradient Boosted Decision Tree (PD Scorecard) optimizado para riesgo de crédito.",
        "dimensions": {
            "Calidad de Datos": 84.1,
            "Rendimiento Predictivo": 98.6,
            "Equidad y Sesgos": 97.9,
            "Robustez y Estrés": 100.0,
            "Seguridad de la IA": 100.0,
            "Privacidad de Datos": 80.0,
            "Explicabilidad": 100.0,
            "Cumplimiento Regulatorio": 100.0,
            "Documentación": 100.0,
            "Proceso Entrenamiento": 100.0,
            "Producción y Deriva": 100.0
        },
        "metrics": {
            "ROC-AUC": "0.9862",
            "Coeficiente Gini": "0.9725",
            "Estadística KS": "0.8828",
            "F1-Score": "0.9150",
            "Accuracy": "93.42%",
            "Disparate Impact Ratio": "1.0293 (Pasa Regla 80%)",
            "Equal Opportunity Diff": "0.0159",
            "Data Drift (PSI)": "0.000 (Sin deriva)"
        },
        "alerts": [
            "⚠️ Se identificaron 3 filas duplicadas en el dataset original.",
            "⚠️ Columna PII 'ssn' detectada sin flag explícita de anonimización (Penalización de -20 pts en Privacidad)."
        ],
        "recommendations": [
            "📌 Enmascarar/cifrar con SHA-256 la columna 'ssn' antes de ingerir en el pipeline de producción.",
            "📌 Establecer reglas de deduplicación estricta en el pipeline ETL."
        ]
    },
    "Prueba 2: Regresión Tasa de Interés (OLS)": {
        "score": 100.1,
        "risk_level": "LOW",
        "description": "Modelo de Regresión Lineal Múltiple (OLS) para estimar la tasa de interés óptima en préstamos.",
        "dimensions": {
            "Calidad de Datos": 100.0,
            "Rendimiento Predictivo": 80.8,
            "Equidad y Sesgos": 100.0,
            "Robustez y Estrés": 100.0,
            "Seguridad de la IA": 100.0,
            "Privacidad de Datos": 100.0,
            "Explicabilidad": 80.0,
            "Cumplimiento Regulatorio": 100.0,
            "Documentación": 100.0,
            "Proceso Entrenamiento": 100.0,
            "Producción y Deriva": 100.0
        },
        "metrics": {
            "R² (Determinación)": "0.8076",
            "MAE (Error Abs. Medio)": "0.8039%",
            "RMSE (Error Cuadrático)": "1.0208%",
            "Latencia de Inferencia": "12.4 ms",
            "Disparate Impact Ratio": "N/A (Variable Continua)",
            "Equal Opportunity Diff": "N/A (Sin clases discretas)",
            "Data Drift (PSI)": "0.000 (Estable)"
        },
        "alerts": [
            "⚠️ Leve concentración de importancia en la característica 'dti' (Riesgo de dominancia)."
        ],
        "recommendations": [
            "📌 Monitorear estabilidad de coeficientes ante cambios macroeconómicos.",
            "📌 Mantener esquema de evaluación periódica de residuales."
        ]
    },
    "Prueba 3: Demo Básico (RandomForest Out-of-the-Box)": {
        "score": 66.7,
        "risk_level": "MEDIUM",
        "description": "Modelo RandomForest predeterminado sin gobernanza, sin Ficha Técnica ni controles de seguridad.",
        "dimensions": {
            "Calidad de Datos": 85.0,
            "Rendimiento Predictivo": 100.0,
            "Equidad y Sesgos": 91.2,
            "Robustez y Estrés": 54.4,
            "Seguridad de la IA": 20.0,
            "Privacidad de Datos": 30.0,
            "Explicabilidad": 100.0,
            "Cumplimiento Regulatorio": 71.4,
            "Documentación": 0.0,
            "Proceso Entrenamiento": 0.0,
            "Producción y Deriva": 100.0
        },
        "metrics": {
            "ROC-AUC": "1.0000 (Perfecto en muestra)",
            "Caída de Precisión bajo Ruido": "-22.8% (Alta sensibilidad)",
            "Equal Opportunity Diff": "+0.1457",
            "Model Card Documentada": "NO (0/7 campos)",
            "Semilla Aleatoria Fijada": "NO (No reproducible)",
            "RBAC / Auth API": "NO (Vulnerable)",
            "Rate Limiting": "NO (Riesgo de Inversión)"
        },
        "alerts": [
            "🔴 DOCUMENTACIÓN: 0.0 pts - Ausencia total de Ficha Técnica (Model Card).",
            "🔴 ENTRENAMIENTO: 0.0 pts - Sin registro de train/val split, hiperparámetros ni semilla.",
            "🔴 SEGURIDAD: 20.0 pts - Sin audit logs, rate limiting ni RBAC en API.",
            "🔴 PRIVACIDAD: 30.0 pts - PII 'email' expuesto sin enmascaramiento ni políticas de retención.",
            "🟠 ROBUSTEZ: 54.4 pts - Caída severa del 22.8% de precisión ante perturbación de ruido."
        ],
        "recommendations": [
            "📌 OBLIGATORIO: Completar Ficha Técnica con los 7 campos normativos antes de pase a producción.",
            "📌 OBLIGATORIO: Implementar rate-limiting, RBAC y sanitización de salidas en la API de inferencia.",
            "📌 OBLIGATORIO: Aplicar hashing SHA-256 a datos de entrada con PII.",
            "📌 RECOMENDADO: Entrenar con inyección de ruido o regularización para mejorar la robustez."
        ]
    }
}

# Sidebar Navigation
st.sidebar.title("🛡️ AuditModels Nav")
st.sidebar.markdown("---")

selected_view = st.sidebar.radio(
    "Seleccione Vista:",
    [
        "📊 Resumen Ejecutivo y Comparativo",
        "🧪 Prueba 1: Riesgo Crediticio (GBDT)",
        "🧪 Prueba 2: Regresión Tasa Interés (OLS)",
        "🧪 Prueba 3: Demo Básico (RandomForest)",
        "📘 Explicación de Metodología y Pruebas",
        "⚙️ Simulador Interactivo de Scoring"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("""
**AuditModels Framework v0.1.0**  
Mapeado a estándares:  
• **ISO/IEC 42001** (Gestión IA)  
• **NIST AI RMF** (Riesgo IA)  
• **EU AI Act** (Regulación Europea)
""")

# Helper Functions
def get_risk_badge(level):
    if level == "LOW":
        return '<span class="badge-low">🟢 Riesgo Bajo (LOW)</span>'
    elif level == "MEDIUM":
        return '<span class="badge-medium">🟡 Riesgo Moderado (MEDIUM)</span>'
    elif level == "HIGH":
        return '<span class="badge-high">🟠 Riesgo Alto (HIGH)</span>'
    else:
        return '<span class="badge-critical">🔴 Riesgo Crítico (CRITICAL)</span>'

def create_gauge_chart(score, title):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 18, 'color': '#e0e6ed'}},
        number = {'suffix': " / 100", 'font': {'size': 24, 'color': '#ffffff'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
            'bar': {'color': "#60a5fa" if score >= 80 else ("#facc15" if score >= 60 else "#f87171")},
            'bgcolor': "#1e293b",
            'borderwidth': 2,
            'bordercolor': "#334155",
            'steps': [
                {'range': [0, 40], 'color': 'rgba(239, 68, 68, 0.2)'},
                {'range': [40, 60], 'color': 'rgba(249, 115, 22, 0.2)'},
                {'range': [60, 80], 'color': 'rgba(234, 179, 8, 0.2)'},
                {'range': [80, 100], 'color': 'rgba(34, 197, 94, 0.2)'}
            ],
            'threshold': {
                'line': {'color': "#ffffff", 'width': 3},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=50, b=20),
        height=220
    )
    return fig

# ---------------------------------------------------------
# VIEW 1: RESUMEN EJECUTIVO Y COMPARATIVO
# ---------------------------------------------------------
if selected_view == "📊 Resumen Ejecutivo y Comparativo":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">📊 Dashboard de Resultados Finales - AuditModels</div>
        <div class="hero-subtitle">
            Evaluación integral de modelos de Inteligencia Artificial a través de 11 dimensiones técnicas, 
            mapeadas rigurosamente a ISO/IEC 42001, NIST AI RMF y la EU AI Act.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Top KPI Metrics
    cols = st.columns(3)
    for idx, (tname, tdata) in enumerate(TEST_DATA.items()):
        with cols[idx]:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-weight: 600; font-size: 1.05rem; color: #60a5fa; margin-bottom: 8px;">{tname.split(':')[0]}</div>
                <div class="metric-val">{tdata['score']:.1f} pts</div>
                <div style="margin-top: 6px;">{get_risk_badge(tdata['risk_level'])}</div>
                <div style="font-size: 0.82rem; color: #94a3b8; margin-top: 10px;">{tdata['description']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Radar Chart Comparison
    st.subheader("🎯 Comparación Radar de las 11 Dimensiones de Auditoría")
    
    categories = DIMENSIONS
    fig_radar = go.Figure()

    colors = ['#3b82f6', '#10b981', '#f59e0b']
    for idx, (tname, tdata) in enumerate(TEST_DATA.items()):
        r_values = [tdata["dimensions"][dim] for dim in categories]
        r_values_closed = r_values + [r_values[0]]
        categories_closed = categories + [categories[0]]
        
        fig_radar.add_trace(go.Scatterpolar(
            r=r_values_closed,
            theta=categories_closed,
            fill='toself',
            name=tname,
            line=dict(color=colors[idx], width=2),
            opacity=0.6
        ))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                color="#94a3b8",
                gridcolor="#334155"
            ),
            angularaxis=dict(
                color="#e0e6ed",
                gridcolor="#334155"
            ),
            bgcolor="#161e31"
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e0e6ed', size=11),
        height=520,
        legend=dict(orientation="h", y=-0.15, x=0.1)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Comparative Table
    st.subheader("📋 Tabla Comparativa Detallada por Dimensión (Scores Reales)")

    df_comp = pd.DataFrame({
        "Dimensión": DIMENSIONS,
        "Peso Global": [f"{WEIGHTS[d]*100:.0f}%" for d in DIMENSIONS],
        "Prueba 1 (GBDT Credit)": [f"{TEST_DATA['Prueba 1: Riesgo Crediticio (GBDT)']['dimensions'][d]:.1f} pts" for d in DIMENSIONS],
        "Prueba 2 (OLS Regresion)": [f"{TEST_DATA['Prueba 2: Regresión Tasa de Interés (OLS)']['dimensions'][d]:.1f} pts" for d in DIMENSIONS],
        "Prueba 3 (RandomForest Demo)": [f"{TEST_DATA['Prueba 3: Demo Básico (RandomForest Out-of-the-Box)']['dimensions'][d]:.1f} pts" for d in DIMENSIONS],
    })

    st.dataframe(df_comp, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# VIEW 2, 3, 4: INDIVIDUAL TEST DETAILS
# ---------------------------------------------------------
elif selected_view.startswith("🧪 Prueba"):
    if "Riesgo Crediticio" in selected_view:
        tname = "Prueba 1: Riesgo Crediticio (GBDT)"
    elif "Regresión" in selected_view:
        tname = "Prueba 2: Regresión Tasa de Interés (OLS)"
    else:
        tname = "Prueba 3: Demo Básico (RandomForest Out-of-the-Box)"

    tdata = TEST_DATA[tname]

    st.markdown(f"""
    <div class="hero-container">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div class="hero-title">{tname}</div>
                <div class="hero-subtitle">{tdata['description']}</div>
            </div>
            <div>{get_risk_badge(tdata['risk_level'])}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.plotly_chart(create_gauge_chart(tdata["score"], "Puntuación Global"), use_container_width=True)
        
        st.subheader("📌 Métricas Clave de la Prueba")
        for k, v in tdata["metrics"].items():
            st.markdown(f"**{k}:** `{v}`")

    with col2:
        st.subheader("📊 Desglose de Puntuación por Dimensión")
        df_dim = pd.DataFrame({
            "Dimensión": list(tdata["dimensions"].keys()),
            "Score": list(tdata["dimensions"].values()),
            "Peso": [WEIGHTS[d] for d in tdata["dimensions"].keys()]
        })
        df_dim["Contribución"] = df_dim["Score"] * df_dim["Peso"]

        fig_bar = px.bar(
            df_dim,
            x="Score",
            y="Dimensión",
            orientation='h',
            text=df_dim["Score"].apply(lambda x: f"{x:.1f}"),
            color="Score",
            color_continuous_scale=["#f87171", "#facc15", "#60a5fa", "#4ade80"],
            range_color=[0, 100]
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='#161e31',
            font=dict(color='#e0e6ed'),
            height=380,
            xaxis=dict(range=[0, 105], gridcolor="#334155"),
            yaxis=dict(autorange="reversed", gridcolor="#334155"),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("⚠️ Evidencias y Alertas Detectadas")
        if tdata["alerts"]:
            for alert in tdata["alerts"]:
                st.markdown(f'<div class="alert-item">{alert}</div>', unsafe_allow_html=True)
        else:
            st.success("✅ No se detectaron alertas de riesgo ni vulnerabilidades críticas.")

    with col_b:
        st.subheader("💡 Plan de Remediación y Recomendaciones")
        for rec in tdata["recommendations"]:
            st.markdown(f"- {rec}")

# ---------------------------------------------------------
# VIEW 5: METHODOLOGY & EXPLANATION OF EACH TEST (UPDATED FROM README_CRITERIOS_SCORE.MD)
# ---------------------------------------------------------
elif selected_view == "📘 Explicación de Metodología y Pruebas":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">📘 Metodología de Scoring y Resultados de Pruebas (README_CRITERIOS_SCORE.md)</div>
        <div class="hero-subtitle">
            Explicación detallada de la <b>metodología matemática, fórmulas de ponderación, penalizaciones específicas y umbrales de categorización</b> 
            utilizados por <code>auditmodels</code>, junto a los resultados empíricos reales obtenidos.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("🎯 1. Puntuación Global (`overall_score`) y Niveles de Riesgo")
    st.markdown("""
    El orquestador principal `ModelAuditor` (`src/auditmodels/auditor.py`) calcula la puntuación global (`overall_score`) como un **promedio ponderado** 
    de las 11 dimensiones técnicas de auditoría. Cada dimensión se evalúa en una escala continua de **0.0 a 100.0 puntos**.

    $$\\text{Overall Score} = \\sum_{i=1}^{11} (\\text{Score}_i \\times \\text{Peso}_i)$$
    """)

    st.markdown("### ⚖️ Tabla de Ponderaciones Globales y Módulos Responsables")
    df_weights_tbl = pd.DataFrame({
        "Dimensión de Auditoría": [
            "Privacidad de Datos", "Rendimiento Predictivo", "Calidad de Datos",
            "Equidad y Sesgos (Fairness)", "Robustez y Estrés", "Seguridad de la IA",
            "Explicabilidad", "Cumplimiento Regulatorio", "Documentación",
            "Proceso de Entrenamiento", "Producción y Deriva"
        ],
        "Peso en Score Global": ["15% (0.15)", "15% (0.15)", "10% (0.10)", "10% (0.10)", "10% (0.10)", "10% (0.10)", "10% (0.10)", "10% (0.10)", "5% (0.05)", "5% (0.05)", "5% (0.05)"],
        "Módulo Responsable": [
            "privacy_audit.py", "performance_audit.py", "data_audit.py",
            "fairness_audit.py", "robustness_audit.py", "security_audit.py",
            "explainability_audit.py", "compliance_audit.py", "documentation_audit.py",
            "training_audit.py", "production_audit.py"
        ],
        "Enfoque Principal": [
            "Exposición de PII, memorización y políticas de retención.",
            "Métricas de precisión, ROC-AUC, Gini, KS o R².",
            "Valores faltantes, duplicados, varianza cero y desbalance.",
            "Regla del 80% (Disparate Impact) e Igualdad de Oportunidades.",
            "Resistencia a ruido sintético Gaussiano y perturbaciones.",
            "Extracción de modelo, rate limiting, sanitización y RBAC.",
            "Transparencia de importancias y dominancia de variables.",
            "Conformidad con ISO 42001, NIST AI RMF y EU AI Act.",
            "Integridad y completitud de la Ficha Técnica (Model Card).",
            "División de datos (Train/Val/Test), hiperparámetros y semilla.",
            "Data Drift (PSI), Concept Drift, latencias y tasa de error."
        ]
    })
    st.dataframe(df_weights_tbl, use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🚦 Categorización del Nivel de Riesgo Global (`overall_risk_level`)")

    st.markdown("""
    | Nivel de Riesgo | Rango de Score | Icono | Significado Operativo | Acción Recomendada |
    |---|:---:|:---:|---|---|
    | **`LOW`** | **80.0 – 100.0** | 🟢 | **Bajo Riesgo**: Cumplimiento sólido en precisión, gobernanza, equidad y seguridad. | Apto para despliegue y pase a producción. |
    | **`MEDIUM`** | **60.0 – 79.9** | 🟡 | **Riesgo Moderado**: Desviaciones menores o alertas secundarias en una o más dimensiones. | Apto con monitoreo activo y plan de remediación sugerido. |
    | **`HIGH`** | **40.0 – 59.9** | 🟠 | **Alto Riesgo**: Deficiencias significativas (sesgo moderado, falta de RBAC o PII expuesto). | Requiere remediación obligatoria antes de desplegar. |
    | **`CRITICAL`** | **0.0 – 39.9** | 🔴 | **Riesgo Crítico**: Fallo severo en gobernanza, desbalance extremo o vulnerabilidad crítica. | **No apto para producción**. Suspensión o bloqueo del modelo. |
    """)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🔬 2. Criterios de Evaluación y Penalizaciones Específicas por Dimensión")
    st.markdown("Cada dimensión parte de una puntuación base de **100.0 puntos** y aplica deducciones en función de métricas cuantitativas o respuestas de control:")

    expansions_updated = [
        ("1️⃣ Calidad de Datos (data_audit.py - Base: 100.0 pts)", """
        Evaluación de la salud general del conjunto de datos:
        - **Valores Nulos:** $-\min\left(\%\\text{datos faltantes} \\times 2,\; 30\\right)$ (deducción máxima de 30 pts).
        - **Filas Duplicadas:** $-\\min\\left(\\frac{\\text{duplicados}}{\\text{total filas}} \\times 100 \\times 2, 20\\right)$ (deducción máxima de 20 pts).
        - **Columnas de Varianza Cero (Constantes):** $-5$ pts por cada columna inútil.
        - **PII Expuesto sin Anonimización:** $-15$ pts si detecta nombres de columnas sensibles (`ssn`, `email`, `dni`, `phone`, `credit_card`).
        - **Desbalance Severo de Clases:** $-15$ pts si la proporción de clase mayoritaria a minoritaria es $> 5.0$.
        """),
        ("2️⃣ Rendimiento Predictivo (performance_audit.py - Base: 100.0 pts)", """
        - **Clasificación:**
          - Con probabilidades (`y_prob`): $\\text{Score} = \\text{ROC-AUC} \\times 100$.
          - Sin probabilidades: $\\text{Score} = \\text{F1-Score} \\times 100$.
          - *Métricas Bancarias Adicionales*: Genera advertencias si $\\text{Gini} < 0.40$ o $\\text{Estadística KS} < 0.30$.
        - **Regresión:**
          - $\\text{Score} = \\max(0.0, \\min(100.0, R^2 \\times 100))$.
        """),
        ("3️⃣ Equidad Algorítmica / Fairness (fairness_audit.py - Base: 100.0 pts)", """
        Calcula la disparidad en la tasa de selección y tasa de verdaderos positivos (TPR):
        - **Impacto Dispar (Regla del 80% / EEOC):** $\\text{Penalización DI} = \\min(|1.0 - \\text{Disparate Impact Ratio}| \\times 50, 40)$ (máximo 40 pts).
        - **Igualdad de Oportunidades:** $\\text{Penalización EO} = |\\text{Diferencia en TPR}| \\times 40$.
        - **Fórmula:** $\\text{Score} = \\max(0.0, 100.0 - \\text{Penalización DI} - \\text{Penalización EO})$.
        - *Excepción Crítica*: Si un grupo demográfico no tiene datos, retorna `0.0` y nivel `CRITICAL`.
        """),
        ("4️⃣ Robustez y Estrés (robustness_audit.py - Base: 100.0 pts)", """
        Evalúa la degradación del rendimiento al aplicar ruido Gaussiano ($\sigma = 5\\%$ y $15\\%$):
        - Sea $\\text{max\\_drop\\_pct}$ la mayor caída porcentual de precisión/R² frente al ruido.
        - $\\text{Score} = \\max(0.0, 100.0 - \\text{max\\_drop\\_pct} \\times 2)$.
        """),
        ("5️⃣ Explicabilidad e Interpretabilidad (explainability_audit.py - Base: 100.0 pts)", """
        - **Incapacidad de extraer importancias** (`feature_importances_` o `coef_`): $-40$ pts.
        - **Dominancia Excesiva de una sola característica** ($> 60\\%$ de la importancia total): $-20$ pts (riesgo de sesgo por variable única).
        """),
        ("6️⃣ Seguridad de la IA (security_audit.py - Base: 100.0 pts)", """
        - **Sin Rate Limiting en API:** $-15$ pts (riesgo de extracción del modelo).
        - **Salida de probabilidades con precisión ilimitada:** $-10$ pts.
        - **Sin defensas contra inferencia de membresía:** $-10$ pts.
        - **Modelo Generativo sin sanitización de Prompts:** $-20$ pts.
        - **Robustez $< 70.0\\%$:** $-15$ pts (vulnerabilidad a ataques adversariales).
        - **Sin Control de Acceso (RBAC):** $-15$ pts.
        - **Sin Registros de Auditoría inmutables (Audit Logs):** $-15$ pts.
        """),
        ("7️⃣ Privacidad y Protección de Datos (privacy_audit.py - Base: 100.0 pts)", """
        - **PII detectado en texto plano:** $-20$ pts.
        - **Sin pruebas de riesgo de memorización realizadas:** $-15$ pts.
        - **PII presente sin anonimización activa (hashing/enmascaramiento):** $-20$ pts.
        - **Sin políticas definidas de retención o purga de datos:** $-15$ pts.
        """),
        ("8️⃣ Cumplimiento Regulatorio (compliance_audit.py - Base: 100.0 pts)", """
        Evalúa una lista de verificación estándar contra **ISO/IEC 42001**, **NIST AI RMF** y la **EU AI Act**:
        $$\\text{Score} = \\left(\\frac{\\text{Controles Cumplidos}}{\\text{Total de Controles (7)}}\\right) \\times 100$$
        """),
        ("9️⃣ Documentación (documentation_audit.py - Base: 100.0 pts)", """
        Verifica la presencia y longitud mínima ($> 5$ caracteres) de 7 campos clave de la Ficha Técnica (*Model Card*):
        `objective`, `use_cases`, `architecture`, `algorithm`, `version`, `limitations`, `owners`.
        $$\\text{Score} = \\left(\\frac{\\text{Campos Validados}}{\\text{Total Campos (7)}}\\right) \\times 100$$
        """),
        ("🔟 Proceso de Entrenamiento (training_audit.py - Base: 100.0 pts)", """
        - **Sin proporciones de división (Train/Val/Test):** $-25$ pts.
        - **Sin conjunto de prueba (Test Ratio = 0):** $-20$ pts.
        - **Sin hiperparámetros registrados:** $-20$ pts.
        - **Sin semilla aleatoria (`random_seed`):** $-15$ pts.
        - **Reproducibilidad no verificada:** $-10$ pts.
        - **Sin versionado de código (commit Git o hash MLflow):** $-10$ pts.
        """),
        ("1️⃣1️⃣ Producción y Deriva (production_audit.py - Base: 100.0 pts)", """
        - **Deriva Severa de Datos** ($\\text{PSI} \\ge 0.25$ en variables): $-20$ pts por cada característica con deriva severa.
        - **Deriva de Concepto (Concept Drift)** detectada: $-25$ pts.
        - **Latencia de respuesta $> 200$ ms:** $-10$ pts.
        - **Tasa de error de peticiones $> 1.0\\%$:** $-15$ pts.
        - **Satisfacción del usuario $< 80.0\\%$:** $-10$ pts.
        """)
    ]

    for title, content in expansions_updated:
        with st.expander(title):
            st.markdown(content)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📈 3. Clasificación Sintética Local Dimensional")
    st.markdown("""
    Para cada módulo individual, la categorización de riesgo local se determina según la regla estándar:
    ```python
    risk_level = "LOW" if score >= 80 else ("MEDIUM" if score >= 60 else "HIGH")
    ```
    """)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🧪 4. Resultados Empíricos Obtenidos en las Pruebas del Proyecto")
    st.markdown("""
    Resumen comparativo completo con los **puntajes exactos y la contribución ponderada** calculada para cada una de las 3 pruebas reales:
    """)

    df_empirical_full = pd.DataFrame({
        "Dimensión de Auditoría": [
            "Puntuación Global (Score)", "Nivel de Riesgo Global", "Calidad de Datos",
            "Rendimiento Predictivo", "Equidad y Sesgos (Fairness)", "Robustez y Estrés",
            "Seguridad de la IA", "Privacidad de Datos", "Explicabilidad",
            "Cumplimiento Regulatorio", "Documentación", "Proceso de Entrenamiento",
            "Producción y Deriva"
        ],
        "Peso": ["100%", "—", "10%", "15%", "10%", "10%", "10%", "15%", "10%", "10%", "5%", "5%", "5%"],
        "Prueba 1: Riesgo Crediticio (GBDT)": [
            "100.0 / 100", "🟢 LOW", "84.1 pts (contrib: 8.41 pts)", "98.6 pts (contrib: 14.79 pts)",
            "97.9 pts (contrib: 9.79 pts)", "100.0 pts (contrib: 10.00 pts)", "100.0 pts (contrib: 10.00 pts)",
            "80.0 pts (contrib: 12.00 pts)", "100.0 pts (contrib: 10.00 pts)", "100.0 pts (contrib: 10.00 pts)",
            "100.0 pts (contrib: 5.00 pts)", "100.0 pts (contrib: 5.00 pts)", "100.0 pts (contrib: 5.00 pts)"
        ],
        "Prueba 2: Regresión Tasa Interés (OLS)": [
            "100.1 / 100 (≈100)", "🟢 LOW", "100.0 pts (contrib: 10.00 pts)", "80.8 pts (contrib: 12.12 pts)",
            "100.0 pts (contrib: 10.00 pts)", "100.0 pts (contrib: 10.00 pts)", "100.0 pts (contrib: 10.00 pts)",
            "100.0 pts (contrib: 15.00 pts)", "80.0 pts (contrib: 8.00 pts)", "100.0 pts (contrib: 10.00 pts)",
            "100.0 pts (contrib: 5.00 pts)", "100.0 pts (contrib: 5.00 pts)", "100.0 pts (contrib: 5.00 pts)"
        ],
        "Prueba 3: Demo Básico (RandomForest)": [
            "66.7 / 100", "🟡 MEDIUM", "85.0 pts (contrib: 8.50 pts)", "100.0 pts (contrib: 15.00 pts)",
            "91.2 pts (contrib: 9.12 pts)", "54.4 pts (contrib: 5.44 pts)", "20.0 pts (contrib: 2.00 pts)",
            "30.0 pts (contrib: 4.50 pts)", "100.0 pts (contrib: 10.00 pts)", "71.4 pts (contrib: 7.14 pts)",
            "0.0 pts (contrib: 0.00 pts)", "0.0 pts (contrib: 0.00 pts)", "100.0 pts (contrib: 5.00 pts)"
        ]
    })

    st.dataframe(df_empirical_full, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# VIEW 6: INTERACTIVE AUDIT SIMULATOR
# ---------------------------------------------------------
elif selected_view == "⚙️ Simulador Interactivo de Scoring":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">⚙️ Simulador Interactivo de Score y Riesgo</div>
        <div class="hero-subtitle">
            Ajuste dinámicamente las puntuaciones de cada dimensión para observar cómo impactan en tiempo real 
            la puntuación global ponderada y la clasificación final de riesgo.
        </div>
    </div>
    """, unsafe_allow_html=True)

    sim_scores = {}
    col_sim1, col_sim2 = st.columns([1, 1])

    with col_sim1:
        st.subheader("🎚️ Ajuste de Dimensiones Principales")
        sim_scores["Calidad de Datos"] = st.slider("1. Calidad de Datos (10%)", 0.0, 100.0, 85.0, 1.0)
        sim_scores["Rendimiento Predictivo"] = st.slider("2. Rendimiento Predictivo (15%)", 0.0, 100.0, 90.0, 1.0)
        sim_scores["Equidad y Sesgos"] = st.slider("3. Equidad y Sesgos (10%)", 0.0, 100.0, 80.0, 1.0)
        sim_scores["Robustez y Estrés"] = st.slider("4. Robustez y Estrés (10%)", 0.0, 100.0, 75.0, 1.0)
        sim_scores["Seguridad de la IA"] = st.slider("5. Seguridad de la IA (10%)", 0.0, 100.0, 60.0, 1.0)
        sim_scores["Privacidad de Datos"] = st.slider("6. Privacidad de Datos (15%)", 0.0, 100.0, 70.0, 1.0)

    with col_sim2:
        st.subheader("🎚️ Ajuste de Dimensiones de Gobernanza")
        sim_scores["Explicabilidad"] = st.slider("7. Explicabilidad (10%)", 0.0, 100.0, 85.0, 1.0)
        sim_scores["Cumplimiento Regulatorio"] = st.slider("8. Cumplimiento Regulatorio (10%)", 0.0, 100.0, 80.0, 1.0)
        sim_scores["Documentación"] = st.slider("9. Documentación (5%)", 0.0, 100.0, 50.0, 1.0)
        sim_scores["Proceso Entrenamiento"] = st.slider("10. Proceso de Entrenamiento (5%)", 0.0, 100.0, 50.0, 1.0)
        sim_scores["Producción y Deriva"] = st.slider("11. Producción y Deriva (5%)", 0.0, 100.0, 95.0, 1.0)

    # Calculate overall weighted score
    overall_sim_score = sum(sim_scores[dim] * WEIGHTS[dim] for dim in DIMENSIONS)
    
    if overall_sim_score >= 80.0:
        sim_risk = "LOW"
    elif overall_sim_score >= 60.0:
        sim_risk = "MEDIUM"
    elif overall_sim_score >= 40.0:
        sim_risk = "HIGH"
    else:
        sim_risk = "CRITICAL"

    st.markdown("---")
    st.subheader("📊 Resultado en Tiempo Real de la Simulación")

    res_col1, res_col2 = st.columns([1, 2])

    with res_col1:
        st.plotly_chart(create_gauge_chart(overall_sim_score, "Score Simulado Global"), use_container_width=True)
        st.markdown(f"<div style='text-align:center;'>Nivel de Riesgo Calculado:<br>{get_risk_badge(sim_risk)}</div>", unsafe_allow_html=True)

    with res_col2:
        df_sim = pd.DataFrame({
            "Dimensión": DIMENSIONS,
            "Score": [sim_scores[d] for d in DIMENSIONS],
            "Peso": [WEIGHTS[d] for d in DIMENSIONS]
        })
        df_sim["Contribución Ponderada"] = df_sim["Score"] * df_sim["Peso"]

        fig_sim = px.bar(
            df_sim,
            x="Dimensión",
            y="Contribución Ponderada",
            text=df_sim["Contribución Ponderada"].apply(lambda x: f"{x:.1f} pts"),
            color="Contribución Ponderada",
            color_continuous_scale="Blues",
            title="Contribución Ponderada por Dimensión al Score Global"
        )
        fig_sim.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='#161e31',
            font=dict(color='#e0e6ed'),
            height=320,
            xaxis=dict(tickangle=-45, gridcolor="#334155"),
            yaxis=dict(gridcolor="#334155"),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_sim, use_container_width=True)

# Footer
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.85rem;">
    🛡️ <b>AuditModels Framework v0.1.0</b> | Desarrollado para Auditoría Rigurosa e Interactiva de Modelos IA/ML<br>
    Cumplimiento normativo ISO/IEC 42001 • NIST AI RMF • EU AI Act
</div>
""", unsafe_allow_html=True)
