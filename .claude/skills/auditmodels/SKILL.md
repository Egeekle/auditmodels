---
name: auditmodels
description: Use when working in this repo (AuditModels) to audit an AI/ML model or dataset — via CLI, the Python API (ModelAuditor), the autonomous agent (ModelTestingAgent), or the Streamlit dashboard (app.py); when interpreting/extending the 13-step audit methodology, the weighted score, or risk levels (LOW/MEDIUM/HIGH/CRITICAL); when generating HTML/Markdown audit reports; or when adding a new audit dimension/module. Trigger on "auditoría", "audit", "ModelAuditor", "ModelTestingAgent", "auditmodels", "fairness/robustness/compliance audit", "risk score", "audit report".
---

# AuditModels

Framework Python (`src/auditmodels/`) + CLI + dashboard Streamlit (`app.py`) para auditar modelos de IA/ML contra 13 pasos de metodología (calidad de datos, rendimiento, fairness, robustez, explicabilidad, seguridad, privacidad, cumplimiento ISO 42001/NIST AI RMF/EU AI Act, entrenamiento, producción/drift, reporting). Paquete gestionado con `uv`, Python >=3.12.

## Puntos de entrada — elegir según el caso

| Caso | Cómo |
|---|---|
| Auditoría rápida, ya tengo `df`, `model`, predicciones | API Python: `ModelAuditor(model_name=...).audit(...)` — ver [src/auditmodels/auditor.py](../../../src/auditmodels/auditor.py) |
| No sé qué columnas son target/sensibles/PII, quiero cero-config | `ModelTestingAgent(...).run_tests(df=..., model=..., model_name=...)` — auto-detecta target, columna sensible, grupos, PII y genera plan de remediación priorizado (`generate_remediation_plan`) |
| Ejecutar desde terminal sin escribir código | `uv run auditmodels --data dataset.csv --target col --model-name "X"` (o `--use-agent` para modo agente; sin `--data` genera dataset sintético demo) — ver [src/auditmodels/cli.py](../../../src/auditmodels/cli.py) |
| Explorar/demostrar visualmente (multi-actor: auditora/cliente/auditor) | `uv run streamlit run app.py` — dashboard de simulación de flujo de auditoría (usa `st.session_state`, datos mock, no persiste) |
| Ejemplos completos end-to-end | `uv run python examples/audit_credit_risk_modelling.py` (clasificación GBDT) o `examples/audit_regression_performance.py` (regresión OLS) |

Comandos base:
```powershell
uv sync                                    # instalar deps
uv run python -m unittest discover -s tests  # correr tests
```

## Flujo típico para auditar un modelo nuevo

1. Tener `df` (pandas), `y_true`, `y_pred`, opcional `y_prob`, `model` entrenado y `predict_fn`.
2. Instanciar `ModelAuditor(model_name=...)` y llamar `.audit(...)` pasando también (si aplican): `sensitive_column` + `privileged_group`/`unprivileged_group` (fairness), `compliance_answers` (dict de bools), `doc_metadata` (model card), `training_config`, `production_df`/`latency_ms`/`error_rate`, `security_answers`, `privacy_answers`.
3. El resultado es un `AuditResult`: `.overall_score`, `.overall_risk_level`, `.all_warnings`, `.sections[dimensión]`.
4. Exportar con `result.export_html(path)` y `result.export_markdown(path)` (usa [src/auditmodels/reporting.py](../../../src/auditmodels/reporting.py)).
5. Si faltan parámetros opcionales (model, predict_fn, sensitive_column...), el auditor **no falla**: esa sección devuelve score 100 con warning "skipped" — no interpretar 100 en esas dimensiones como "aprobado", sino como "no evaluado".

## Scoring y niveles de riesgo

`overall_score` = suma ponderada de 11 dimensiones (cada una 0–100, penalización desde base 100):

