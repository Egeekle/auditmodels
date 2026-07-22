# 🛡️ AuditModels: Framework & Dashboard de Auditoría de Modelos de IA

**AuditModels** es una librería modular y herramienta CLI en Python diseñada para auditar modelos de Inteligencia Artificial y Machine Learning. Permite evaluar si un modelo opera de manera **precisa, segura, ética, robusta, interpretable y conforme a los marcos regulatorios internacionales** (ISO/IEC 42001, NIST AI Risk Management Framework, EU AI Act y Basilea III).

---

## 📋 Metodología de Auditoría en 13 Pasos

El framework estructura el proceso de auditoría cubriendo exhaustivamente los 13 aspectos clave del ciclo de vida del modelo:

| # | Dimensión / Paso | Descripción y Enfoque Técnico | Módulo en `auditmodels` |
|---|---|---|---|
| **1** | **Definición del Objetivo** | Establecer metas de precisión, equidad, seguridad y explicabilidad. | `auditor.py` |
| **2** | **Revisión de Documentación** | Verificar Ficha Técnica (*Model Card*), arquitectura, limitaciones y responsables. | `documentation_audit.py` |
| **3** | **Auditoría de Datos** | Analizar calidad, valores nulos, duplicados, representatividad y PII expuesto. | `data_audit.py` |
| **4** | **Proceso de Entrenamiento** | Revisar división Train/Val/Test, hiperparámetros, versionado (Git/MLflow) y reproducibilidad. | `training_audit.py` |
| **5** | **Evaluación de Rendimiento** | Calcular métricas de Clasificación (ROC-AUC, Gini, KS, F1) o Regresión (MAE, RMSE, $R^2$). | `performance_audit.py` |
| **6** | **Evaluación de Sesgos (Fairness)** | Cuantificar disparidades con la Regla del 80% (Disparate Impact), Paridad Demográfica e Igualdad de Oportunidades. | `fairness_audit.py` |
| **7** | **Evaluación de Robustez** | Pruebas de estrés con ruido Gaussiano e inyección de datos fuera de distribución (OOD). | `robustness_audit.py` |
| **8** | **Evaluación de Explicabilidad** | Extraer importancia de características (*Feature Importances* / Coeficientes) e interpretabilidad. | `explainability_audit.py` |
| **9** | **Evaluación de Seguridad** | Analizar riesgos de extracción del modelo, inversión, inyección de prompts, autenticación y registros (*Audit Logs*). | `security_audit.py` |
| **10** | **Evaluación de Privacidad** | Verificar técnicas de anonimización, riesgos de memorización y políticas de retención. | `privacy_audit.py` |
| **11** | **Cumplimiento Normativo** | Evaluar la conformidad técnica contra **ISO 42001**, **NIST AI RMF** y la **EU AI Act**. | `compliance_audit.py` |
| **12** | **Pruebas en Producción** | Monitorear la deriva de datos (**Data Drift** vía PSI), latencia (ms), tasa de errores y satisfacción del usuario. | `production_audit.py` |
| **13** | **Documentar Hallazgos** | Generar reportes ejecutivos e interactivos en HTML/Markdown con **Plan de Remediación** automatizado. | `reporting.py` |

---

## 📊 Criterios de Categorización de Score y Niveles de Riesgo

`auditmodels` evalúa los modelos asignando un **Score Global (0.0 a 100.0)** ponderado a través de 11 dimensiones técnicas y clasificándolo en 4 Niveles de Riesgo:

- 🟢 **`LOW` (Bajo Riesgo, Score $\ge 80.0$)**: El modelo cumple holgadamente con los estándares de calidad, equidad, gobernanza y seguridad. Apto para producción.
- 🟡 **`MEDIUM` (Riesgo Moderado, $60.0 \le \text{Score} < 80.0$)**: Presenta alertas o desviaciones menores. Apto con monitoreo y plan de remediación.
- 🟠 **`HIGH` (Alto Riesgo, $40.0 \le \text{Score} < 60.0$)**: Deficiencias significativas en seguridad, equidad o privacidad. Requiere remediación obligatoria previa al despliegue.
- 🔴 **`CRITICAL` (Riesgo Crítico, Score $< 40.0$)**: Vulnerabilidades o fallos graves. **No apto para producción**.

