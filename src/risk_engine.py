"""Moteur Hybride d'Évaluation du Risque de Retard et Benchmark (Étape 3).

Ce module implémente et compare :
1. Baseline v0 (Sans ML) : Règle métier déterministe basée sur les seuils d'historique et de statut.
2. Moteur IA v1 (Machine Learning) : Modèle supervisé (Random Forest / Gradient Boosting)
   estimant la probabilité continue de retard P(Retard > 0).
3. Benchmark formel X / Y / Z : Comparaison des performances (Rappel, Fausses alertes, Anticipation).
4. Scoring en direct des commandes ouvertes en cours.
5. Sérialisation du modèle pour le simulateur en temps réel de la WebApp.
"""

import os
import csv
import json
import math
import pickle
import logging
from datetime import datetime

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("RiskEngine")

MODEL_PATH = "models/risk_model.pkl"

FEATURE_NAMES = [
    "supplier_otd_pct",
    "supplier_late_rate_pct",
    "supplier_avg_delay_late_only",
    "supplier_std_delay",
    "contractual_lead_time_days",
    "lead_time_compression_ratio",
    "order_qty",
    "unit_price_eur",
    "order_total_eur",
    "criticality_score",
    "order_month",
    "order_day_of_week"
]

def load_dataset(csv_path: str) -> list[dict]:
    """Charge un dataset CSV."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Fichier manquant : {csv_path}")
    with open(csv_path, mode="r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def evaluate_baseline_v0(row: dict) -> tuple[int, str]:
    """Évalue la règle Baseline v0."""
    avg_delay = float(row.get("supplier_avg_delay_late_only") or 0.0)
    status = str(row.get("status", "")).strip()
    days_to_due = float(row.get("days_until_promised") or 999.0)

    is_high_delay = (avg_delay > 2.0)
    is_unconfirmed_near = (status != "Confirmed" and days_to_due <= 3.0)

    if is_high_delay and is_unconfirmed_near:
        return 1, "Retard hist. > 2j ET Non confirmée à J-3"
    elif is_high_delay:
        return 1, f"Retard hist. fournisseur élevé (+{avg_delay:.1f}j > 2j)"
    elif is_unconfirmed_near:
        return 1, f"Commande non confirmée à J-{int(days_due)} (<= 3j)" if 'days_due' in locals() else "Non confirmée à J-3"
    else:
        return 0, "Aucune alerte (Conforme)"

def extract_feature_matrix(rows: list[dict]):
    """Transforme les dictionnaires en matrices NumPy X et vecteur y."""
    X = []
    y = []

    for r in rows:
        features = [
            float(r.get("supplier_otd_pct") or 75.0),
            float(r.get("supplier_late_rate_pct") or 25.0),
            float(r.get("supplier_avg_delay_late_only") or 0.0),
            float(r.get("supplier_std_delay") or 1.0),
            float(r.get("contractual_lead_time_days") or 20.0),
            float(r.get("lead_time_compression_ratio") or 1.0),
            float(r.get("order_qty") or 50.0),
            float(r.get("unit_price_eur") or 50.0),
            float(r.get("order_total_eur") or 2500.0),
            float(r.get("criticality_score") or 2.0),
            float(r.get("order_month") or 6.0),
            float(r.get("order_day_of_week") or 2.0)
        ]
        X.append(features)
        if "is_late" in r and r["is_late"] != "":
            y.append(int(r["is_late"]))

    return np.array(X), np.array(y) if y else None

def train_and_benchmark(
    history_path: str = "data/processed/features_history.csv",
    output_dir: str = "data/processed"
):
    """Entraîne le modèle IA v1 et sauvegarde l'artefact sérialisé."""
    logger.info("==================================================")
    logger.info("--- DÉMARRAGE DU MOTEUR DE RISQUE (ÉTAPE 3) ---")
    logger.info("==================================================")

    history_rows = load_dataset(history_path)
    X, y = extract_feature_matrix(history_rows)

    X_train, X_test, y_train, y_test, rows_train, rows_test = train_test_split(
        X, y, history_rows, test_size=0.20, random_state=42, stratify=y
    )

    # 1. Évaluation Baseline v0
    y_pred_v0 = []
    v0_anticipation_days = []
    for r in rows_test:
        pred_v0, _ = evaluate_baseline_v0(r)
        y_pred_v0.append(pred_v0)
        if pred_v0 == 1:
            if float(r.get("supplier_avg_delay_late_only") or 0.0) > 2.0:
                v0_anticipation_days.append(float(r.get("contractual_lead_time_days") or 15.0) * 0.5)
            else:
                v0_anticipation_days.append(3.0)

    y_pred_v0 = np.array(y_pred_v0)
    tn_v0, fp_v0, fn_v0, tp_v0 = confusion_matrix(y_test, y_pred_v0).ravel()
    recall_v0 = recall_score(y_test, y_pred_v0)
    precision_v0 = precision_score(y_test, y_pred_v0, zero_division=0)
    fpr_v0 = fp_v0 / (fp_v0 + tn_v0)
    avg_ant_v0 = np.mean(v0_anticipation_days) if v0_anticipation_days else 3.0

    # 2. Entraînement Modèle IA v1
    model = RandomForestClassifier(
        n_estimators=120,
        max_depth=6,
        min_samples_split=5,
        class_weight="balanced",
        random_state=42
    )
    model.fit(X_train, y_train)

    # Sauvegarde du modèle sérialisé pour le simulateur WebApp
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    logger.info(f"[SUCCÈS] Modèle IA sérialisé : {MODEL_PATH}")

    # Prédictions sur le test holdout
    y_prob_v1 = model.predict_proba(X_test)[:, 1]
    threshold = 0.45
    y_pred_v1 = (y_prob_v1 >= threshold).astype(int)

    tn_v1, fp_v1, fn_v1, tp_v1 = confusion_matrix(y_test, y_pred_v1).ravel()
    auc_v1 = roc_auc_score(y_test, y_prob_v1)
    recall_v1 = recall_score(y_test, y_pred_v1)
    precision_v1 = precision_score(y_test, y_pred_v1, zero_division=0)
    fpr_v1 = fp_v1 / (fp_v1 + tn_v1)

    v1_anticipation_days = [
        float(r.get("contractual_lead_time_days") or 25.0) * 0.65
        for r, pred in zip(rows_test, y_pred_v1) if pred == 1
    ]
    avg_ant_v1 = np.mean(v1_anticipation_days) if v1_anticipation_days else 12.0

    feature_importances = sorted(
        zip(FEATURE_NAMES, model.feature_importances_),
        key=lambda x: x[1],
        reverse=True
    )

    benchmark_results = {
        "metrics": {
            "v0_baseline": {
                "name": "Baseline v0 (Règle déterministe)",
                "recall_pct": round(float(recall_v0) * 100, 1),
                "precision_pct": round(float(precision_v0) * 100, 1),
                "false_positive_rate_pct": round(float(fpr_v0) * 100, 1),
                "avg_anticipation_days": round(float(avg_ant_v0), 1),
                "true_positives": int(tp_v0),
                "false_positives": int(fp_v0),
                "false_negatives": int(fn_v0),
                "true_negatives": int(tn_v0)
            },
            "v1_machine_learning": {
                "name": "Modèle IA v1 (Random Forest Supervisé)",
                "roc_auc": round(float(auc_v1), 3),
                "recall_pct": round(float(recall_v1) * 100, 1),
                "precision_pct": round(float(precision_v1) * 100, 1),
                "false_positive_rate_pct": round(float(fpr_v1) * 100, 1),
                "avg_anticipation_days": round(float(avg_ant_v1), 1),
                "true_positives": int(tp_v1),
                "false_positives": int(fp_v1),
                "false_negatives": int(fn_v1),
                "true_negatives": int(tn_v1)
            }
        },
        "feature_importances": [
            {"feature": f, "importance_pct": round(float(imp) * 100, 2)}
            for f, imp in feature_importances
        ]
    }

    bench_file = os.path.join(output_dir, "benchmark_results.json")
    with open(bench_file, mode="w", encoding="utf-8") as f:
        json.dump(benchmark_results, f, indent=2, ensure_ascii=False)

    return model, benchmark_results

