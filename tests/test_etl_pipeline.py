"""Script de test et de validation pour le pipeline ETL (Phase 1)."""

import os
import csv

def test_pipeline_outputs():
    raw_path = "data/raw/orders_raw.csv"
    history_path = "data/processed/history_cleaned.csv"
    open_path = "data/processed/open_orders.csv"

    assert os.path.exists(raw_path), f"Fichier raw manquant : {raw_path}"
    assert os.path.exists(history_path), f"Fichier historique manquant : {history_path}"
    assert os.path.exists(open_path), f"Fichier open manquant : {open_path}"

    with open(raw_path, mode="r", encoding="utf-8") as f:
        raw_rows = list(csv.DictReader(f))

    with open(history_path, mode="r", encoding="utf-8") as f:
        hist_rows = list(csv.DictReader(f))

    with open(open_path, mode="r", encoding="utf-8") as f:
        open_rows = list(csv.DictReader(f))

    # 1. Vérification du dédoublonnage
    hist_ids = [r["order_id"] for r in hist_rows]
    open_ids = [r["order_id"] for r in open_rows]
    assert len(hist_ids) == len(set(hist_ids)), "Erreur : Doublons détectés dans l'historique !"
    assert len(open_ids) == len(set(open_ids)), "Erreur : Doublons détectés dans les commandes ouvertes !"
    assert len(set(hist_ids).intersection(set(open_ids))) == 0, "Erreur : Recouvrement entre historique et ouvertures !"

    # 2. Vérification des colonnes calculées
    expected_cols = ["delay_days", "is_late", "contractual_lead_time_days", "supplier_name_clean"]
    for col in expected_cols:
        assert col in hist_rows[0], f"Colonne {col} manquante dans history_cleaned"
        assert col in open_rows[0], f"Colonne {col} manquante dans open_orders"

    # 3. Vérification des statuts
    for r in hist_rows:
        assert r["status"] == "Delivered", f"Statut non livré trouvé dans l'historique : {r['status']}"
        assert r["delay_days"] != "", "delay_days vide pour une commande livrée !"
        assert r["is_late"] in ["0", "1"], f"is_late invalide : {r['is_late']}"

    for r in open_rows:
        assert r["status"] in ["Open", "Confirmed", "In Transit"], f"Statut invalide dans les commandes ouvertes : {r['status']}"

    # 4. Statistiques de retard
    late_count = sum(1 for r in hist_rows if r["is_late"] == "1")
    ontime_count = sum(1 for r in hist_rows if r["is_late"] == "0")
    otd_global = ontime_count / len(hist_rows) * 100

    print("==================================================")
    print("=== RÉSULTATS DE VALIDATION DU PIPELINE ETL ===")
    print("==================================================")
    print(f"- Lignes brutes initiales : {len(raw_rows)}")
    print(f"- Commandes livrées dédoublonnées (historique) : {len(hist_rows)}")
    print(f"- Commandes ouvertes actives : {len(open_rows)}")
    print(f"- Total commandes dédoublonnées : {len(hist_rows) + len(open_rows)}")
    print(f"- Commandes historiques livrées à l'heure : {ontime_count} ({otd_global:.1f}%)")
    print(f"- Commandes historiques en retard : {late_count} ({100 - otd_global:.1f}%)")
    print("==================================================")
    print("=== TOUS LES TESTS DE VALIDATION SONT PASSÉS AVEC SUCCÈS [OK] ===")
    print("==================================================")

if __name__ == "__main__":
    test_pipeline_outputs()
