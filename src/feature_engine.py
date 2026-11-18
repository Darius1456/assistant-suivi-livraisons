"""Moteur d'Indicateurs Historiques et Feature Engineering (Étape 2).

Ce module :
1. Calcule les indicateurs historiques de performance par fournisseur (OTD %, Retard moyen, Écart-type, Taux de retard).
2. Construit les features analytiques avancées pour les commandes ouvertes (ratio de tension sur le délai, urgence, criticité).
3. Exporte les tables enrichies prêtes pour le moteur d'évaluation des risques (Étape 3).
"""

import os
import csv
import math
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("FeatureEngine")

def load_csv_data(filepath: str) -> list[dict]:
    """Charge un fichier CSV sous forme de liste de dictionnaires."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Fichier manquant : {filepath}")
    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def save_csv_data(filepath: str, data: list[dict], fieldnames: list[str]):
    """Sauvegarde une liste de dictionnaires dans un fichier CSV."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def compute_supplier_kpis(history_rows: list[dict]) -> dict[str, dict]:
    """Calcule les indicateurs historiques clés pour chaque fournisseur."""
    suppliers_data = {}

    for row in history_rows:
        sup_id = row["supplier_id"]
        if sup_id not in suppliers_data:
            suppliers_data[sup_id] = {
                "supplier_id": sup_id,
                "supplier_name_clean": row["supplier_name_clean"],
                "delays": [],
                "lead_times": [],
                "is_late_list": [],
                "critical_orders_count": 0,
                "total_eur_spent": 0.0
            }

        delay = float(row["delay_days"])
        is_late = int(row["is_late"])
        lead_time = float(row["actual_lead_time_days"]) if row.get("actual_lead_time_days") else 0.0
        order_total = float(row.get("order_total_eur", 0.0))

        suppliers_data[sup_id]["delays"].append(delay)
        suppliers_data[sup_id]["lead_times"].append(lead_time)
        suppliers_data[sup_id]["is_late_list"].append(is_late)
        suppliers_data[sup_id]["total_eur_spent"] += order_total

        if row.get("item_criticality") == "Haute":
            suppliers_data[sup_id]["critical_orders_count"] += 1

    supplier_kpi_map = {}

    for sup_id, s in suppliers_data.items():
        total_orders = len(s["delays"])
        late_orders = sum(s["is_late_list"])
        on_time_orders = total_orders - late_orders
        
        otd_pct = round((on_time_orders / total_orders) * 100, 2)
        late_rate_pct = round((late_orders / total_orders) * 100, 2)

        # Retard moyen sur l'ensemble des commandes
        avg_delay_all = round(sum(s["delays"]) / total_orders, 2)
        
        # Retard moyen conditionnel (sur les commandes en retard uniquement)
        late_delays = [d for d in s["delays"] if d > 0]
        avg_delay_late_only = round(sum(late_delays) / len(late_delays), 2) if late_delays else 0.0
        max_delay = max(s["delays"]) if s["delays"] else 0.0

        # Écart-type du retard (volatilité)
        variance = sum((d - avg_delay_all) ** 2 for d in s["delays"]) / total_orders
        std_delay = round(math.sqrt(variance), 2)

        # Délai moyen réel de livraison (Lead time physique moyen)
        avg_lead_time = round(sum(s["lead_times"]) / total_orders, 2)

        supplier_kpi_map[sup_id] = {
            "supplier_id": sup_id,
            "supplier_name_clean": s["supplier_name_clean"],
            "total_orders_delivered": total_orders,
            "on_time_orders": on_time_orders,
            "late_orders": late_orders,
            "otd_rate_pct": otd_pct,
            "late_rate_pct": late_rate_pct,
            "avg_delay_days_all": avg_delay_all,
            "avg_delay_days_late_only": avg_delay_late_only,
            "max_delay_days": max_delay,
            "std_delay_days": std_delay,
            "avg_actual_lead_time_days": avg_lead_time,
            "critical_orders_count": s["critical_orders_count"],
            "total_spend_eur": round(s["total_eur_spent"], 2)
        }

    return supplier_kpi_map