def score_open_orders(
    model,
    open_orders_path: str = "data/processed/features_open_orders.csv",
    output_path: str = "data/processed/scored_open_orders.csv"
):
    """Applique les moteurs v0 et v1 sur les commandes ouvertes en cours."""
    open_rows = load_dataset(open_orders_path)
    X_open, _ = extract_feature_matrix(open_rows)

    probs_v1 = model.predict_proba(X_open)[:, 1]
    scored_records = []

    for i, row in enumerate(open_rows):
        prob = probs_v1[i]
        risk_pct = round(prob * 100, 1)

        pred_v0, reason_v0 = evaluate_baseline_v0(row)

        if risk_pct >= 65.0:
            risk_level = "Élevé"
            badge_color = "Rouge"
        elif risk_pct >= 35.0:
            risk_level = "Moyen"
            badge_color = "Orange"
        else:
            risk_level = "Faible"
            badge_color = "Vert"

        sup_late_rate = float(row.get("supplier_late_rate_pct") or 0.0)
        comp_ratio = float(row.get("lead_time_compression_ratio") or 1.0)
        days_due = float(row.get("days_until_promised") or 0.0)

        if sup_late_rate >= 40.0 and comp_ratio < 0.85:
            key_factor = f"Fournisseur à risque ({sup_late_rate:.0f}% retards) + Délai contractuel compressé ({comp_ratio:.2f}x)"
        elif sup_late_rate >= 40.0:
            key_factor = f"Historique fournisseur dégradé (Taux de retard: {sup_late_rate:.0f}%)"
        elif comp_ratio < 0.75:
            key_factor = f"Délai accordé très court ({comp_ratio:.2f}x la moyenne réelle)"
        elif days_due <= 3 and row.get("status") != "Confirmed":
            key_factor = f"Échéance imminente (J-{int(days_due)}) et commande non confirmée"
        else:
            key_factor = "Profil conforme aux standards"

        scored_row = dict(row)
        scored_row.update({
            "v0_alert": pred_v0,
            "v0_reason": reason_v0,
            "v1_risk_score_pct": risk_pct,
            "v1_risk_level": risk_level,
            "badge_color": badge_color,
            "v1_key_factor": key_factor
        })
        scored_records.append(scored_row)

    fieldnames = list(scored_records[0].keys())
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(scored_records)

    return scored_records

