from __future__ import annotations

from collections import OrderedDict
from hashlib import sha256

import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import KFold

# Only profile attributes available independently of the final assessment result.
FEATURES = ("clicks", "engagement_trend", "completion", "attempts", "credits", "active_weeks")
_CACHE_LIMIT = 4
_MODEL_CACHE: OrderedDict[str, tuple[HistGradientBoostingRegressor, dict[str, float], float, int]] = OrderedDict()


def vector(student):
    return [float(getattr(student, feature, 0) or 0) for feature in FEATURES]


def _scored_rows(rows):
    return sorted(
        (row for row in rows if row.score is not None and float(row.completion or 0) > 0),
        key=lambda row: row.student_code,
    )


def _fingerprint(rows):
    digest = sha256()
    for row in rows:
        values = [row.student_code, *(format(value, ".8g") for value in vector(row)), format(float(row.score), ".8g")]
        digest.update("|".join(values).encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def _new_model():
    # Histogram boosting is much faster than fitting several large forests for each request.
    return HistGradientBoostingRegressor(
        max_iter=70,
        max_leaf_nodes=15,
        min_samples_leaf=25,
        learning_rate=0.08,
        l2_regularization=2.0,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=6,
        random_state=42,
    )


def _models_for(rows):
    scored = _scored_rows(rows)
    if len(scored) < 20:
        raise ValueError("At least 20 learner profiles with scored assessment submissions are required.")

    fingerprint = _fingerprint(scored)
    cached = _MODEL_CACHE.get(fingerprint)
    if cached is not None:
        _MODEL_CACHE.move_to_end(fingerprint)
        return cached

    x = np.asarray([vector(row) for row in scored], dtype=np.float32)
    y = np.asarray([float(row.score) for row in scored], dtype=np.float32)
    folds = KFold(n_splits=5, shuffle=True, random_state=42)
    out_of_fold: dict[str, float] = {}
    holdout_actual: list[float] = []
    holdout_predicted: list[float] = []

    # Each existing learner receives a prediction from a model that did not train on that learner.
    for train_index, test_index in folds.split(x):
        model = _new_model()
        model.fit(x[train_index], y[train_index])
        fold_predictions = model.predict(x[test_index])
        for index, value in zip(test_index, fold_predictions):
            out_of_fold[scored[index].student_code] = float(value)
        holdout_actual.extend(y[test_index].tolist())
        holdout_predicted.extend(fold_predictions.tolist())

    final_model = _new_model()
    final_model.fit(x, y)
    mae = float(mean_absolute_error(holdout_actual, holdout_predicted))
    result = (final_model, out_of_fold, mae, len(scored))
    _MODEL_CACHE[fingerprint] = result
    _MODEL_CACHE.move_to_end(fingerprint)
    while len(_MODEL_CACHE) > _CACHE_LIMIT:
        _MODEL_CACHE.popitem(last=False)
    return result


def predictions(rows, target):
    model, out_of_fold, mae, scored_count = _models_for(rows)
    predicted = out_of_fold.get(target.student_code)
    if predicted is None:
        predicted = float(model.predict(np.asarray([vector(target)], dtype=np.float32))[0])
    return {
        "predicted_assessment_score": round(max(0.0, min(100.0, predicted)), 1),
        "performance_model": {
            "type": "HistGradientBoostingRegressor",
            "target": "mean score across submitted assessments (%)",
            "features": list(FEATURES),
            "mae": round(mae, 2),
            "holdout_rows": scored_count,
        },
        "training_rows": scored_count,
        "data_scope": "Estimated from profiles with scored assessment submissions; demonstration data only.",
    }
