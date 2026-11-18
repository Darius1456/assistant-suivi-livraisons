"""Script de test et de validation pour le Feature Engine (Phase 2)."""

import os
import csv

def test_feature_engine():
    kpi_path = "data/processed/supplier_kpis.csv"
    history_feat_path = "data/processed/features_history.csv"
    open_feat_path = "data/processed/features_open_orders.csv"

    assert os.path.exists(kpi_path), f"Fichier manquant : {kpi_path}"
    assert os.path.exists(history_feat_path), f"Fichier manquant : {history_feat_path}"
    assert os.path.exists(open_feat_path), f"Fichier manquant : {open_feat_path}"

    with open(kpi_path, mode="r", encoding="utf-8") as f:
        kpi_rows = list(csv.DictReader(f))

    with open(open_feat_path, mode="r", encoding="utf-8") as f:
        open_rows = list(csv.DictReader(f))

    # 1. Vérification des fournisseurs
    assert len(kpi_rows) == 5, f"Attendu : 5 fournisseurs, obtenu : {len(kpi_rows)}"
    
    print("==================================================")
    print("=== SCORECARD FOURNISSEURS CALCULÉE (PHASE 2) ===")
    print("==================================================")
    for r in sorted(kpi_rows, key=lambda x: float(x["otd_rate_pct"]), reverse=True):
        otd = float(r["otd_rate_pct"])
        late_rate = float(r["late_rate_pct"])
        avg_delay = float(r["avg_delay_days_late_only"])
        total_cmd = int(r["total_orders_delivered"])
        sup_name = r["supplier_name_clean"]
        print(f"[{r['supplier_id']}] {sup_name:<22} | OTD: {otd:5.1f}% | Taux Retard: {late_rate:5.1f}% | Retard moyen: +{avg_delay:.1f}j | Vol: {total_cmd} cmd")
        # Sanity check
        assert abs((otd + late_rate) - 100.0) < 0.5, f"Erreur de somme OTD + Retard pour {sup_name}"

    # 2. Vérification des features sur les commandes ouvertes
    required_features = [
        "supplier_otd_pct", "supplier_avg_delay_late_only", "supplier_std_delay",
        "lead_time_compression_ratio", "criticality_score", "days_until_promised"
    ]
    for feat in required_features:
        assert feat in open_rows[0], f"Feature {feat} manquante dans {open_feat_path}"

    print("==================================================")
    print(f"- Commandes ouvertes enrichies prêtes pour le scoring : {len(open_rows)}")
    print("=== TOUS LES TESTS DU FEATURE ENGINE SONT VALIDÉS [OK] ===")
    print("==================================================")

if __name__ == "__main__":
    test_feature_engine()
