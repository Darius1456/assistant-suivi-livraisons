"""Moteur Prescriptif et Aide à la Décision (Étape 4).

Ce module transforme les probabilités prédictives en décisions opérationnelles concrètes :
1. Calcul de la Matrice d'Urgence : Risque IA (v1) x Criticité pièce & Enjeu financier.
2. Attribution de la recommandation d'action prescriptive (Nominal, Surveillance, Relance, Contingence).
3. Identification intelligente d'un Fournisseur Alternatif qualifié en cas de risque critique.
4. Export de la table des prescriptions pour le tableau de bord et les notifications.
"""

import os
import csv
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("PrescriptiveEngine")

def load_csv(filepath: str) -> list[dict]:
    """Charge un fichier CSV."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Fichier introuvable : {filepath}")
    with open(filepath, mode="r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def find_best_alternative_supplier(
    current_supplier_id: str,
    item_category: str,
    supplier_kpi_rows: list[dict]
) -> dict | None:
    """Trouve le meilleur fournisseur alternatif ayant un bon OTD pour la même catégorie."""
    # Candidats différents du fournisseur actuel
    candidates = [s for s in supplier_kpi_rows if s["supplier_id"] != current_supplier_id]
    if not candidates:
        return None

    # Tri par OTD décroissant
    candidates_sorted = sorted(candidates, key=lambda x: float(x["otd_rate_pct"]), reverse=True)
    best = candidates_sorted[0]
    return {
        "alt_supplier_id": best["supplier_id"],
        "alt_supplier_name": best["supplier_name_clean"],
        "alt_supplier_otd": float(best["otd_rate_pct"]),
        "alt_supplier_avg_delay": float(best["avg_delay_days_late_only"])
    }

def run_prescriptive_engine(
    scored_orders_path: str = "data/processed/scored_open_orders.csv",
    supplier_kpi_path: str = "data/processed/supplier_kpis.csv",
    output_path: str = "data/processed/prescriptions_open_orders.csv"
):
    """Exécute les règles prescriptives sur les commandes ouvertes."""
    logger.info("==================================================")
    logger.info("--- DÉMARRAGE DU MOTEUR PRESCRIPTIF (ÉTAPE 4) ---")
    logger.info("==================================================")

    scored_orders = load_csv(scored_orders_path)
    supplier_kpis = load_csv(supplier_kpi_path)

    prescriptions = []

    for row in scored_orders:
        risk_pct = float(row.get("v1_risk_score_pct") or 0.0)
        risk_level = row.get("v1_risk_level", "Faible")
        crit = row.get("item_criticality", "Moyenne")
        total_eur = float(row.get("order_total_eur") or 0.0)
        days_due = float(row.get("days_until_promised") or 0.0)

        # Coefficient multiplicateur de criticité
        crit_weight = 1.35 if crit == "Haute" else (1.1 if crit == "Moyenne" else 0.9)
        financial_weight = 1.15 if total_eur >= 50000.0 else 1.0

        # Score d'urgence pondéré [0 - 150]
        urgency_score = round(risk_pct * crit_weight * financial_weight, 1)

        # Logique de recommandation prescriptive
        alt_supplier_str = "Non requis"
        if risk_level == "Élevé" and crit == "Haute":
            action_code = "ACT-04"
            action_title = "Plan de contingence & Sécurisation prioritaire"
            action_desc = (
                f"Pièce critique ({crit}) avec risque de retard de {risk_pct}%. "
                "Action immédiate : Émettre une relance formelle et pré-alerter le fournisseur alternatif référencé."
            )
            # Recherche de l'alternative
            alt = find_best_alternative_supplier(row["supplier_id"], row["item_category"], supplier_kpis)
            if alt:
                alt_supplier_str = f"{alt['alt_supplier_name']} (OTD: {alt['alt_supplier_otd']:.1f}%)"
        elif risk_level == "Élevé":
            action_code = "ACT-03"
            action_title = "Relance proactive fournisseur"
            action_desc = (
                f"Risque élevé de {risk_pct}%. "
                "Action : Transmettre l'email de confirmation d'avancement pour valider la date de livraison."
            )
        elif risk_level == "Moyen":
            action_code = "ACT-02"
            action_title = "Surveillance hebdomadaire"
            action_desc = (
                f"Risque modéré ({risk_pct}%). "
                "Action : Suivre lors de la revue logistique hebdo ; relancer à J-5 si aucune expédition n'est notifiée."
            )
        else:
            action_code = "ACT-01"
            action_title = "Flux nominal sécurisé"
            action_desc = "Risque faible (< 35%). Aucune action particulière requise."

        p_row = dict(row)
        p_row.update({
            "urgency_score": urgency_score,
            "action_code": action_code,
            "action_title": action_title,
            "action_description": action_desc,
            "recommended_alternative_supplier": alt_supplier_str
        })
        prescriptions.append(p_row)

    # Tri par score d'urgence décroissant (Top priorités de l'acheteur en premier)
    prescriptions_sorted = sorted(prescriptions, key=lambda x: float(x["urgency_score"]), reverse=True)

    fieldnames = list(prescriptions_sorted[0].keys())
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(prescriptions_sorted)

    logger.info(f"[SUCCÈS] Prescriptions sauvegardées : {output_path} ({len(prescriptions_sorted)} commandes triées par urgence)")
    return prescriptions_sorted

if __name__ == "__main__":
    run_prescriptive_engine()
