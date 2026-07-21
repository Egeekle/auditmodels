from typing import Dict, Any, Optional, List


def audit_training(
    training_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Audits model training process, data split strategy, hyperparameter tracking, and reproducibility.

    Args:
        training_config: Dict containing training details such as split_ratios, random_seed,
                         hyperparameters, versioning, and reproducibility_verified.

    Returns:
        Dict containing training audit score (0-100), risk level, and warnings.
    """
    config = training_config or {}
    warnings = []

    # 1. Data Split Audit
    split_ratios = config.get("split_ratios", {})
    train_ratio = split_ratios.get("train", 0.0)
    val_ratio = split_ratios.get("val", 0.0)
    test_ratio = split_ratios.get("test", 0.0)

    total_split = train_ratio + val_ratio + test_ratio
    is_stratified = config.get("is_stratified", False)

    if not split_ratios:
        warnings.append("No se registraron las proporciones de división de datos (Train/Val/Test).")
    elif abs(total_split - 1.0) > 0.01 and abs(total_split - 100) > 1.0:
        warnings.append(f"La suma de las proporciones de división no suma 100%: {split_ratios}")
    elif test_ratio == 0:
        warnings.append("El conjunto de datos de prueba (Test set) está ausente en la configuración de entrenamiento.")

    if not is_stratified and config.get("problem_type") == "classification":
        warnings.append("La división de datos no utilizó estratificación por clase (Stratified Split).")

    # 2. Hyperparameters & Parameters
    hyperparams = config.get("hyperparameters", {})
    if not hyperparams:
        warnings.append("No se registraron los hiperparámetros del entrenamiento del modelo.")

    # 3. Reproducibility & Random Seed
    random_seed = config.get("random_seed")
    reproducibility_verified = config.get("reproducibility_verified", False)

    if random_seed is None:
        warnings.append("No se definió una semilla aleatoria (random seed) para garantizar reproducibilidad.")
    if not reproducibility_verified:
        warnings.append("No se ha verificado explícitamente la reproducibilidad del código de entrenamiento.")

    # 4. Versioning & Lineage
    model_version = config.get("model_version")
    code_commit = config.get("git_commit")

    if not model_version and not code_commit:
        warnings.append("El entrenamiento carece de versionado de código (ej. commit de Git o registro MLflow).")

    # Score calculation (100 base)
    score = 100.0
    if not split_ratios: score -= 25
    if test_ratio == 0: score -= 20
    if not hyperparams: score -= 20
    if random_seed is None: score -= 15
    if not reproducibility_verified: score -= 10
    if not model_version and not code_commit: score -= 10

    score = max(0.0, round(score, 1))
    risk_level = "LOW" if score >= 80 else ("MEDIUM" if score >= 60 else "HIGH")

    return {
        "score": score,
        "risk_level": risk_level,
        "split_ratios": split_ratios,
        "is_stratified": is_stratified,
        "hyperparameters": hyperparams,
        "random_seed": random_seed,
        "reproducibility_verified": reproducibility_verified,
        "model_version": model_version,
        "git_commit": code_commit,
        "warnings": warnings,
    }
