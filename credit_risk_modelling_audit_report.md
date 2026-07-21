# 🛡️ Informe de Auditoría de IA - Credit Risk Modelling (PD Scorecard)

**Puntuación General:** 85.7 / 100  
**Nivel de Riesgo AuditModels:** `LOW`  
**Fecha:** 2026-07-21 15:28:49  

---

## 📝 Alcance y Metodología
- **Alcance:** Auditoría técnica integral de seguridad, cumplimiento, calidad de datos, equidad algorítmica y robustez para el modelo *Credit Risk Modelling (PD Scorecard)*.
- **Metodología:** Análisis y cuantificación cuantitativa a través de 10 dimensiones independientes mapeadas a estándares ISO 42001, NIST AI RMF y EU AI Act.

---

## 📊 Resumen de Evaluaciones

| Dimensión Auditada | Puntuación | Nivel de Riesgo |
| :--- | :---: | :---: |
| **Calidad de Datos** | 83.1 / 100 | `LOW` |
| **Rendimiento Predictivo** | 52.1 / 100 | `HIGH` |
| **Equidad y Sesgos (Fairness)** | 60.0 / 100 | `MEDIUM` |
| **Robustez y Perturbaciones** | 99.6 / 100 | `LOW` |
| **Gobernanza y Cumplimiento** | 85.7 / 100 | `LOW` |
| **Seguridad** | 100.0 / 100 | `LOW` |
| **Privacidad** | 80.0 / 100 | `LOW` |

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