> 📖 **Para conocer la desglose detallado de las 11 dimensiones, pesos y fórmulas matemáticas de penalización, consulta:**  
> 👉 [**README_CRITERIOS_SCORE.md**](file:///c:/Users/I13311/Desktop/Projects/auditmodels/README_CRITERIOS_SCORE.md)

---

## 🛠️ Instalación y Requisitos

Requiere **Python `>=3.12`** y la herramienta de gestión de paquetes [uv](https://github.com/astral-sh/uv).

```powershell
# Clonar o situarse en el directorio del proyecto
cd auditmodels

# Sincronizar el entorno virtual e instalar dependencias automáticamente
uv sync
```

---

## 🚀 Explicación Paso a Paso de los Ejemplos

### 1️⃣ Ejemplo 1: Clasificación de Riesgo Crediticio (`examples/audit_credit_risk_modelling.py`)

Este ejemplo demuestra la auditoría completa de un modelo de **Probabilidad de Incumplimiento (PD - Scorecard)** en el sector financiero.

#### 📜 Ejecución del Ejemplo:
```powershell
uv run python examples/audit_credit_risk_modelling.py
```

#### 🔍 Paso a Paso del Proceso Interno:
1. **Generación / Carga del Dataset de Crédito**:
   - Variables financieras: `loan_amount`, `annual_inc`, `dti` (deuda-ingreso), `credit_score`, `delinq_2yrs` (morosidades) y `revol_util`.
   - Atributos demográficos protegidos: `gender` (Hombre/Mujer) y `age_group`.
   - Variable PII: `ssn` (Número de Seguro Social en texto plano).
2. **Entrenamiento del Modelo**:
   - Entrena un `GradientBoostingClassifier` con división 70/30 estratificada y `random_state=42`.
3. **Auditoría con `ModelAuditor`**:
   - **Calidad de Datos**: Identifica nulos en `annual_inc`, filas duplicadas y alerta sobre el campo sensible `ssn`.
   - **Rendimiento Crediticio**: Calcula métricas específicas de scoring bancario:
     - **ROC-AUC**: Capacidad general de discriminación.
     - **Coeficiente de Gini ($2 \times \text{AUC} - 1$)**: Métrica de ordenación de riesgo (alerta si es $< 0.40$).
     - **Estadística KS (Kolmogorov-Smirnov)**: Máxima separación entre clientes solventes e insolventes (alerta si es $< 0.30$).
   - **Evaluación de Equidad (Fairness)**:
     - Calcula la **Regla del 80% (Disparate Impact Ratio)** entre Hombres y Mujeres.
     - Evalúa la diferencia en **Igualdad de Oportunidades (Equal Opportunity)**.
   - **Robustez**: Aplica perturbaciones de ruido ($\sigma=5\%$ y $15\%$) sobre las variables numéricas.
   - **Explicabilidad**: Determina las variables más influyentes (`credit_score`, `dti`, `revol_util`).
   - **Gobernanza y Producción**: Valida requisitos ISO 42001 / NIST AI RMF, calcula **Data Drift (PSI)** y registra latencia (45.2 ms).
4. **Generación de Entregables**:
   - **Reporte HTML Interactivo**: [credit_risk_modelling_audit_report.html](file:///c:/Users/I13311/Desktop/Projects/auditmodels/credit_risk_modelling_audit_report.html)
   - **Resumen Markdown**: [credit_risk_modelling_audit_report.md](file:///c:/Users/I13311/Desktop/Projects/auditmodels/credit_risk_modelling_audit_report.md)

---

### 2️⃣ Ejemplo 2: Regresión de Tasa de Interés (`examples/audit_regression_performance.py`)

Este ejemplo audita un modelo de **Regresión Lineal** que predice la tasa de interés óptima ajustada al riesgo del solicitante.

#### 📜 Ejecución del Ejemplo:
```powershell
uv run python examples/audit_regression_performance.py
```

#### 🔍 Paso a Paso del Proceso Interno:
1. **Preparación de Datos y Modelo de Regresión**:
   - Variables predictoras: `credit_score`, `income`, `loan_amount`.
   - Variable continua objetivo: `interest_rate` (tasa de interés en %).
   - Modelo: `LinearRegression` (OLS).
2. **Evaluación de Métricas de Regresión**:
   - **MAE (Mean Absolute Error)**: Error medio absoluto en puntos porcentuales de tasa.
   - **RMSE (Root Mean Squared Error)**: Raíz del error cuadrático medio.
   - **$R^2$ Score**: Coeficiente de determinación que mide la varianza explicada.
3. **Explicabilidad por Coeficientes**:
   - Analiza la magnitud relativa de los coeficientes (`coef_`) para verificar que el modelo asigna tasas menores a mayores puntajes de crédito.
4. **Cumplimiento y Gobernanza Integrados**:
   - Verifica la Ficha Técnica, políticas de retención de datos, controles de seguridad y estabilidad de datos en producción.
5. **Generación de Entregables**:
   - **Reporte HTML Interactivo**: [regression_model_audit_report.html](file:///c:/Users/I13311/Desktop/Projects/auditmodels/regression_model_audit_report.html)
   - **Resumen Markdown**: [regression_model_audit_report.md](file:///c:/Users/I13311/Desktop/Projects/auditmodels/regression_model_audit_report.md)

---

### 3️⃣ Ejemplo 3: Auditoría desde Línea de Comandos (CLI)

`auditmodels` incluye un comando ejecutable directamente desde la consola:

```powershell
# Ejecución básica sintética desde consola
uv run auditmodels --model-name "Modelo Crediticio CLI"

# Auditoría especificando archivo CSV de datos
uv run auditmodels --data dataset_credito.csv --target default_flag --model-name "Modelo Produccion"
```

---

## 💻 Ejemplo de Uso en Python (API)

```python
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from auditmodels import ModelAuditor

# 1. Cargar datos y modelo
df = pd.read_csv("datos_credito.csv")
model = RandomForestClassifier().fit(X_train, y_train)

# 2. Inicializar auditor
auditor = ModelAuditor(model_name="Modelo de Aprobación de Crédito")

# 3. Ejecutar auditoría integral de 13 pasos
result = auditor.audit(
    df=df,
    y_true=y_test,
    y_pred=model.predict(X_test),
    y_prob=model.predict_proba(X_test)[:, 1],
    problem_type="classification",
    sensitive_column="gender",
    privileged_group="Male",
    unprivileged_group="Female",
    model=model,
    predict_fn=model.predict,
    compliance_answers={"GOV-01": True, "DOC-01": True, "RISK-01": True},
    doc_metadata={
        "objective": "Evaluación de riesgo crediticio",
        "version": "v1.0.0",
        "owners": "Equipo Data Science"
    }
)

# 4. Exportar reportes
result.export_html("reporte_auditoria.html")
result.export_markdown("reporte_auditoria.md")

print(f"Puntuación Global: {result.overall_score}/100 | Riesgo: {result.overall_risk_level}")
```

---

## 🧪 Pruebas Unitarias

El proyecto cuenta con una suite completa de pruebas unitarias que verifican la integridad de cada módulo de auditoría:

```powershell
uv run python -m unittest discover -s tests
```

---

## 📄 Estructura del Proyecto

```
auditmodels/
├── pyproject.toml                     # Configuración del proyecto y dependencias uv
├── README.md                          # Documentación principal del proyecto
├── documentation.md                   # Resumen estructurado del proceso de auditoría
├── src/
│   └── auditmodels/
│       ├── __init__.py                # Exportaciones principales del paquete
│       ├── auditor.py                 # Orquestador principal (ModelAuditor)
│       ├── data_audit.py              # Auditoría de Calidad de Datos y PII (Paso 3 y 10)
│       ├── performance_audit.py       # Rendimiento Clasificación y Regresión (Paso 5)
│       ├── fairness_audit.py          # Sesgos y Equidad Algorítmica (Paso 6)
│       ├── robustness_audit.py        # Pruebas de Estrés y Perturbación (Paso 7)
│       ├── explainability_audit.py    # Explicabilidad e Importancia de Variables (Paso 8)
│       ├── security_audit.py          # Seguridad, Extracción e Inyección (Paso 9)
│       ├── privacy_audit.py           # Privacidad, Anonimización y Retención (Paso 10)
│       ├── compliance_audit.py        # Marcos Regulatorios ISO/NIST/EU AI Act (Paso 11)
│       ├── training_audit.py          # Proceso de Entrenamiento y Trazabilidad (Paso 4)
│       ├── documentation_audit.py     # Ficha Técnica y Documentación (Paso 2)
│       ├── production_audit.py        # Monitoreo Data Drift PSI y Latencia (Paso 12)
│       ├── reporting.py               # Generador de Reportes HTML & MD (Paso 13)
│       └── cli.py                     # Interfaz de Línea de Comandos
├── examples/
│   ├── demo_audit.py                  # Demo básico
│   ├── audit_credit_risk_modelling.py # Ejemplo real completo de Clasificación
│   └── audit_regression_performance.py# Ejemplo real completo de Regresión
└── tests/
    └── test_audit.py                  # Suite de pruebas unitarias
```
