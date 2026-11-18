"""Pipeline ETL : Nettoyage, Validation et Harmonisation des Données Achats.

Étape 1 du projet :
- Suppression des doublons
- Conversion & harmonisation des formats de dates
- Normalisation des identifiants et libellés fournisseurs
- Recalcul des écarts (delay_days, is_late, contractual_lead_time_days)
- Partitionnement : Historique clôturé vs Commandes ouvertes en cours
"""

import os
import csv
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("ETLPipeline")

# Référentiel canonique des fournisseurs
SUPPLIER_CANONICAL_NAMES = {
    "SUP-001": "Acme Components",
    "SUP-002": "LogiTech Solutions",
    "SUP-003": "Global Metal Works",
    "SUP-004": "FastTrack Packaging",
    "SUP-005": "Apex Electronics",
}

def parse_iso_date(date_str: str) -> datetime | None:
    """Parse une date au format YYYY-MM-DD en toute sécurité."""
    if not date_str or not date_str.strip():
        return None
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d")
    except ValueError:
        return None

def run_etl_pipeline(
    raw_path: str = "data/raw/orders_raw.csv",
    output_dir: str = "data/processed",
    reference_date_str: str = "2026-11-04"
):
    """Exécute l'ensemble du pipeline ETL Phase 1."""
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Fichier introuvable : {raw_path}")

    os.makedirs(output_dir, exist_ok=True)
    ref_date = datetime.strptime(reference_date_str, "%Y-%m-%d")

    logger.info("==================================================")
    logger.info("--- DÉMARRAGE DU PIPELINE ETL (PHASE 1) ---")
    logger.info("==================================================")

    with open(raw_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        raw_rows = list(reader)

    initial_count = len(raw_rows)
    logger.info(f"Fichier brut chargé ({raw_path}) : {initial_count} lignes.")

    # 1. Dédoublonnage sur 'order_id'
    seen_ids = set()
    deduped_rows = []
    duplicate_count = 0

    for row in raw_rows:
        oid = row.get("order_id", "").strip()
        if oid in seen_ids:
            duplicate_count += 1
            continue
        seen_ids.add(oid)
        deduped_rows.append(row)

    logger.info(f"Dédoublonnage : {duplicate_count} doublons supprimés ({len(deduped_rows)} lignes uniques conservées).")

    # 2 & 3. Harmonisation fournisseurs, conversion des dates et calcul des écarts
    history_records = []
    open_records = []
    incoherent_count = 0

    for row in deduped_rows:
        sup_id = row.get("supplier_id", "").strip().upper()
        clean_sup_name = SUPPLIER_CANONICAL_NAMES.get(sup_id, row.get("supplier_name", "").strip())

        order_dt = parse_iso_date(row.get("order_date"))
        promised_dt = parse_iso_date(row.get("promised_date"))
        actual_dt = parse_iso_date(row.get("actual_delivery_date"))

        # Contrôle de cohérence temporelle
        if order_dt and promised_dt and (promised_dt < order_dt):
            incoherent_count += 1
            logger.warning(f"Commande {row.get('order_id')} ignorée : date promise antérieure à la date de commande.")
            continue

        contractual_lead_time = (promised_dt - order_dt).days if (order_dt and promised_dt) else None
        days_until_promised = (promised_dt - ref_date).days if promised_dt else None

        processed_row = {
            "order_id": row.get("order_id", "").strip(),
            "supplier_id": sup_id,
            "supplier_name_raw": row.get("supplier_name", "").strip(),
            "supplier_name_clean": clean_sup_name,
            "item_id": row.get("item_id", "").strip(),
            "item_category": row.get("item_category", "").strip(),
            "item_criticality": row.get("item_criticality", "").strip(),
            "order_qty": int(row.get("order_qty", 0)),
            "unit_price_eur": float(row.get("unit_price_eur", 0.0)),
            "order_total_eur": float(row.get("order_total_eur", 0.0)),
            "order_date": row.get("order_date", "").strip(),
            "promised_date": row.get("promised_date", "").strip(),
            "actual_delivery_date": row.get("actual_delivery_date", "").strip(),
            "contractual_lead_time_days": contractual_lead_time,
            "days_until_promised": days_until_promised,
            "status": row.get("status", "").strip()
        }

        # 4. Partitionnement et métriques de retard
        if processed_row["status"] == "Delivered" and actual_dt and promised_dt:
            delay_days = (actual_dt - promised_dt).days
            is_late = 1 if delay_days > 0 else 0
            actual_lead_time = (actual_dt - order_dt).days if order_dt else None

            processed_row["delay_days"] = delay_days
            processed_row["is_late"] = is_late
            processed_row["actual_lead_time_days"] = actual_lead_time
            history_records.append(processed_row)
        else:
            # Commande en cours / ouverte
            processed_row["delay_days"] = ""
            processed_row["is_late"] = ""
            processed_row["actual_lead_time_days"] = ""
            open_records.append(processed_row)

    if incoherent_count > 0:
        logger.warning(f"Contrôles de cohérence : {incoherent_count} commandes incohérentes écartées.")

    # 5. Export des fichiers partitionnés
    history_file = os.path.join(output_dir, "history_cleaned.csv")
    open_file = os.path.join(output_dir, "open_orders.csv")

    fieldnames = [
        "order_id", "supplier_id", "supplier_name_clean", "supplier_name_raw",
        "item_id", "item_category", "item_criticality", "order_qty",
        "unit_price_eur", "order_total_eur", "order_date", "promised_date",
        "actual_delivery_date", "contractual_lead_time_days", "days_until_promised",
        "delay_days", "is_late", "actual_lead_time_days", "status"
    ]

    with open(history_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(history_records)

    with open(open_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(open_records)

    logger.info(f"[SUCCÈS] Historique clôturé : {history_file} ({len(history_records)} commandes)")
    logger.info(f"[SUCCÈS] Commandes ouvertes : {open_file} ({len(open_records)} commandes)")
    logger.info("==================================================")
    logger.info("--- PIPELINE ETL TERMINÉ AVEC SUCCÈS ---")
    logger.info("==================================================")

    return history_file, open_file

if __name__ == "__main__":
    run_etl_pipeline()
