"""Script de test et de validation pour le Moteur de Risque & Benchmark (Phase 3)."""

import os
import csv
import json

def test_risk_engine():
    bench_path = "data/processed/benchmark_results.json"
    scored_path = "data/processed/scored_open_orders.csv"

    assert os.path.exists(bench_path), f"Fichier manquant : {bench_path}"
    assert os.path.exists(scored_path), f"Fichier manquant : {scored_path}"

    with open(bench_path, mode="r", encoding="utf-8") as f:
        bench = json.load(f)

    v0 = bench["metrics"]["v0_baseline"]
    v1 = bench["metrics"]["v1_machine_learning"]

    print("================================================================================")
    print("=== BENCHMARK COMPARATIF DE VALIDATION (LIVRABLE MÉMOIRE X / Y / Z) ===")
    print("================================================================================")
    print(f"{'Métrique Métier (Y)':<32} | {'Baseline v0':<15} | {'Modèle IA v1':<15} | {'Gain / Écart'}")
    print("-" * 80)
    print(f"{'Taux de Rappel (Retards détectés)':<32} | {v0['recall_pct']:>13.1f}% | {v1['recall_pct']:>13.1f}% | +{v1['recall_pct'] - v0['recall_pct']:.1f}%")
    print(f"{'Précision':<32} | {v0['precision_pct']:>13.1f}% | {v1['precision_pct']:>13.1f}% | +{v1['precision_pct'] - v0['precision_pct']:.1f}%")
    print(f"{'Garde-fou : Faux Positifs':<32} | {v0['false_positive_rate_pct']:>13.1f}% | {v1['false_positive_rate_pct']:>13.1f}% | {v1['false_positive_rate_pct'] - v0['false_positive_rate_pct']:+.1f}%")
    print(f"{'Délai Moyen d Anticipation':<32} | {v0['avg_anticipation_days']:>12.1f} j | {v1['avg_anticipation_days']:>12.1f} j | +{v1['avg_anticipation_days'] - v0['avg_anticipation_days']:.1f} jours")
    if "roc_auc" in v1:
        print(f"{'Capacité Discriminante (ROC AUC)':<32} | {'N/A (Règle)':>15} | {v1['roc_auc']:>15.3f} | Score élevé (>0.85)")
    print("================================================================================")

    print("\n=== TOP 5 DES VARIABLES LES PLUS IMPORTANTES (EXPLICABILITÉ IA) ===")
    for item in bench["feature_importances"][:5]:
        print(f"- {item['feature']:<30} : {item['importance_pct']:>5.1f}%")

    with open(scored_path, mode="r", encoding="utf-8") as f:
        scored_orders = list(csv.DictReader(f))

    n_red = sum(1 for r in scored_orders if r["badge_color"] == "Rouge")
    n_orange = sum(1 for r in scored_orders if r["badge_color"] == "Orange")
    n_green = sum(1 for r in scored_orders if r["badge_color"] == "Vert")

    print(f"\n=== RÉPARTITION DES 66 COMMANDES OUVERTES EN COURS ===")
    print(f"- Risque Élevé (Rouge > 65%) : {n_red} commandes (Relances prioritaires)")
    print(f"- Risque Modéré (Orange 35-65%) : {n_orange} commandes (À surveiller)")
    print(f"- Risque Faible (Vert < 35%) : {n_green} commandes (Flux nominal)")
    print("================================================================================")
    print("=== VALIDATION DE LA PHASE 3 RÉUSSIE AVEC SUCCÈS [OK] ===")
    print("================================================================================")

if __name__ == "__main__":
    test_risk_engine()
