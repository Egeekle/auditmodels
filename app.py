import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import datetime

from auditmodels.agent import ModelTestingAgent
from auditmodels.auditor import ModelAuditor

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Audit Platform | Plataforma Multi-Actor de Auditoría de IA",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# CUSTOM STYLING & DESIGN SYSTEM
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Main Theme Overrides */
    .stApp {
        background-color: #0e1117;
        color: #e0e6ed;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Header Container */
    .hero-container {
        background: linear-gradient(135deg, #1e2640 0%, #0d1527 100%);
        border: 1px solid #2a365c;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }
    
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(90deg, #60a5fa 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }

    .hero-subtitle {
        font-size: 1.02rem;
        color: #94a3b8;
        line-height: 1.5;
    }

    /* Metric Cards */
    .kpi-card {
        background: #161e31;
        border: 1px solid #24304f;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        border-color: #3b82f6;
    }
    .kpi-val {
        font-size: 1.9rem;
        font-weight: 700;
        color: #ffffff;
        margin: 4px 0;
    }
    .kpi-lbl {
        font-size: 0.82rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-trend {
        font-size: 0.78rem;
        font-weight: 600;
        margin-top: 4px;
    }
    .trend-up { color: #4ade80; }
    .trend-down { color: #f87171; }

    /* Risk Badges */
    .badge-low {
        background-color: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid #22c55e;
        padding: 4px 10px;
        border-radius: 16px;
        font-weight: 600;
        font-size: 0.82rem;
        display: inline-block;
    }
    .badge-medium {
        background-color: rgba(234, 179, 8, 0.15);
        color: #facc15;
        border: 1px solid #eab308;
        padding: 4px 10px;
        border-radius: 16px;
        font-weight: 600;
        font-size: 0.82rem;
        display: inline-block;
    }
    .badge-high {
        background-color: rgba(249, 115, 22, 0.15);
        color: #fb923c;
        border: 1px solid #f97316;
        padding: 4px 10px;
        border-radius: 16px;
        font-weight: 600;
        font-size: 0.82rem;
        display: inline-block;
    }
    .badge-critical {
        background-color: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid #ef4444;
        padding: 4px 10px;
        border-radius: 16px;
        font-weight: 600;
        font-size: 0.82rem;
        display: inline-block;
    }

    /* Content Cards */
    .content-card {
        background: #161b26;
        border: 1px solid #232d42;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 18px;
    }

    /* Step Banner */
    .step-banner {
        background: rgba(59, 130, 246, 0.1);
        border-left: 4px solid #3b82f6;
        padding: 10px 14px;
        border-radius: 4px;
        margin-bottom: 16px;
        font-size: 0.92rem;
    }

    /* Agent Quote Container */
    .agent-quote-box {
        background: #1b2336;
        border: 1px solid #2b3859;
        border-radius: 10px;
        padding: 14px;
        margin-top: 10px;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# INITIALIZE SESSION STATE (REACTIVE MULTI-TENANT STORAGE)
# ---------------------------------------------------------
if "clients" not in st.session_state:
    st.session_state.clients = [
        {"id": "CLI-001", "name": "FinanCorp", "sector": "Banca & Finanzas", "region": "Colombia / LatAm", "contact": "María González", "team": "Riesgo & Data Science", "audit_type": "Auditoría Integral EU AI Act & ISO 42001", "start": "2024-04-01", "end": "2024-05-15"},
        {"id": "CLI-002", "name": "SaludPlus", "sector": "Salud & Seguros", "region": "México", "contact": "Dr. Roberto Silva", "team": "AI Medical Board", "audit_type": "Auditoría de Sesgo y Privacidad", "start": "2024-04-10", "end": "2024-05-30"},
        {"id": "CLI-003", "name": "RetailNext", "sector": "E-Commerce", "region": "Chile", "contact": "Ana Paredes", "team": "Personalization Team", "audit_type": "Auditoría de Trazabilidad", "start": "2024-04-15", "end": "2024-06-01"},
        {"id": "CLI-004", "name": "Seguros Andina", "sector": "Aseguradora", "region": "Perú", "contact": "Carlos Mendoza", "team": "Underwriting Tech", "audit_type": "Auditoría de Gobernanza y Robustez", "start": "2024-03-20", "end": "2024-05-05"},
        {"id": "CLI-005", "name": "EduLearn", "sector": "EdTech", "region": "España", "contact": "Laura Torres", "team": "Adaptive Learning", "audit_type": "Auditoría Inicial de Cumplimiento", "start": "2024-04-20", "end": "2024-06-10"}
    ]

if "audits" not in st.session_state:
    st.session_state.audits = [
        {"id": "AUD-2024-001", "client": "FinanCorp", "model": "CreditScore AI", "risk": "Alto", "status": "En revisión", "progress": 68, "auditor": "María González"},
        {"id": "AUD-2024-002", "client": "SaludPlus", "model": "Diagnóstico IA", "risk": "Alto", "status": "En progreso", "progress": 42, "auditor": "Juan Martínez"},
        {"id": "AUD-2024-003", "client": "RetailNext", "model": "Recomendador IA", "risk": "Medio", "status": "Evidencias", "progress": 58, "auditor": "Laura Torres"},
        {"id": "AUD-2024-004", "client": "Seguros Andina", "model": "FraudeDetect AI", "risk": "Bajo", "status": "Revisión", "progress": 90, "auditor": "Carlos Mendoza"},
        {"id": "AUD-2024-005", "client": "EduLearn", "model": "Tutor IA", "risk": "Medio", "status": "Registro", "progress": 15, "auditor": "Ana Paredes"}
    ]

if "models" not in st.session_state:
    st.session_state.models = [
        {
            "name": "CreditScore AI",
            "client": "FinanCorp",
            "use_case": "Evaluación de scoring crediticio automatizado para préstamos de consumo.",
            "area": "Riesgo de Crédito",
            "provider": "FinanCorp Data Science (In-House)",
            "ai_type": "Modelo de clasificación (GBDT)",
            "status": "Producción",
            "users": "Interno (Analistas de crédito) y Externo (App Banca Móvil)",
            "decisions": "Aprueba, rechaza o escala solicitudes de préstamos hasta $50,000 USD.",
            "data_processed": "Historial crediticio, ingresos, buró de crédito, datos demográficos.",
            "impact": "Alto (Afecta acceso a servicios financieros y datos personales)"
        }
    ]

if "risk_questionnaire" not in st.session_state:
    st.session_state.risk_questionnaire = {
        "decisions_people": True,
        "sensitive_data": True,
        "affects_employment_health": True,
        "generates_client_content": False,
        "no_human_review": True,
        "third_party_models": False,
        "auto_actions": True,
        "calculated_risk": "Alto",
        "priority_dimensions": ["Privacidad", "Sesgo y Equidad", "Supervisión Humana", "Trazabilidad", "Seguridad"]
    }

if "evidences" not in st.session_state:
    st.session_state.evidences = [
        {
            "code": "EV-001",
            "control": "PRV-01 Consentimiento y Base Legal",
            "title": "Documentación del origen de datos y consentimiento PII",
            "dimension": "Privacidad",
            "status": "En revisión",
            "file": "origen_datos_pii.pdf",
            "due_days": "Vence en 2 días",
            "confidence": 72,
            "quote": "La documentación menciona el acuerdo de confidencialidad con el buró de crédito externo, pero no adjunta la política de purga de datos personales.",
            "preliminary_result": "Observada - Evidencia insuficiente sobre políticas de retención."
        },
        {
            "code": "EV-002",
            "control": "TRZ-01 Trazabilidad de Decisiones",
            "title": "Diccionario de datos y linaje del modelo",
            "dimension": "Trazabilidad",
            "status": "Cargada",
            "file": "diccionario_linaje_v2.pdf",
            "due_days": "Hace 2 días",
            "confidence": 88,
            "quote": "Se detalla la canalización de datos desde el Data Lake hasta la matriz de características X_train.",
            "preliminary_result": "Aprobada preliminarmente"
        },
        {
            "code": "EV-003",
            "control": "SES-01 Evaluación de Sesgos de Datos",
            "title": "Evaluación de impacto dispar y equidad demográfica",
            "dimension": "Sesgo y Equidad",
            "status": "Observada",
            "file": "reporte_fairness_2024.pdf",
            "due_days": "Hace 3 días",
            "confidence": 65,
            "quote": "El reporte evalúa la regla del 80% para género, pero omite pruebas sobre grupos de edad avanzada (>60 años).",
            "preliminary_result": "Observada - Falta cobertura en variable proxy edad."
        },
        {
            "code": "EV-004",
            "control": "SEG-02 Robustez y Seguridad del Modelo",
            "title": "Informe de pruebas de pruebas de estrés ante ruido",
            "dimension": "Seguridad",
            "status": "Aprobada",
            "file": "stress_testing_report.pdf",
            "due_days": "Hace 6 días",
            "confidence": 94,
            "quote": "Pruebas de inyección de ruido Gaussiano demuestran degradación menor al 4% en precisión.",
            "preliminary_result": "Aprobada"
        },
        {
            "code": "EV-005",
            "control": "PRV-02 Políticas de Retención",
            "title": "Política de expiración y purga de logs de consulta",
            "dimension": "Privacidad",
            "status": "Pendiente",
            "file": None,
            "due_days": "Vence en 3 días",
            "confidence": 0,
            "quote": "Documento aún no subido por la empresa cliente.",
            "preliminary_result": "Pendiente de carga"
        }
    ]

if "findings" not in st.session_state:
    st.session_state.findings = [
        {
            "id": "HALL-001",
            "severity": "Crítico",
            "title": "Uso de datos sensibles sin política de retención documentada",
            "control": "PRV-01 Consentimiento y base legal",
            "dimension": "Privacidad",
            "status": "Confirmado",
            "date": "28 abr 2024",
            "description": "No se evidencia la base legal para la retención prolongada de datos provenientes del buró de crédito externo.",
            "recommendation": "Implementar política de purga periódica a los 24 meses y cifrado SHA-256 en repositorio de inferencia."
        },
        {
            "id": "HALL-002",
            "severity": "Alto",
            "title": "Sesgo por variable proxy detectado en grupo de edad",
            "control": "SES-01 Evaluación de sesgos",
            "dimension": "Sesgo y Equidad",
            "status": "En revisión",
            "date": "24 abr 2024",
            "description": "La variable 'código postal' muestra alta correlación con el grupo protegido de adultos mayores y puede inducir sesgo indirecto.",
            "recommendation": "Aplicar re-ponderación (Reweighing) o remoción de la característica proxy."
        },
        {
            "id": "HALL-003",
            "severity": "Medio",
            "title": "Falta de pruebas de extracción de modelo en API",
            "control": "SEG-02 Seguridad y Rate-Limiting",
            "dimension": "Seguridad",
            "status": "Confirmado",
            "date": "23 abr 2024",
            "description": "El API devuelve probabilidades de decisión con precisión flotante sin rate limiting activo.",
            "recommendation": "Configurar redondeo de probabilidades a 2 decimales y limitar peticiones a 100 req/min por usuario."
        },
        {
            "id": "HALL-004",
            "severity": "Bajo",
            "title": "Trazabilidad parcial en explicaciones locales",
            "control": "TRZ-01 Registro de decisiones",
            "dimension": "Trazabilidad",
            "status": "En revisión",
            "date": "22 abr 2024",
            "description": "Algunas predicciones de inferencia no guardan el vector SHAP completo de la consulta.",
            "recommendation": "Activar audit trail inmutable en base de datos de inferencia."
        }
    ]

if "remediation_tasks" not in st.session_state:
    st.session_state.remediation_tasks = [
        {"id": "REM-001", "finding": "HALL-001", "action": "Definir e implementar script de purga automatizada de PII a los 24 meses.", "assignee": "María González (Data Ops)", "due": "2024-05-20", "status": "En progreso"},
        {"id": "REM-002", "finding": "HALL-002", "action": "Remover variable proxy 'código postal' y re-entrenar modelo en staging.", "assignee": "Riesgo & Data Science", "due": "2024-05-25", "status": "Pendiente"},
        {"id": "REM-003", "finding": "HALL-003", "action": "Implementar API Gateway con Rate-Limiting y truncation de output.", "assignee": "DevOps / Security", "due": "2024-05-15", "status": "Completado"},
        {"id": "REM-004", "finding": "HALL-004", "action": "Habilitar registro inmutable de valores SHAP en base de datos PostgreSQL.", "assignee": "ML Engineer", "due": "2024-05-30", "status": "Pendiente"}
    ]

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"sender": "agent", "text": "Hola, soy el **Agente IA de Auditoría**. He analizado las 5 evidencias cargadas para FinanCorp (CreditScore AI). He detectado 1 posible brecha en la documentación de Privacidad (EV-001) y 1 hallazgo de sesgo proxy. ¿En qué te puedo ayudar?"}
    ]

# ---------------------------------------------------------
# SIDEBAR ROLE SELECTOR & NAVIGATION
# ---------------------------------------------------------
st.sidebar.image("https://img.icons8.com/isometric-folders/100/shield.png", width=65)
st.sidebar.title("🛡️ AI Audit Platform")
st.sidebar.markdown("---")

current_role = st.sidebar.selectbox(
    "👤 Seleccionar Actor / Rol:",
    ["🏢 Empresa Auditora", "🏢 Empresa Cliente", "👨‍⚖️ Auditor Responsable"]
)

st.sidebar.markdown("---")

# Navigation by Role
if current_role == "🏢 Empresa Auditora":
    nav_option = st.sidebar.radio(
        "Navegación Auditora:",
        [
            "📊 Dashboard Principal",
            "🏢 Clientes",
            "🤖 Modelos Auditados",
            "📋 Auditorías Activas",
            "📁 Repositorio de Evidencias",
            "⚠️ Matriz de Hallazgos",
            "📄 Informes Emitidos",
            "🛠️ Planes de Acción"
        ]
    )
elif current_role == "🏢 Empresa Cliente":
    nav_option = st.sidebar.radio(
        "Navegación Cliente:",
        [
            "👋 Onboarding e Instrucciones",
            "📝 Registro del Modelo IA",
            "🚦 Clasificación Inicial de Riesgo",
            "📤 Carga de Evidencias",
            "💬 Consultas al Agente IA",
            "📈 Mi Plan de Remediación",
            "📄 Informe Final Aceptado"
        ]
    )
else: # 👨‍⚖️ Auditor Responsable
    nav_option = st.sidebar.radio(
        "Navegación Auditor:",
        [
            "📐 Definición del Alcance & Controles",
            "🔍 Análisis Asistido por Agente IA",
            "❓ Solicitudes de Aclaración",
            "✅ Revisión y Validación de Hallazgos",
            "🤝 Registro de Reunión de Cierre",
            "📜 Generación de Informe Final"
        ]
    )

st.sidebar.markdown("---")
st.sidebar.caption("⚡ **AuditModels Engine v0.1.0**")
st.sidebar.caption("Mapeado a ISO 42001 • NIST AI RMF • EU AI Act")

# ---------------------------------------------------------
# HELPER BADGE FUNCTIONS
# ---------------------------------------------------------
def get_risk_badge(level):
    if level in ["Bajo", "LOW"]:
        return '<span class="badge-low">🟢 Riesgo Bajo</span>'
    elif level in ["Medio", "MEDIUM"]:
        return '<span class="badge-medium">🟡 Riesgo Moderado</span>'
    elif level in ["Alto", "HIGH"]:
        return '<span class="badge-high">🟠 Riesgo Alto</span>'
    else:
        return '<span class="badge-critical">🔴 Riesgo Crítico</span>'

def get_status_badge(status):
    if status in ["Aprobada", "Confirmado", "Completado", "Finalizada"]:
        return '<span class="badge-low">✅ ' + status + '</span>'
    elif status in ["En revisión", "En progreso", "Evidencias"]:
        return '<span class="badge-medium">⏳ ' + status + '</span>'
    elif status in ["Observada", "Pendiente"]:
        return '<span class="badge-high">⚠️ ' + status + '</span>'
    else:
        return '<span class="badge-critical">🔴 ' + status + '</span>'

def create_risk_gauge(score, title="Puntaje de Riesgo General"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16, 'color': '#e0e6ed'}},
        number={'suffix': " / 100", 'font': {'size': 22, 'color': '#ffffff'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
            'bar': {'color': "#60a5fa" if score >= 80 else ("#facc15" if score >= 60 else "#f87171")},
            'bgcolor': "#1e293b",
            'borderwidth': 2,
            'bordercolor': "#334155",
            'steps': [
                {'range': [0, 40], 'color': 'rgba(239, 68, 68, 0.25)'},
                {'range': [40, 60], 'color': 'rgba(249, 115, 22, 0.25)'},
                {'range': [60, 80], 'color': 'rgba(234, 179, 8, 0.25)'},
                {'range': [80, 100], 'color': 'rgba(34, 197, 94, 0.25)'}
            ]
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=15, r=15, t=40, b=15),
        height=200
    )
    return fig

# =========================================================
# ROLE 1: EMPRESA AUDITORA VIEWS
# =========================================================
if current_role == "🏢 Empresa Auditora":

    if nav_option == "📊 Dashboard Principal":
        st.markdown("""
        <div class="hero-container">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div class="hero-title">Hola, María González</div>
                    <div class="hero-subtitle">Resumen general de auditorías, empresas clientes y control operativo de IA</div>
                </div>
                <div style="text-align: right;">
                    <span style="font-size:0.85rem; color:#94a3b8;">Plataforma Auditora</span><br>
                    <b>AuditModels Governance Portal</b>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 4 KPI Top Cards
        kpi_cols = st.columns(4)
        with kpi_cols[0]:
            st.markdown("""
            <div class="kpi-card">
                <div class="kpi-lbl">Auditorías Activas</div>
                <div class="kpi-val">24</div>
                <div class="kpi-trend trend-up">↑ 20% vs. mes anterior</div>
            </div>
            """, unsafe_allow_html=True)

        with kpi_cols[1]:
            st.markdown("""
            <div class="kpi-card">
                <div class="kpi-lbl">Riesgos Críticos</div>
                <div class="kpi-val">7</div>
                <div class="kpi-trend trend-down">↑ 16% vs. mes anterior</div>
            </div>
            """, unsafe_allow_html=True)

        with kpi_cols[2]:
            st.markdown("""
            <div class="kpi-card">
                <div class="kpi-lbl">Evidencias Pendientes</div>
                <div class="kpi-val">48</div>
                <div class="kpi-trend trend-up">↓ 8% vs. mes anterior</div>
            </div>
            """, unsafe_allow_html=True)

        with kpi_cols[3]:
            st.markdown("""
            <div class="kpi-card">
                <div class="kpi-lbl">Informes Emitidos</div>
                <div class="kpi-val">15</div>
                <div class="kpi-trend trend-up">↑ 25% vs. mes anterior</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Main Table + Progress Donut
        col_tbl, col_chart = st.columns([2, 1])

        with col_tbl:
            st.subheader("🏢 Clientes y Estado de Auditorías")
            df_audits = pd.DataFrame(st.session_state.audits)
            
            # Format badges for dataframe display
            formatted_df = df_audits.copy()
            st.dataframe(
                formatted_df,
                use_container_width=True,
                column_config={
                    "progress": st.column_config.ProgressColumn(
                        "Avance General",
                        help="Porcentaje de avance en evidencias y revisiones",
                        format="%d%%",
                        min_value=0,
                        max_value=100,
                    )
                },
                hide_index=True
            )

        with col_chart:
            st.subheader("📊 Avance General")
            fig_donut = go.Figure(data=[go.Pie(
                labels=['Completada', 'En progreso', 'Pendiente'],
                values=[50, 36, 14],
                hole=.6,
                marker_colors=['#22c55e', '#3b82f6', '#f59e0b']
            )])
            fig_donut.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e0e6ed'),
                showlegend=True,
                legend=dict(orientation="h", y=-0.1),
                margin=dict(l=10, r=10, t=20, b=20),
                height=260
            )
            st.plotly_chart(fig_donut, use_container_width=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # PASO 1: Creación de la Empresa Cliente
        st.subheader("➕ Paso 1: Registrar Nueva Empresa Cliente")
        with st.expander("📝 Formulario de Alta de Cliente"):
            with st.form("form_create_client"):
                c1, c2 = st.columns(2)
                with c1:
                    new_client_name = st.text_input("Nombre de la Empresa Cliente:", placeholder="Ej. Banco del Norte")
                    new_sector = st.selectbox("Sector de la Empresa:", ["Banca & Finanzas", "Salud & Medicina", "Retail & E-Commerce", "Aseguradora", "Servicios Públicos", "Educación"])
                    new_region = st.text_input("País o Región:", placeholder="Ej. México / LatAm")
                    new_contact = st.text_input("Contacto Principal:", placeholder="Ej. Ana Martínez (Directora de Riesgo)")
                with c2:
                    new_team = st.text_input("Equipo Responsable de IA:", placeholder="Ej. AI & Analytics Board")
                    new_audit_type = st.selectbox("Tipo de Auditoría Contratada:", ["Auditoría Integral EU AI Act & ISO 42001", "Auditoría de Sesgo y Equidad", "Auditoría de Seguridad y Robustez", "Auditoría de Privacidad de Datos"])
                    new_start = st.date_input("Fecha Estimada de Inicio:", datetime.date.today())
                    new_end = st.date_input("Fecha Estimada de Cierre:", datetime.date.today() + datetime.timedelta(days=45))

                btn_create = st.form_submit_button("🚀 Crear Empresa Cliente y Generar Espacio Privado")

                if btn_create and new_client_name:
                    new_id = f"CLI-{len(st.session_state.clients)+1:03d}"
                    st.session_state.clients.append({
                        "id": new_id,
                        "name": new_client_name,
                        "sector": new_sector,
                        "region": new_region,
                        "contact": new_contact,
                        "team": new_team,
                        "audit_type": new_audit_type,
                        "start": str(new_start),
                        "end": str(new_end)
                    })
                    st.session_state.audits.append({
                        "id": f"AUD-2024-{len(st.session_state.audits)+1:03d}",
                        "client": new_client_name,
                        "model": "Pendiente de Registro",
                        "risk": "Por Definir",
                        "status": "Registro",
                        "progress": 5,
                        "auditor": "Por Asignar"
                    })
                    st.success(f"✅ Empresa cliente '{new_client_name}' creada exitosamente. Espacio privado asignado: `{new_id}`.")

    elif nav_option == "🏢 Clientes":
        st.header("🏢 Registro de Empresas Clientes")
        st.dataframe(pd.DataFrame(st.session_state.clients), use_container_width=True, hide_index=True)

    elif nav_option == "🤖 Modelos Auditados":
        st.header("🤖 Portafolio de Sistemas de IA Auditados")
        st.dataframe(pd.DataFrame(st.session_state.models), use_container_width=True, hide_index=True)

    elif nav_option == "📋 Auditorías Activas":
        st.header("📋 Estado de Auditorías en Curso")
        st.dataframe(pd.DataFrame(st.session_state.audits), use_container_width=True, hide_index=True)

    elif nav_option == "📁 Repositorio de Evidencias":
        st.header("📁 Gestión Centralizada de Evidencias")
        st.dataframe(pd.DataFrame(st.session_state.evidences), use_container_width=True, hide_index=True)

    elif nav_option == "⚠️ Matriz de Hallazgos":
        st.header("⚠️ Matriz de Hallazgos y Vulnerabilidades")
        st.dataframe(pd.DataFrame(st.session_state.findings), use_container_width=True, hide_index=True)

    elif nav_option == "📄 Informes Emitidos":
        st.header("📄 Informes de Auditoría Emitidos")
        st.info("Informes listos para descarga en formato PDF, HTML interactivo y Markdown.")

    elif nav_option == "🛠️ Planes de Acción":
        st.header("🛠️ Seguimiento de Remedación")
        st.dataframe(pd.DataFrame(st.session_state.remediation_tasks), use_container_width=True, hide_index=True)

# =========================================================
# ROLE 2: EMPRESA CLIENTE VIEWS
# =========================================================
elif current_role == "🏢 Empresa Cliente":

    # PASO 2: Onboarding del Cliente
    if nav_option == "👋 Onboarding e Instrucciones":
        st.markdown("""
        <div class="hero-container">
            <div class="hero-title">👋 Bienvenido a su Espacio Privado de Auditoría de IA</div>
            <div class="hero-subtitle">
                Este proceso está diseñado para acompañar a su organización en la verificación transparente de seguridad, 
                privacidad y cumplimiento de sus sistemas de Inteligencia Artificial.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="step-banner">
            💡 <b>Objetivo UX:</b> Reducir la sensación de inspección compleja. Este espacio es colaborativo y privado.
        </div>
        """, unsafe_allow_html=True)

        col_onb1, col_onb2 = st.columns(2)
        with col_onb1:
            st.markdown("""
            ### ❓ Lo que debe saber antes de iniciar:
            1. **¿Qué se va a auditar?**  
               Se evaluará el modelo de IA registrado contra los estándares ISO 42001, NIST AI RMF y la regulación EU AI Act.
            2. **¿Qué información se solicitará?**  
               Fichas técnicas, arquitecturas, políticas de privacidad, registros de entrenamiento y pruebas de rendimiento.
            3. **¿Quién tendrá acceso?**  
               Únicamente el equipo de auditores asignado a su espacio privado seguro.
            """)
        with col_onb2:
            st.markdown("""
            ### 🎁 Entregables que recibirá:
            - 📜 **Informe Ejecutivo y Técnico** de Auditoría de IA.
            - 🚦 **Matriz de Riesgo y Hallazgos** validados.
            - 🛠️ **Plan de Remediación Priorizado** paso a paso.
            - 🛡️ **Sello de Verificación y Cumplimiento**.
            """)

        st.markdown("<br>", unsafe_allow_html=True)
        st.button("🚀 Comenzar Auditoría (Registrar Sistema IA)", type="primary", use_container_width=True)

    # PASO 3: Registro del Modelo de IA
    elif nav_option == "📝 Registro del Modelo IA":
        st.markdown("""
        <div class="hero-container">
            <div class="hero-title">📝 Registro del Sistema o Modelo de IA</div>
            <div class="hero-subtitle">Registre la información técnica básica del sistema que será auditado.</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_register_model"):
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                m_name = st.text_input("Nombre del Modelo o Sistema IA:", value="CreditScore AI")
                m_usecase = st.text_area("Caso de Uso Principal:", value="Evaluación de riesgo crediticio para aprobación de préstamos de consumo.")
                m_area = st.text_input("Área Responsable:", value="Gerencia de Riesgo y Analytics")
                m_provider = st.text_input("Proveedor o Modelo Base:", value="Desarrollo In-House (Python / GBDT)")
                m_type = st.selectbox("Tipo de IA:", [
                    "Modelo de clasificación",
                    "Modelo predictivo",
                    "Modelo generativo (LLM)",
                    "Agente de IA",
                    "Sistema de recomendación",
                    "Visión por computadora",
                    "Sistema de toma de decisiones"
                ])
            with col_m2:
                m_status = st.selectbox("Estado del Sistema:", ["Producción", "Piloto", "Desarrollo"])
                m_users = st.selectbox("Usuarios Destino:", ["Internos y Externos", "Solo Internos (Analistas)", "Solo Externos (Clientes)"])
                m_decisions = st.text_area("Decisiones que Apoya o Automatiza:", value="Aprueba o rechaza préstamos de forma automatizada hasta $50k USD.")
                m_data = st.text_area("Datos que Procesa:", value="Historial crediticio, ingresos mensuales, PII básico, comportamiento de pago.")
                m_impact = st.selectbox("Nivel de Impacto Estimado:", ["Alto Impacto (Finanzas / Empleo / Salud)", "Medio Impacto", "Bajo Impacto"])

            btn_reg_model = st.form_submit_button("💾 Guardar y Registrar Sistema IA")
            if btn_reg_model:
                st.session_state.models[0] = {
                    "name": m_name, "client": "FinanCorp", "use_case": m_usecase, "area": m_area,
                    "provider": m_provider, "ai_type": m_type, "status": m_status, "users": m_users,
                    "decisions": m_decisions, "data_processed": m_data, "impact": m_impact
                }
                st.success("✅ Modelo registrado correctamente. Proceda al paso de Clasificación Inicial de Riesgo.")

    # PASO 4: Clasificación Inicial de Riesgo
    elif nav_option == "🚦 Clasificación Inicial de Riesgo":
        st.markdown("""
        <div class="hero-container">
            <div class="hero-title">🚦 Cuestionario de Clasificación Inicial de Riesgo</div>
            <div class="hero-subtitle">Responda a las siguientes preguntas clave para determinar el alcance preliminar de la auditoría.</div>
        </div>
        """, unsafe_allow_html=True)

        q1 = st.checkbox("1. ¿El sistema toma decisiones sobre personas (ej. aprobación de créditos, contratación, selección)?", value=True)
        q2 = st.checkbox("2. ¿Procesa información personal identificable (PII) o sensible (ej. finanzas, salud, biométricos)?", value=True)
        q3 = st.checkbox("3. ¿El resultado puede afectar empleo, educación, salud o acceso a servicios fundamentales?", value=True)
        q4 = st.checkbox("4. ¿Genera contenido directamente para clientes externos sin supervisión previa?", value=False)
        q5 = st.checkbox("5. ¿Opera sin revisión humana directa en tiempo real (autónomo)?", value=True)
        q6 = st.checkbox("6. ¿Utiliza modelos o APIs de terceros (ej. OpenAI, Anthropic, Google Cloud)?", value=False)
        q7 = st.checkbox("7. ¿Puede ejecutar acciones o transacciones automáticamente?", value=True)

        if st.button("📊 Calcular Riesgo Preliminar", type="primary"):
            affirmative_count = sum([q1, q2, q3, q4, q5, q6, q7])
            calculated_risk = "Alto" if affirmative_count >= 3 else ("Medio" if affirmative_count >= 1 else "Bajo")
            
            st.session_state.risk_questionnaire["calculated_risk"] = calculated_risk
            
            st.markdown("<hr>", unsafe_allow_html=True)
            col_r1, col_r2 = st.columns([1, 2])
            with col_r1:
                st.markdown(f"""
                <div class="content-card" style="text-align:center;">
                    <div style="font-size:0.9rem; color:#94a3b8;">Clasificación de Riesgo Preliminar</div>
                    <div style="margin:10px 0;">{get_risk_badge(calculated_risk)}</div>
                    <div style="font-size:0.85rem; color:#94a3b8;">Respuestas afirmativas: {affirmative_count}/7</div>
                </div>
                """, unsafe_allow_html=True)
            with col_r2:
                st.markdown("""
                ### 🎯 Dimensiones Prioritarias Asignadas:
                - 🔒 **Privacidad y Protección de Datos**
                - ⚖️ **Sesgo y Equidad Algorítmica**
                - 👤 **Supervisión Humana y Control**
                - 📜 **Trazabilidad y Linaje**
                - 🛡️ **Seguridad e Inmunidad**
                """)

    # PASO 6: Carga de Evidencias
    elif nav_option == "📤 Carga de Evidencias":
        st.markdown("""
        <div class="hero-container">
            <div class="hero-title">📤 Solicitudes de Evidencias Requeridas</div>
            <div class="hero-subtitle">Cargue los documentos y artefactos solicitados por la plataforma para el análisis de cumplimiento.</div>
        </div>
        """, unsafe_allow_html=True)

        for ev in st.session_state.evidences:
            with st.expander(f"📌 [{ev['code']}] {ev['title']} — Estado: {ev['status']}"):
                col_e1, col_e2 = st.columns([2, 1])
                with col_e1:
                    st.write(f"**Control Asociado:** `{ev['control']}`")
                    st.write(f"**Dimensión:** `{ev['dimension']}`")
                    st.write(f"**Fecha Límite:** `{ev['due_days']}`")
                    if ev['file']:
                        st.success(f"📄 Archivo actual: `{ev['file']}`")
                    else:
                        st.warning("⚠️ Sin archivo adjunto")
                with col_e2:
                    uploaded_f = st.file_uploader(f"Subir evidencia para {ev['code']}:", key=f"up_{ev['code']}")
                    if uploaded_f:
                        ev["file"] = uploaded_f.name
                        ev["status"] = "Cargada"
                        st.success(f"Archivo '{uploaded_f.name}' cargado con éxito.")

    # Consultas al Agente IA
    elif nav_option == "💬 Consultas al Agente IA":
        st.markdown("""
        <div class="hero-container">
            <div class="hero-title">💬 Asistente IA de Auditoría</div>
            <div class="hero-subtitle">Consulte dudas sobre el estado de sus evidencias y recomendaciones con el Agente de Auditoría.</div>
        </div>
        """, unsafe_allow_html=True)

        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["sender"]):
                st.markdown(msg["text"])

        user_input = st.chat_input("Escriba su consulta para el Agente IA...")
        if user_input:
            st.session_state.chat_messages.append({"sender": "user", "text": user_input})
            # Simulated Agent Response
            response_text = f"🤖 **Agente IA:** He revisado su consulta sobre *'{user_input}'*. Basado en las evidencias cargadas para **CreditScore AI**, le sugiero verificar la sección de Políticas de Privacidad (EV-001) donde se requiere especificar el periodo de retención de PII."
            st.session_state.chat_messages.append({"sender": "agent", "text": response_text})
            st.rerun()

    # PASO 12: Plan de Remediación
    elif nav_option == "📈 Mi Plan de Remediación":
        st.markdown("""
        <div class="hero-container">
            <div class="hero-title">📈 Plan de Remediación y Seguimiento</div>
            <div class="hero-subtitle">Seguimiento interactivo de acciones correctivas para el cierre de hallazgos.</div>
        </div>
        """, unsafe_allow_html=True)

        st.dataframe(pd.DataFrame(st.session_state.remediation_tasks), use_container_width=True, hide_index=True)

    elif nav_option == "📄 Informe Final Aceptado":
        st.header("📄 Informe Final de Auditoría de IA")
        st.success("✅ Su informe final ha sido validado y emitido por el Auditor Responsable.")

# =========================================================
# ROLE 3: AUDITOR RESPONSABLE VIEWS
# =========================================================
else:

    # PASO 5: Definición del Alcance
    if nav_option == "📐 Definición del Alcance & Controles":
        st.markdown("""
        <div class="hero-container">
            <div class="hero-title">📐 PASO 5: Definición del Alcance y Configuración de Auditoría</div>
            <div class="hero-subtitle">Configure el marco normativo, dimensiones aplicables y controles obligatorios para el modelo.</div>
        </div>
        """, unsafe_allow_html=True)

        c_a1, c_a2 = st.columns(2)
        with c_a1:
            st.selectbox("Marco Normativo de Auditoría:", ["ISO/IEC 42001 + EU AI Act", "NIST AI RMF", "Regulación Local Financiera"])
            st.multiselect("Dimensiones Aplicables:", [
                "Gobernanza", "Datos y Privacidad", "Desempeño del Modelo",
                "Sesgo y Equidad", "Explicabilidad", "Seguridad", "Supervisión Humana", "Trazabilidad"
            ], default=["Gobernanza", "Datos y Privacidad", "Desempeño del Modelo", "Sesgo y Equidad", "Seguridad"])
        with c_a2:
            st.text_input("Periodo Analizado:", value="Q1 2024 (Enero - Marzo 2024)")
            st.text_input("Auditor Lider Asignado:", value="María González")

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📋 Controles Aplicables Seleccionados (12)")
        
        df_controls = pd.DataFrame([
            {"Código": "PRV-01", "Control": "Consentimiento y Base Legal", "Dimensión": "Privacidad", "Estado": "En evaluación"},
            {"Código": "PRV-02", "Control": "Políticas de Retención de PII", "Dimensión": "Privacidad", "Estado": "Pendiente"},
            {"Código": "SES-01", "Control": "Evaluación de Sesgos de Datos", "Dimensión": "Sesgo y Equidad", "Estado": "En evaluación"},
            {"Código": "SEG-02", "Control": "Robustez y Seguridad del Modelo", "Dimensión": "Seguridad", "Estado": "Aprobado"},
            {"Código": "TRZ-01", "Control": "Trazabilidad de Decisiones", "Dimensión": "Trazabilidad", "Estado": "Pendiente"},
            {"Código": "GOB-01", "Control": "Ficha Técnica Documentada", "Dimensión": "Gobernanza", "Estado": "En evaluación"}
        ])
        st.dataframe(df_controls, use_container_width=True, hide_index=True)

    # PASO 7: Análisis Asistido por Agente IA
    elif nav_option == "🔍 Análisis Asistido por Agente IA":
        st.markdown("""
        <div class="hero-container">
            <div class="hero-title">🔍 PASO 7: Análisis Asistido por Agente IA (`ModelTestingAgent`)</div>
            <div class="hero-subtitle">Análisis documental automático con citas de evidencia, cálculo de confianza % y detección de hallazgos.</div>
        </div>
        """, unsafe_allow_html=True)

        col_ev_list, col_agent_view = st.columns([1, 2])

        with col_ev_list:
            st.subheader("Solicitudes de Evidencias")
            selected_ev_code = st.radio("Seleccionar Evidencia a Inspeccionar:", [ev["code"] + " - " + ev["title"] for ev in st.session_state.evidences])
            ev_code = selected_ev_code.split(" ")[0]
            curr_ev = [ev for ev in st.session_state.evidences if ev["code"] == ev_code][0]

        with col_agent_view:
            st.subheader(f"✨ Análisis del Agente IA para {curr_ev['code']}")
            
            st.markdown(f"**Control Evaluado:** `{curr_ev['control']}`")
            st.markdown(f"**Evidencia Usada:** `{curr_ev['file'] or 'Sin archivo'}`")

            st.markdown(f"""
            <div class="agent-quote-box">
                <b>📌 Cita Textual de la Evidencia Analizada:</b><br>
                <i>"{curr_ev['quote']}"</i>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"**Resultado Preliminar de la IA:** {curr_ev['preliminary_result']}")
            st.progress(curr_ev['confidence'] / 100.0)
            st.caption(f"🎯 **Nivel de Confianza del Análisis:** {curr_ev['confidence']}%")

            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("### 🤖 Chat Directo con el Agente de Análisis Documental")
            q_agent = st.text_input("Preguntar al Agente sobre esta evidencia:", value="¿Cuál es el principal problema detectado en esta evidencia?")
            if st.button("Enviar Consulta al Agente"):
                st.info(f"🤖 **Respuesta del Agente:** He detectado una posible brecha en la documentación. El archivo `{curr_ev['file']}` menciona el acuerdo con el buró externo pero carece de la clausula explícita de purga de PII.")

    # PASO 8: Solicitudes de Aclaración
    elif nav_option == "❓ Solicitudes de Aclaración":
        st.markdown("""
        <div class="hero-container">
            <div class="hero-title">❓ PASO 8: Solicitudes de Aclaración al Cliente</div>
            <div class="hero-subtitle">Envíe preguntas directas al cliente sin salir de la plataforma.</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_aclaracion"):
            st.selectbox("Evidencia o Control Afectado:", [ev["code"] + " - " + ev["title"] for ev in st.session_state.evidences])
            aclaracion_text = st.text_area("Pregunta / Observación para la Empresa Cliente:", value="No se encontró evidencia sobre el procedimiento utilizado para responder ante resultados incorrectos del modelo. Adjunte el protocolo o indique si todavía no existe.")
            st.form_submit_button("📤 Enviar Solicitud de Aclaración al Cliente")

    # PASO 9: Revisión y Validación de Hallazgos
    elif nav_option == "✅ Revisión y Validación de Hallazgos":
        st.markdown("""
        <div class="hero-container">
            <div class="hero-title">✅ PASO 9: Validación Humana de Hallazgos</div>
            <div class="hero-subtitle">El agente propone hallazgos, pero el Auditor Responsable los valida, confirma o descarta.</div>
        </div>
        """, unsafe_allow_html=True)

        for find in st.session_state.findings:
            with st.expander(f"⚠️ [{find['id']}] {find['title']} — Severidad: {find['severity']} | Estado: {find['status']}"):
                col_f1, col_f2 = st.columns([2, 1])
                with col_f1:
                    st.write(f"**Dimensión:** `{find['dimension']}`")
                    st.write(f"**Control Evaluado:** `{find['control']}`")
                    st.write(f"**Descripción:** {find['description']}")
                    st.write(f"**Recomendación:** {find['recommendation']}")
                with col_f2:
                    new_status = st.selectbox(f"Acción del Auditor ({find['id']}):", ["Propuesto por IA", "En revisión", "Confirmado", "Descartado", "Aceptado por Cliente"], index=["Propuesto por IA", "En revisión", "Confirmado", "Descartado", "Aceptado por Cliente"].index(find['status']) if find['status'] in ["Propuesto por IA", "En revisión", "Confirmado", "Descartado", "Aceptado por Cliente"] else 2)
                    auditor_comment = st.text_area(f"Comentario del Auditor ({find['id']}):", value="Hallazgo verificado contra evidencias EV-001 y logs de inferencia.")
                    if st.button(f"💾 Actualizar Hallazgo {find['id']}"):
                        find["status"] = new_status
                        st.success(f"Hallazgo {find['id']} actualizado a '{new_status}'.")

    # PASO 10: Registro de Reunión de Cierre
    elif nav_option == "🤝 Registro de Reunión de Cierre":
        st.markdown("""
        <div class="hero-container">
            <div class="hero-title">🤝 PASO 10: Registro de Reunión de Cierre</div>
            <div class="hero-subtitle">Documénte acuerdos, observaciones del cliente y fechas de compromiso antes de emitir el informe.</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_closing_meeting"):
            st.text_area("Acuerdos Principales de la Reunión:", value="La empresa cliente FinanCorp acepta los hallazgos HALL-001 y HALL-003 y se compromete a implementar el script de purga de PII antes del 20 de mayo.")
            st.text_area("Riesgos Aceptados por el Cliente:", value="Se acepta temporalmente el riesgo moderado en explicaciones locales (HALL-004) durante el periodo de migración.")
            st.date_input("Fecha de Compromiso de Cierre:", datetime.date.today() + datetime.timedelta(days=30))
            st.form_submit_button("💾 Guardar Acta de Reunión de Cierre")

    # PASO 11: Generación de Informe Final
    elif nav_option == "📜 Generación de Informe Final":
        st.markdown("""
        <div class="hero-container">
            <div class="hero-title">📜 PASO 11: Emisión del Informe Final de Auditoría</div>
            <div class="hero-subtitle">Generación del informe consolidado con velocímetro de score, matriz de hallazgos y plan de remediación.</div>
        </div>
        """, unsafe_allow_html=True)

        col_inf1, col_inf2 = st.columns([1, 2])

        with col_inf1:
            st.plotly_chart(create_risk_gauge(72.0, "Puntaje de Riesgo General"), use_container_width=True)
            st.markdown("<div style='text-align:center;'>Nivel de Riesgo AuditModels:<br><span class='badge-medium'>🟡 Riesgo Moderado (72/100)</span></div>", unsafe_allow_html=True)

        with col_inf2:
            st.subheader("📋 Resumen del Informe Final")
            st.write("**Sistema Auditado:** CreditScore AI (FinanCorp)")
            st.write("**Controles Evaluados:** 12 Controles en 5 Dimensiones")
            st.write("**Hallazgos Confirmados:** 1 Crítico, 1 Alto, 1 Medio, 1 Bajo")
            st.write("**Plan de Remediación:** 4 Acciones programadas (35% completado)")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Emitir y Firmar Informe Final de Auditoría", type="primary", use_container_width=True):
                st.success("✅ Informe Final emitido y notificado a la Empresa Cliente.")

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.85rem;">
    🛡️ <b>AuditModels Platform v0.1.0</b> | Plataforma Multi-Actor de Auditoría de Inteligencia Artificial<br>
    Cumplimiento normativo ISO/IEC 42001 • NIST AI RMF • EU AI Act
</div>
""", unsafe_allow_html=True)
