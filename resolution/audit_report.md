# 🛡️ Informe de Auditoría de IA - Credit Risk Model

**Puntuación General:** 74.2 / 100  
**Nivel de Riesgo AuditModels:** `MEDIUM`  
**Fecha:** 2026-07-21 10:27:12  

---

## 📊 Resumen de Evaluaciones

| Dimensión Auditada | Puntuación | Nivel de Riesgo |
| :--- | :---: | :---: |
| **Calidad de Datos** | 100.0 / 100 | `LOW` |
| **Rendimiento Predictivo** | 61.8 / 100 | `MEDIUM` |
| **Equidad y Sesgos (Fairness)** | 49.8 / 100 | `HIGH` |
| **Robustez y Perturbaciones** | 100.0 / 100 | `LOW` |
| **Cumplimiento y Gobernanza** | 71.4 / 100 | `MEDIUM` |

---

## ⚠️ Alertas e Indicadores Clave

- ⚠️ Fails 80% rule for Disparate Impact (0.656). Selection rate for 'Female' (18.4%) vs 'Male' (28.0%).
- ⚠️ Significant Equal Opportunity Difference (-0.825). TPR for unprivileged: 0.175, privileged: 1.000.
- ⚠️ Non-compliant item [SEC-01] (NIST AI RMF): Are access control logs and audit trails maintained for model inference and training data?
- ⚠️ Non-compliant item [MON-01] (ISO/IEC 42001): Is continuous monitoring established for data drift and concept drift in production?


---

## ⚖️ Métrica de Equidad (Fairness)

- **Disparate Impact Ratio:** `0.656` (Regla del 80%: ❌ NO CUMPLE)
- **Equal Opportunity Difference:** `-0.825`
- **Demographic Parity Difference:** `-0.0964`

---
*Generado automáticamente por AuditModels Framework v0.1.0*
