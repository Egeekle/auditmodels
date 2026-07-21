# 🛡️ Informe de Auditoría de IA - Credit Risk Modelling (PD Scorecard)

**Puntuación General:** 72.0 / 100  
**Nivel de Riesgo AuditModels:** `MEDIUM`  
**Fecha:** 2026-07-21 10:50:27  

---

## 📊 Resumen de Evaluaciones

| Dimensión Auditada | Puntuación | Nivel de Riesgo |
| :--- | :---: | :---: |
| **Calidad de Datos** | 83.1 / 100 | `LOW` |
| **Rendimiento Predictivo** | 52.1 / 100 | `HIGH` |
| **Equidad y Sesgos (Fairness)** | 60.0 / 100 | `MEDIUM` |
| **Robustez y Perturbaciones** | 99.6 / 100 | `LOW` |
| **Cumplimiento y Gobernanza** | 85.7 / 100 | `LOW` |

---

## ⚠️ Alertas e Indicadores Clave

- ⚠️ Found 3 duplicate rows in dataset
- ⚠️ Potential PII columns identified without explicit anonymization flag: ['ssn']
- ⚠️ Low F1-Score detected (0.000)
- ⚠️ Low Precision detected (0.000)
- ⚠️ Low Recall detected (0.000)
- ⚠️ Low Gini coefficient for credit risk modelling (0.042 < 0.40 threshold)
- ⚠️ Low KS statistic for credit risk modelling (0.042 < 0.30 threshold)
- ⚠️ Fails 80% rule for Disparate Impact (0.000). Selection rate for 'Female' (0.0%) vs 'Male' (0.0%).
- ⚠️ Non-compliant item [MON-01] (ISO/IEC 42001): Is continuous monitoring established for data drift and concept drift in production?


---

## ⚖️ Métrica de Equidad (Fairness)

- **Disparate Impact Ratio:** `0.0` (Regla del 80%: ❌ NO CUMPLE)
- **Equal Opportunity Difference:** `0.0`
- **Demographic Parity Difference:** `0.0`

---
*Generado automáticamente por AuditModels Framework v0.1.0*
