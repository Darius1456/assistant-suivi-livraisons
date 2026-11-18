"""Script de test et de validation pour le Moteur Prescriptif et les Notifications (Phase 4)."""

import os
import csv
import json

def test_prescriptive_and_notifications():
    presc_path = "data/processed/prescriptions_open_orders.csv"
    alerts_path = "data/processed/generated_alerts.json"

    assert os.path.exists(presc_path), f"Fichier manquant : {presc_path}"
    assert os.path.exists(alerts_path), f"Fichier manquant : {alerts_path}"

    with open(presc_path, mode="r", encoding="utf-8") as f:
        prescriptions = list(csv.DictReader(f))

    with open(alerts_path, mode="r", encoding="utf-8") as f:
        alerts = json.load(f)

    # 1. Vérification du tri par score d'urgence
    scores = [float(p["urgency_score"]) for p in prescriptions]
    assert scores == sorted(scores, reverse=True), "Erreur : Les commandes ne sont pas triées par urgence !"

    # 2. Vérification des actions
    act_counts = {}
    for p in prescriptions:
        code = p["action_code"]
        act_counts[code] = act_counts.get(code, 0) + 1

    print("==================================================")
    print("=== SYNTHÈSE DES ACTIONS PRESCRIPTIVES (PHASE 4) ===")
    print("==================================================")
    print(f"- ACT-04 (Plan de contingence & Alternative) : {act_counts.get('ACT-04', 0)} commandes")
    print(f"- ACT-03 (Relance proactive fournisseur)     : {act_counts.get('ACT-03', 0)} commandes")
    print(f"- ACT-02 (Surveillance hebdomadaire)         : {act_counts.get('ACT-02', 0)} commandes")
    print(f"- ACT-01 (Flux nominal sécurisé)             : {act_counts.get('ACT-01', 0)} commandes")
    print(f"- Total commandes ouvertes analysées         : {len(prescriptions)}")
    print("--------------------------------------------------")
    print(f"- Nombre d'emails de relance générés         : {len(alerts)}")

    # 3. Aperçu du premier email généré
    top_alert = alerts[0]["email_draft"]
    print(f"\n[EXEMPLE D'EMAIL PRÉ-REMPLI GÉNÉRÉ]")
    print(f"Objet : {top_alert['subject']}")
    print(f"Destinataire : {top_alert['recipient']}")
    print(f"Début du corps : {top_alert['body'][:180]}...")
    print("==================================================")
    print("=== VALIDATION DU MOTEUR PRESCRIPTIF RÉUSSIE [OK] ===")
    print("==================================================")

if __name__ == "__main__":
    test_prescriptive_and_notifications()
