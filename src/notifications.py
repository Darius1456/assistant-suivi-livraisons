"""Module de Notifications et Gestion des Relances Automatisées (Étape 4).

Génère :
1. Les modèles d'emails professionnels prêts à l'envoi pour relancer les fournisseurs.
2. Les messages d'alertes internes pour l'acheteur (compatibles Slack / Teams / Email).
3. Le journal d'audit des relances envoyées (historique d'automatisation).
"""

import os
import csv
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("Notifications")

BUYER_SIGNATURE = """Cordialement,
Darius Kabore
Pôle Achats & Approvisionnements
Email : d.kabore@entreprise-demo.com | Tél : +33 1 40 00 00 00"""

LOG_SENT_FILE = "data/processed/sent_relances_log.csv"

def build_supplier_email_draft(order: dict) -> dict:
    """Rédige un modèle d'email professionnel personnalisé pour la commande concernée."""
    order_id = order.get("order_id", "CMD-XXXX")
    sup_name = order.get("supplier_name_clean", "Madame, Monsieur")
    item_id = order.get("item_id", "N/A")
    item_cat = order.get("item_category", "Composant")
    promised_dt = order.get("promised_date", "N/A")
    qty = order.get("order_qty", "N/A")
    days_due = order.get("days_until_promised", "N/A")

    subject = f"[SUIVI LIVRAISON] Commande {order_id} - Échéance du {promised_dt} - Confirmation d'expédition"

    body = f"""Bonjour {sup_name},

Nous nous permettons de vous contacter dans le cadre du suivi de notre commande référencée ci-dessous :

- Numéro de commande : {order_id}
- Référence article    : {item_id} ({item_cat})
- Quantité attendue    : {qty} unités
- Date de livraison convenue : {promised_dt} (dans {days_due} jours)

Dans le cadre de la sécurisation proactive de notre planning de production, nous souhaitons nous assurer que l'ordonnancement de cette commande se déroule conformément au calendrier convenu.

Pourriez-vous nous confirmer par retour de courriel que l'expédition est bien maintenue pour cette date, et le cas échéant, nous transmettre le numéro de suivi du transporteur ?

En vous remerciant pour votre collaboration habituelle,

{BUYER_SIGNATURE}
"""
    return {
        "order_id": order_id,
        "recipient": f"adv@{order.get('supplier_id', 'fournisseur').lower()}.com",
        "subject": subject,
        "body": body
    }

def record_sent_relance(order_id: str, supplier_name: str, recipient: str, subject: str, status: str = "Envoyé"):
    """Enregistre l'envoi d'une relance dans le journal d'audit d'automatisation."""
    os.makedirs(os.path.dirname(LOG_SENT_FILE), exist_ok=True)
    file_exists = os.path.exists(LOG_SENT_FILE)

    fieldnames = ["timestamp", "order_id", "supplier_name", "recipient", "subject", "status"]
    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "order_id": order_id,
        "supplier_name": supplier_name,
        "recipient": recipient,
        "subject": subject,
        "status": status
    }

    with open(LOG_SENT_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    logger.info(f"[LOG AUTOMATISATION] Relance enregistrée pour {order_id} ({recipient})")
    return row

def load_sent_relances() -> list[dict]:
    """Charge l'historique des relances envoyées."""
    if not os.path.exists(LOG_SENT_FILE):
        return []
    with open(LOG_SENT_FILE, mode="r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def build_internal_slack_alert(order: dict) -> dict:
    """Prépare un payload de notification interne pour l'acheteur."""
    urgency = order.get("urgency_score", "N/A")
    risk = order.get("v1_risk_score_pct", "N/A")
    return {
        "title": f"🚨 Alerte Approvisionnement : Commande {order.get('order_id')} à Risque ({risk}%)",
        "supplier": order.get("supplier_name_clean"),
        "item": f"{order.get('item_id')} ({order.get('item_criticality')})",
        "promised_date": order.get("promised_date"),
        "urgency_score": urgency,
        "recommended_action": order.get("action_title"),
        "alternative_supplier": order.get("recommended_alternative_supplier", "Non requis"),
        "key_risk_driver": order.get("v1_key_factor")
    }

def generate_all_alerts(
    prescriptions_path: str = "data/processed/prescriptions_open_orders.csv",
    output_path: str = "data/processed/generated_alerts.json"
):
    """Génère tous les brouillons d'emails et alertes pour les commandes requérant une action."""
    if not os.path.exists(prescriptions_path):
        raise FileNotFoundError(f"Fichier manquant : {prescriptions_path}")

    with open(prescriptions_path, mode="r", encoding="utf-8") as f:
        orders = list(csv.DictReader(f))

    # Filtrer les commandes à risque élevé ou moyen (ACT-03 et ACT-04)
    urgent_orders = [o for o in orders if o.get("action_code") in ["ACT-03", "ACT-04"]]

    alerts_payload = []
    for o in urgent_orders:
        email_draft = build_supplier_email_draft(o)
        slack_alert = build_internal_slack_alert(o)
        alerts_payload.append({
            "order_id": o["order_id"],
            "urgency_score": float(o["urgency_score"]),
            "email_draft": email_draft,
            "internal_alert": slack_alert
        })

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, mode="w", encoding="utf-8") as f:
        json.dump(alerts_payload, f, indent=2, ensure_ascii=False)

    logger.info(f"[SUCCÈS] {len(alerts_payload)} alertes et modèles d'emails générés : {output_path}")
    return alerts_payload

if __name__ == "__main__":
    generate_all_alerts()