def enrich_orders_with_features(
    orders: list[dict],
    supplier_kpi_map: dict[str, dict],
    is_training_set: bool = False
) -> list[dict]:
    """Enrichit chaque commande avec les indicateurs fournisseur et des variables explicatives avancées."""
    enriched = []

    for row in orders:
        sup_id = row["supplier_id"]
        sup_kpis = supplier_kpi_map.get(sup_id, {})

        contractual_lt = float(row.get("contractual_lead_time_days") or 0.0)
        hist_avg_lt = sup_kpis.get("avg_actual_lead_time_days", contractual_lt or 20.0)

        # Ratio de tension sur le délai :
        # Si contractual_lt < hist_avg_lt -> l'acheteur a demandé un délai plus court que la moyenne réelle du fournisseur !
        lead_time_compression_ratio = round(contractual_lt / max(1.0, hist_avg_lt), 3)

        # Features de calendrier
        order_dt = datetime.strptime(row["order_date"], "%Y-%m-%d")
        promised_dt = datetime.strptime(row["promised_date"], "%Y-%m-%d")

        item_crit = row.get("item_criticality", "Moyenne")
        crit_score = 3 if item_crit == "Haute" else (2 if item_crit == "Moyenne" else 1)

        enriched_row = dict(row)
        enriched_row.update({
            # KPIs historiques du fournisseur
            "supplier_otd_pct": sup_kpis.get("otd_rate_pct", 75.0),
            "supplier_late_rate_pct": sup_kpis.get("late_rate_pct", 25.0),
            "supplier_avg_delay_all": sup_kpis.get("avg_delay_days_all", 0.0),
            "supplier_avg_delay_late_only": sup_kpis.get("avg_delay_days_late_only", 0.0),
            "supplier_std_delay": sup_kpis.get("std_delay_days", 0.0),
            "supplier_avg_actual_lead_time": hist_avg_lt,
            "supplier_delivered_count": sup_kpis.get("total_orders_delivered", 0),
            
            # Variables de tension opérationnelle de la commande
            "lead_time_compression_ratio": lead_time_compression_ratio,
            "order_month": order_dt.month,
            "order_day_of_week": order_dt.weekday(),
            "promised_month": promised_dt.month,
            "criticality_score": crit_score
        })

        enriched.append(enriched_row)

    return enriched

def run_feature_engine(
    history_path: str = "data/processed/history_cleaned.csv",
    open_path: str = "data/processed/open_orders.csv",
    output_dir: str = "data/processed"
):
    """Exécute l'ensemble du Moteur d'Indicateurs Historiques (Étape 2)."""
    logger.info("==================================================")
    logger.info("--- DÉMARRAGE DU FEATURE ENGINE (ÉTAPE 2) ---")
    logger.info("==================================================")

    # 1. Chargement des données de l'Étape 1
    history_rows = load_csv_data(history_path)
    open_rows = load_csv_data(open_path)
    logger.info(f"Données chargées : {len(history_rows)} historiques, {len(open_rows)} commandes ouvertes.")

    # 2. Calcul des indicateurs historiques par fournisseur
    supplier_kpi_map = compute_supplier_kpis(history_rows)
    logger.info(f"Indicateurs calculés pour {len(supplier_kpi_map)} fournisseurs.")

    # Export de la Scorecard Fournisseurs
    supplier_kpi_list = list(supplier_kpi_map.values())
    supplier_kpi_file = os.path.join(output_dir, "supplier_kpis.csv")
    kpi_fields = [
        "supplier_id", "supplier_name_clean", "total_orders_delivered",
        "on_time_orders", "late_orders", "otd_rate_pct", "late_rate_pct",
        "avg_delay_days_all", "avg_delay_days_late_only", "max_delay_days",
        "std_delay_days", "avg_actual_lead_time_days", "critical_orders_count",
        "total_spend_eur"
    ]
    save_csv_data(supplier_kpi_file, supplier_kpi_list, kpi_fields)
    logger.info(f"[SUCCÈS] Scorecard Fournisseurs sauvegardée : {supplier_kpi_file}")

    # 3. Enrichissement des jeux de données
    enriched_history = enrich_orders_with_features(history_rows, supplier_kpi_map, is_training_set=True)
    enriched_open = enrich_orders_with_features(open_rows, supplier_kpi_map, is_training_set=False)

    history_features_file = os.path.join(output_dir, "features_history.csv")
    open_features_file = os.path.join(output_dir, "features_open_orders.csv")

    feature_fields = list(enriched_history[0].keys())
    save_csv_data(history_features_file, enriched_history, feature_fields)
    save_csv_data(open_features_file, enriched_open, feature_fields)

    logger.info(f"[SUCCÈS] Historique enrichi sauvegardé : {history_features_file} ({len(enriched_history)} lignes)")
    logger.info(f"[SUCCÈS] Commandes ouvertes enrichies : {open_features_file} ({len(enriched_open)} lignes)")
    logger.info("==================================================")
    logger.info("--- FEATURE ENGINE TERMINÉ AVEC SUCCÈS ---")
    logger.info("==================================================")

    return supplier_kpi_file, history_features_file, open_features_file

if __name__ == "__main__":
    run_feature_engine()