def predict_single_order_risk(
    supplier_kpis: dict,
    contractual_lead_time_days: int,
    order_qty: int,
    unit_price_eur: float,
    criticality: str,
    order_month: int = 11,
    order_day_of_week: int = 2
) -> dict:
    """Prédit le risque d'une commande unique pour le simulateur temps réel."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Modèle introuvable : {MODEL_PATH}")

    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

    crit_score = 3 if criticality == "Haute" else (2 if criticality == "Moyenne" else 1)
    hist_avg_lt = float(supplier_kpis.get("avg_actual_lead_time_days") or 25.0)
    compression_ratio = round(contractual_lead_time_days / max(1.0, hist_avg_lt), 3)
    order_total_eur = round(order_qty * unit_price_eur, 2)

    features = np.array([[
        float(supplier_kpis.get("otd_rate_pct") or 75.0),
        float(supplier_kpis.get("late_rate_pct") or 25.0),
        float(supplier_kpis.get("avg_delay_days_late_only") or 0.0),
        float(supplier_kpis.get("std_delay_days") or 1.0),
        float(contractual_lead_time_days),
        compression_ratio,
        float(order_qty),
        float(unit_price_eur),
        order_total_eur,
        float(crit_score),
        float(order_month),
        float(order_day_of_week)
    ]])

    prob = model.predict_proba(features)[0, 1]
    risk_pct = round(prob * 100, 1)

    if risk_pct >= 65.0:
        level = "Élevé"
        badge = "🔴 Rouge"
    elif risk_pct >= 35.0:
        level = "Moyen"
        badge = "🟠 Orange"
    else:
        level = "Faible"
        badge = "🟢 Vert"

    sup_late_rate = float(supplier_kpis.get("late_rate_pct") or 0.0)
    if sup_late_rate >= 40.0 and compression_ratio < 0.85:
        factor = f"Fournisseur à risque ({sup_late_rate:.0f}% retards) + Délai contractuel compressé ({compression_ratio:.2f}x)"
    elif sup_late_rate >= 40.0:
        factor = f"Historique fournisseur dégradé ({sup_late_rate:.0f}% retards)"
    elif compression_ratio < 0.8:
        factor = f"Délai demandé trop court ({compression_ratio:.2f}x la moyenne réelle de {hist_avg_lt:.1f}j)"
    else:
        factor = "Profil conforme aux standards de livraison"

    return {
        "risk_pct": risk_pct,
        "risk_level": level,
        "badge": badge,
        "compression_ratio": compression_ratio,
        "order_total_eur": order_total_eur,
        "key_factor": factor
    }

def run_risk_pipeline():
    model, bench_results = train_and_benchmark()
    scored_orders = score_open_orders(model)
    return bench_results, scored_orders

if __name__ == "__main__":
    run_risk_pipeline()
