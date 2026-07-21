# 🛡️ Informe de Auditoría de IA - Credit Risk Modelling (PD Scorecard)

**Puntuación General:** 85.7 / 100  
**Nivel de Riesgo AuditModels:** `LOW`  
**Fecha:** 2026-07-21 16:51:58  

---

## 📝 Alcance y Metodología
- **Alcance:** Auditoría técnica integral de seguridad, cumplimiento, calidad de datos, equidad algorítmica, explicabilidad y deriva en producción para el modelo *Credit Risk Modelling (PD Scorecard)*.
- **Metodología:** Análisis cuantitativo estructurado evaluando las 11 fases de `src/auditmodels/` mapeadas a ISO 42001, NIST AI RMF y EU AI Act.

---

## 📊 Resumen por Fases de Auditoría (`src/auditmodels`)

| Fases Auditadas | Puntuación | Nivel de Riesgo |
| :--- | :---: | :---: |
| **1. Calidad de Datos** (`data_audit`) | 83.1 / 100 | `LOW` |
| **2. Rendimiento Predictivo** (`performance_audit`) | 52.1 / 100 | `HIGH` |
| **3. Equidad y Sesgos** (`fairness_audit`) | 60.0 / 100 | `MEDIUM` |
| **4. Robustez y Estrés** (`robustness_audit`) | 99.6 / 100 | `LOW` |
| **5. Explicabilidad** (`explainability_audit`) | 80.0 / 100 | `LOW` |
| **6. Seguridad** (`security_audit`) | 100.0 / 100 | `LOW` |
| **7. Privacidad** (`privacy_audit`) | 80.0 / 100 | `LOW` |
| **8. Cumplimiento y Gobernanza** (`compliance_audit`) | 85.7 / 100 | `LOW` |
| **9. Documentación** (`documentation_audit`) | 100.0 / 100 | `LOW` |
| **10. Entrenamiento** (`training_audit`) | 100.0 / 100 | `LOW` |
| **11. Producción y Deriva** (`production_audit`) | 100.0 / 100 | `LOW` |

---

## ⚠️ Evidencias y Riesgos Identificados (Alertas)
- ⚠️ Found 3 duplicate rows in dataset
- ⚠️ Potential PII columns identified without explicit anonymization flag: ['ssn']
- ⚠️ Low F1-Score detected (0.000)
- ⚠️ Low Precision detected (0.000)
- ⚠️ Low Recall detected (0.000)
- ⚠️ Low Gini coefficient for credit risk modelling (0.042 < 0.40 threshold)
- ⚠️ Low KS statistic for credit risk modelling (0.042 < 0.30 threshold)
- ⚠️ Fails 80% rule for Disparate Impact (0.000). Selection rate for 'Female' (0.0%) vs 'Male' (0.0%).
- ⚠️ Alta dominancia de una sola característica 'annual_inc' (98.4% de importancia). Riesgo de sesgo por característica única.
- ⚠️ Non-compliant item [MON-01] (ISO/IEC 42001): Is continuous monitoring established for data drift and concept drift in production?
- ⚠️ Protección de Datos: Columnas con PII potencial expuestas en texto plano: ['ssn']

---

## 💡 Explicabilidad (Top Variables Predictivas)
- **Variables principales:** annual_inc, delinq_2yrs, revol_util, credit_score, dti

---

## ⚖️ Métrica de Equidad (Fairness)

- **Disparate Impact Ratio:** `0.0` (Regla del 80%: ❌ NO CUMPLE)
- **Equal Opportunity Difference:** `0.0`
- **Demographic Parity Difference:** `0.0`

---

## 📋 Recomendaciones y Plan de Remediación

### Recomendaciones
- 📌 Limpiar duplicados y registros inconsistentes en los pipelines de ETL.
- 📌 Cifrar/Enmascarar columnas PII detectadas: ['ssn'].
- 📌 Mitigar el sesgo detectado en el modelo mediante re-ponderación de muestras (Reweighing) o post-procesamiento de umbral.

### Plan de Remediación
- 🛠️ ETL/Data Prep: Agregar deduplicación estricta y llaves primarias únicas.
- 🛠️ Seguridad/Privacidad: Implementar hashing SHA-256 o tokenización en variables de identificación personal.
- 🛠️ Modelado/Fairness: Calibrar umbrales de decisión específicos por grupo para cumplir la regla del 80%.

---
*Generado automáticamente por AuditModels Framework v0.1.0*
