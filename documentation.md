# 🏛️ Caso Real: Auditoría a un Modelo de Riesgo Crediticio (Scorecard PD)

---

## 1️⃣ Objetivo de la Auditoría

Evaluar si el modelo de scoring crediticio (`v1.4.2`) utilizado para la aprobación de préstamos personales opera de forma precisa, imparcial (sin discriminación por género u edad), segura, conforme a las regulaciones bancarias (Basilea III, NIST AI RMF, ISO 42001) e interpretable.

---

## 2️⃣ Documentación Auditada

Se verifica la presencia de la ficha técnica (*Model Card*):

```python
doc_metadata = {
    "objective": "Predecir la Probabilidad de Incumplimiento (PD) a 12 meses en préstamos personales.",
    "use_cases": "Evaluación automatizada de riesgo en plataforma de crédito digital.",
    "architecture": "Pipeline Scikit-Learn (Imputador + GradientBoostingClassifier).",
    "algorithm": "GradientBoostingClassifier (n_estimators=100, learning_rate=0.08)",
    "version": "v1.4.2",
    "limitations": "Baja representatividad en solicitantes <21 años sin historial crediticio.",
    "owners": "Equipo de Riesgos Cuantitativos y Ciencia de Datos"
}
```

---

## 3️⃣ Auditoría de Datos

Se analizan 1,500 registros de solicitudes de crédito:

- **Calidad:** 35 valores faltantes en `annual_inc` y 15 filas duplicadas.
- **Privacidad / PII:** Se detectó una columna sensible no anonimizada (`ssn`).
- **Balance de clases:** Ratio de morosidad auditado.

---

## 4️⃣ Auditoría del Proceso de Entrenamiento

Se verifica la trazabilidad y reproducibilidad del modelo:

```python
training_config = {
    "split_ratios": {"train": 0.70, "val": 0.0, "test": 0.30},
    "is_stratified": True,  # División estratificada por clase objetivo
    "hyperparameters": {"n_estimators": 100, "learning_rate": 0.08, "random_state": 42},
    "random_seed": 42,      # Semilla aleatoria fija
    "reproducibility_verified": True,
    "model_version": "v1.4.2",
    "git_commit": "a8f3b29"  # Hash de versión en repositorio
}
```

---

## 5️⃣ Evaluación de Rendimiento

Métricas cuantitativas clave en el conjunto de prueba:

- **ROC-AUC:** `0.5209`
- **Gini Coefficient ($2 \times \text{AUC} - 1$):** `0.0419` *(Alerta: $< 0.40$ mínimo en scoring bancario)*
- **Estadística KS (Kolmogorov-Smirnov):** `0.0419` *(Alerta: $< 0.30$ discriminación pobre)*

---

## 6️⃣ Evaluación de Sesgos (Fairness)

Análisis de equidad entre grupos protegidos (`gender` - Hombres vs Mujeres):

- **Disparate Impact Ratio:** `0.00` *(Alerta: Falla la Regla del 80% EEOC)*
- **Demographic Parity Difference:** Evaluada.

---

## 7️⃣ Evaluación de Robustez

Resiliencia del modelo ante perturbaciones en los datos:

- Pruebas de estrés con ruido Gaussiano ($\sigma = 5\%$ y $15\%$) en ingresos y puntaje de crédito (`credit_score`).

---

## 8️⃣ Evaluación de Explicabilidad

Importancia relativa de variables (*Feature Importances*):

1. `credit_score` (Puntaje crediticio)
2. `dti` (Relación deuda-ingreso)
3. `revol_util` (Uso de líneas de crédito)
4. `delinq_2yrs` (Morosidades previas)

---

## 9️⃣ Evaluación de Seguridad

- Control de acceso a artefactos del modelo.
- Verificación de registros de inferencia inmutables (*Audit Log*).

---

## 🔟 Evaluación de Privacidad

- Identificación y recomendación de cifrado o hashing para variables PII (`ssn`).

---

## 11️⃣ Cumplimiento Normativo (Checklist Gobernanza)

- **NIST AI RMF:** Pruebas de estrés y evaluación de riesgos completada.
- **ISO/IEC 42001:** Políticas de gobernanza vigentes.
- **EU AI Act:** Transparencia y derechos de explicabilidad para clientes.

---

## 12️⃣ Pruebas en Producción y Deriva (Data Drift)

- **PSI (Population Stability Index):** Cálculo de deriva en variables numéricas entre baseline y datos de producción.
- **Latencia de respuesta:** `45.2 ms` (Cumple requerimiento de $< 200\text{ ms}$).

---

## 13️⃣ Documentar Hallazgos y Plan de Remediación

Se generaron los reportes de auditoría en los siguientes formatos:

- **Reporte HTML Interactivo:** `credit_risk_modelling_audit_report.html`
- **Resumen Ejecutivo Markdown:** `credit_risk_modelling_audit_report.md`