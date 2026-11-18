"""Générateur de données réalistes d'approvisionnement et de livraisons fournisseurs.

Produit un jeu de données simulant un ERP achats (commandes historiques livrées et commandes ouvertes en cours).
Conçu avec les modules natifs Python (zéro dépendance externe fragile).
"""

import os
import csv
import random
from datetime import datetime, timedelta

def generate_supplier_orders(n_orders: int = 700, output_path: str = "data/raw/orders_raw.csv", seed: int = 42):
    random.seed(seed)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Référentiel des 5 fournisseurs avec profils de ponctualité contrastés
    suppliers_profile = {
        "SUP-001": {
            "name": "Acme Components SAS",
            "name_variants": ["Acme Components SAS", "ACME COMPONENTS", "Acme Components"],
            "otd_target": 0.93,
            "delay_mean": 0.5,
            "delay_std": 1.0,
            "category": "Composant critique"
        },
        "SUP-002": {
            "name": "LogiTech Solutions Ltd",
            "name_variants": ["LogiTech Solutions Ltd", "logitech solutions", "LogiTech Solutions"],
            "otd_target": 0.82,
            "delay_mean": 1.8,
            "delay_std": 2.0,
            "category": "Électronique"
        },
        "SUP-003": {
            "name": "Global Metal Works",
            "name_variants": ["Global Metal Works", "GLOBAL METAL WORKS SA", "Global Metal Works "],
            "otd_target": 0.55,
            "delay_mean": 4.8,
            "delay_std": 3.5,
            "category": "Matière première"
        },
        "SUP-004": {
            "name": "FastTrack Packaging",
            "name_variants": ["FastTrack Packaging", "FastTrack Packaging SARL", "fasttrack packaging"],
            "otd_target": 0.72,
            "delay_mean": 2.5,
            "delay_std": 2.2,
            "category": "Emballage"
        },
        "SUP-005": {
            "name": "Apex Electronics Corp",
            "name_variants": ["Apex Electronics Corp", "APEX ELECTRONICS", "Apex Electronics Corp "],
            "otd_target": 0.42,
            "delay_mean": 7.0,
            "delay_std": 4.5,
            "category": "Composant critique"
        }
    }

    supplier_keys = list(suppliers_profile.keys())
    # Pondération des volumes de commandes par fournisseur
    supplier_weights = [0.25, 0.20, 0.22, 0.18, 0.15]

    ref_date = datetime(2026, 11, 4)  # Date d'aujourd'hui
    start_date = ref_date - timedelta(days=365)  # 12 derniers mois

    records = []

    for i in range(1, n_orders + 1):
        order_id = f"CMD-2026-{i:04d}"
        sup_id = random.choices(supplier_keys, weights=supplier_weights, k=1)[0]
        sup_meta = suppliers_profile[sup_id]

        # Variante de libellé fournisseur (pour tester le nettoyage ETL)
        supplier_name_raw = random.choice(sup_meta["name_variants"])

        # Date de passation
        days_offset = random.randint(0, 365)
        order_date = start_date + timedelta(days=days_offset)

        # Délai contractuel accordé (10 à 45 jours)
        contractual_lead_time = random.randint(10, 45)
        promised_date = order_date + timedelta(days=contractual_lead_time)

        # Statut de la commande
        if promised_date < (ref_date - timedelta(days=5)):
            status = "Delivered"
        else:
            open_statuses = ["Open", "Confirmed", "In Transit"]
            weights_status = [0.25, 0.50, 0.25]
            status = random.choices(open_statuses, weights=weights_status, k=1)[0]

        # Caractéristiques article
        item_category = sup_meta["category"]
        item_id = f"ITM-{sup_id[-3:]}-{random.randint(10, 99)}"
        qty = random.randint(10, 500)
        unit_price = round(random.uniform(15.0, 450.0), 2)
        total_eur = round(qty * unit_price, 2)

        # Criticité de la référence
        if item_category == "Composant critique":
            criticality = random.choices(["Haute", "Moyenne"], weights=[0.75, 0.25], k=1)[0]
        elif item_category == "Matière première":
            criticality = random.choices(["Haute", "Moyenne", "Basse"], weights=[0.4, 0.4, 0.2], k=1)[0]
        else:
            criticality = random.choices(["Moyenne", "Basse"], weights=[0.4, 0.6], k=1)[0]

        # Date de livraison réelle (si livrée)
        actual_delivery_date = ""
        if status == "Delivered":
            is_on_time = (random.random() < sup_meta["otd_target"])
            if is_on_time:
                # À l'heure ou légère avance (0 à 2 jours)
                advance_days = random.randint(0, 2)
                delivery_dt = promised_date - timedelta(days=advance_days)
            else:
                # En retard selon la distribution normale du fournisseur
                delay = max(1, int(random.gauss(sup_meta["delay_mean"], sup_meta["delay_std"])))
                delivery_dt = promised_date + timedelta(days=delay)
            actual_delivery_date = delivery_dt.strftime("%Y-%m-%d")

        records.append({
            "order_id": order_id,
            "supplier_id": sup_id,
            "supplier_name": supplier_name_raw,
            "item_id": item_id,
            "item_category": item_category,
            "item_criticality": criticality,
            "order_qty": qty,
            "unit_price_eur": unit_price,
            "order_total_eur": total_eur,
            "order_date": order_date.strftime("%Y-%m-%d"),
            "promised_date": promised_date.strftime("%Y-%m-%d"),
            "actual_delivery_date": actual_delivery_date,
            "status": status
        })

    # Injection intentionnelle de doublons pour tester l'étape de dédoublonnage de l'ETL
    dup_sample = random.sample(records, k=15)
    records.extend(dup_sample)

    fieldnames = [
        "order_id", "supplier_id", "supplier_name", "item_id", "item_category",
        "item_criticality", "order_qty", "unit_price_eur", "order_total_eur",
        "order_date", "promised_date", "actual_delivery_date", "status"
    ]

    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"[OK] Fichier brut g\u00e9n\u00e9r\u00e9 : {output_path} ({len(records)} lignes, dont 15 doublons inject\u00e9s)")
    return output_path

if __name__ == "__main__":
    generate_supplier_orders()
