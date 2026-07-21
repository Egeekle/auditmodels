# 🛡️ Informe de Auditoría de IA - Modelo de Riesgo Crediticio - Banco Demo

**Puntuación General:** 85.8 / 100  
**Nivel de Riesgo AuditModels:** `LOW`  
**Fecha:** 2026-07-21 10:26:52  

---

## 📊 Resumen de Evaluaciones

| Dimensión Auditada | Puntuación | Nivel de Riesgo |
| :--- | :---: | :---: |
| **Calidad de Datos** | 83.0 / 100 | `LOW` |
| **Rendimiento Predictivo** | 89.5 / 100 | `LOW` |
| **Equidad y Sesgos (Fairness)** | 90.0 / 100 | `LOW` |
| **Robustez y Perturbaciones** | 90.6 / 100 | `LOW` |
| **Cumplimiento y Gobernanza** | 71.4 / 100 | `MEDIUM` |

---

## ⚠️ Alertas e Indicadores Clave

- ⚠️ Found 1 duplicate rows in dataset
- ⚠️ Potential PII columns identified without explicit anonymization flag: ['email']
- ⚠️ Significant Equal Opportunity Difference (+0.146). TPR for unprivileged: 1.000, privileged: 0.854.
- ⚠️ Non-compliant item [SEC-01] (NIST AI RMF): Are access control logs and audit trails maintained for model inference and training data?
- ⚠️ Non-compliant item [MON-01] (ISO/IEC 42001): Is continuous monitoring established for data drift and concept drift in production?


---

## ⚖️ Métrica de Equidad (Fairness)

- **Disparate Impact Ratio:** `0.9159` (Regla del 80%: ✅ CUMPLE)
- **Equal Opportunity Difference:** `0.1457`
- **Demographic Parity Difference:** `-0.0683`

---
*Generado automáticamente por AuditModels Framework v0.1.0*
