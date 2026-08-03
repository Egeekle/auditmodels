# 🛡️ Informe de Auditoría de IA - Credit Risk RandomForest Classifier

**Puntuación General:** 71.0 / 100  
**Nivel de Riesgo AuditModels:** `MEDIUM`  
**Fecha:** 2026-07-31 11:50:51  

---

## 📝 Alcance y Metodología
- **Alcance:** Auditoría técnica integral de seguridad, cumplimiento, calidad de datos, equidad algorítmica, explicabilidad y deriva en producción para el modelo *Credit Risk RandomForest Classifier*.
- **Metodología:** Análisis cuantitativo estructurado evaluando las 11 fases de `src/auditmodels/` mapeadas a ISO 42001, NIST AI RMF y EU AI Act.

---

## 📊 Resumen por Fases de Auditoría (`src/auditmodels`)

| Fases Auditadas | Puntuación | Nivel de Riesgo |
| :--- | :---: | :---: |
| **1. Calidad de Datos** (`data_audit`) | 85.0 / 100 | `LOW` |
| **2. Rendimiento Predictivo** (`performance_audit`) | 100.0 / 100 | `LOW` |
| **3. Equidad y Sesgos** (`fairness_audit`) | 93.8 / 100 | `LOW` |
| **4. Robustez y Estrés** (`robustness_audit`) | 100.0 / 100 | `LOW` |
| **5. Explicabilidad** (`explainability_audit`) | 80.0 / 100 | `LOW` |
| **6. Seguridad** (`security_audit`) | 35.0 / 100 | `HIGH` |
| **7. Privacidad** (`privacy_audit`) | 30.0 / 100 | `HIGH` |
| **8. Cumplimiento y Gobernanza** (`compliance_audit`) | 71.4 / 100 | `MEDIUM` |
| **9. Documentación** (`documentation_audit`) | 0.0 / 100 | `HIGH` |
| **10. Entrenamiento** (`training_audit`) | 0.0 / 100 | `HIGH` |
| **11. Producción y Deriva** (`production_audit`) | 100.0 / 100 | `LOW` |

---

## ⚠️ Evidencias y Riesgos Identificados (Alertas)
- ⚠️ Potential PII columns identified without explicit anonymization flag: ['email', 'ssn']
- ⚠️ Robustness test skipped: predict_fn failed on validation dataset (The feature names should match those that were passed during fit.
Feature names unseen at fit time:
- approved
)
- ⚠️ Alta dominancia de una sola característica 'gender' (71.8% de importancia). Riesgo de sesgo por característica única.
- ⚠️ Non-compliant item [SEC-01] (NIST AI RMF): Are access control logs and audit trails maintained for model inference and training data?
- ⚠️ Non-compliant item [MON-01] (ISO/IEC 42001): Is continuous monitoring established for data drift and concept drift in production?
- ⚠️ Falta documentación sobre: Objetivo del modelo (qué problema resuelve y metas de negocio)
- ⚠️ Falta documentación sobre: Casos de uso autorizados y contexto de despliegue
- ⚠️ Falta documentación sobre: Arquitectura del sistema (pipeline de datos, preprocesamiento, modelo)
- ⚠️ Falta documentación sobre: Algoritmos utilizados (ej. Gradient Boosting, Regresión Logística, Neural Net)
- ⚠️ Falta documentación sobre: Versión del modelo (ej. v1.2.0 o hash de commit git)
- ⚠️ Falta documentación sobre: Limitaciones conocidas y casos bordes no cubiertos
- ⚠️ Falta documentación sobre: Responsables del desarrollo, mantenimiento y gobernanza
- ⚠️ No se registraron las proporciones de división de datos (Train/Val/Test).
- ⚠️ No se registraron los hiperparámetros del entrenamiento del modelo.
- ⚠️ No se definió una semilla aleatoria (random seed) para garantizar reproducibilidad.
- ⚠️ No se ha verificado explícitamente la reproducibilidad del código de entrenamiento.
- ⚠️ El entrenamiento carece de versionado de código (ej. commit de Git o registro MLflow).
- ⚠️ Riesgo de Extracción de Modelo: No se detectó limitación de peticiones (rate limiting) en las APIs de inferencia.
- ⚠️ Riesgo de Extracción de Modelo: El API devuelve probabilidades con alta precisión, facilitando la copia del modelo.
- ⚠️ Riesgo de Inversión de Modelo: No hay defensas activas de inferencia de membresía (ej. privacidad diferencial o ruido en outputs).
- ⚠️ Control de Acceso: El entorno de despliegue no tiene autenticación / RBAC configurado para el acceso al modelo.
- ⚠️ Registro de Auditoría: No hay registros inmutables (audit trails) que logueen las consultas e inferencias del modelo.
- ⚠️ Protección de Datos: Columnas con PII potencial expuestas en texto plano: ['email', 'ssn']
- ⚠️ Memorización de Datos: No se han realizado pruebas de ataque de inferencia de membresía (membership inference) para evaluar memorización de datos de entrenamiento.
- ⚠️ Técnicas de Anonimización: Se identificaron columnas PII pero no hay hashing, enmascaramiento o tokenización activa en el pipeline.
- ⚠️ Políticas de Retención: No existe una política definida de expiración o purga de datos históricos de consultas e inferencias.

---

## 💡 Explicabilidad (Top Variables Predictivas)
- **Variables principales:** gender, credit_score, debt_to_income, annual_income

---

## ⚖️ Métrica de Equidad (Fairness)

- **Disparate Impact Ratio:** `1.125` (Regla del 80%: ✅ CUMPLE)
- **Equal Opportunity Difference:** `0.0`
- **Demographic Parity Difference:** `0.0417`

---

## 📋 Recomendaciones y Plan de Remediación

### Recomendaciones
- 📌 Cifrar/Enmascarar columnas PII detectadas: ['email', 'ssn'].

### Plan de Remediación
- 🛠️ Seguridad/Privacidad: Implementar hashing SHA-256 o tokenización en variables de identificación personal.

---
*Generado automáticamente por AuditModels Framework v0.1.0*