privacidad 15%, rendimiento 15%, calidad de datos 10%, fairness 10%, robustez 10%, seguridad 10%, explicabilidad 10%, cumplimiento 10%, documentación 5%, entrenamiento 5%, producción 5%.

Niveles: `LOW` ≥80 · `MEDIUM` 60–79.9 · `HIGH` 40–59.9 · `CRITICAL` <40.

Para las fórmulas exactas de penalización por dimensión (ej. Disparate Impact, PSI, Gini/KS bancarios, umbrales de nulos/duplicados/PII) y resultados empíricos de los 3 ejemplos del repo, leer **[README_CRITERIOS_SCORE.md](../../../README_CRITERIOS_SCORE.md)** en vez de recalcular de memoria — es la referencia autoritativa y ya está detallada ahí.

## Mapa de módulos (paso metodológico → archivo)

Cada dimensión vive en su propio módulo `audit_*` bajo `src/auditmodels/`, todos con la firma `audit_x(...) -> dict` (con `score`, `risk_level`, `warnings`). El orquestador es [auditor.py](../../../src/auditmodels/auditor.py); todos se re-exportan desde [src/auditmodels/__init__.py](../../../src/auditmodels/__init__.py).

- `data_audit.py` — calidad de datos + flag de PII (pasos 3 y 10)
- `performance_audit.py` — clasificación (ROC-AUC/F1/Gini/KS) o regresión (MAE/RMSE/R²) (paso 5)
- `fairness_audit.py` — Disparate Impact (regla 80%) + Equal Opportunity (paso 6)
- `robustness_audit.py` — estrés con ruido Gaussiano σ=5%/15% (paso 7)
- `explainability_audit.py` — feature_importances_/coef_ (paso 8)
- `security_audit.py` — rate limiting, RBAC, audit logs, extracción de modelo (paso 9)
- `privacy_audit.py` — anonimización, memorización, retención (paso 10)
- `compliance_audit.py` — checklist ISO 42001/NIST AI RMF/EU AI Act (paso 11)
- `documentation_audit.py` — model card (paso 2)
- `training_audit.py` — split, hiperparámetros, seed, versionado (paso 4)
- `production_audit.py` — PSI drift, concept drift, latencia, error rate (paso 12)
- `reporting.py` — genera HTML/MD (paso 13)
- `agent.py` — `ModelTestingAgent`: auto-detección + orquesta `ModelAuditor` + plan de remediación
- `cli.py` — entrypoint `auditmodels` (declarado en `pyproject.toml` `[project.scripts]`)

## Para añadir/modificar una dimensión de auditoría

1. Editar (o crear) el módulo `audit_x.py` correspondiente; mantener el contrato de retorno `{"score": float 0-100, "risk_level": "LOW"|"MEDIUM"|"HIGH", "warnings": [...]}` más los campos específicos de esa dimensión.
2. Si cambian los pesos o se añade una dimensión nueva, actualizar el dict `weights` en `ModelAuditor.audit()` ([auditor.py](../../../src/auditmodels/auditor.py)) — deben sumar 1.0.
3. Actualizar `generate_html_report`/`generate_markdown_report` en `reporting.py` si la nueva sección debe aparecer en los reportes.
4. Añadir/actualizar tests en `tests/test_audit.py` (o `tests/test_agent.py` si afecta auto-detección/remediación).
5. Si cambian pesos o fórmulas, reflejarlo en `README_CRITERIOS_SCORE.md` para que la tabla no quede desactualizada.

## Notas

- `app.py` (dashboard Streamlit) es una simulación de UX multi-actor (empresa auditora / empresa cliente / auditor responsable) con datos mock en `st.session_state`; **no** está conectado al motor real `ModelAuditor`/`ModelTestingAgent` — no asumir que los números que muestra vienen de una auditoría ejecutada.
- Los reportes HTML/MD generados por ejemplos y por el CLI se escriben en la raíz del repo (`*_audit_report.html/.md`) y también hay copias en `resolution/` — no confundir esos artefactos versionados con salida nueva a regenerar.
