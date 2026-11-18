"""Script d'orchestration global : Exécute l'ensemble des étapes 1 à 4 de bout en bout."""

import sys
import logging
from src.etl_pipeline import run_etl_pipeline
from src.feature_engine import run_feature_engine
from src.risk_engine import run_risk_pipeline
from src.prescriptive_engine import run_prescriptive_engine
from src.notifications import generate_all_alerts

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("MasterOrchestrator")

def run_full_pipeline():
    logger.info("===================================================================")
    logger.info(">>> DÉMARRAGE DU PIPELINE COMPLET SUPPLY CHAIN PRÉDICTIF <<<")
    logger.info("===================================================================")

    # Étape 1 : Nettoyage et Harmonisation
    logger.info("[ÉTAPE 1/4] Nettoyage, Dédoublonnage & Harmonisation...")
    run_etl_pipeline()

    # Étape 2 : Moteur d'Indicateurs Historiques
    logger.info("[ÉTAPE 2/4] Calcul des KPIs Fournisseurs (OTD %, Retard moyen)...")
    run_feature_engine()

    # Étape 3 : Moteur Hybride de Risque & Benchmark v0 vs v1
    logger.info("[ÉTAPE 3/4] Modélisation IA, Scoring de Risque & Benchmark...")
    run_risk_pipeline()

    # Étape 4 : Moteur Prescriptif & Alertes
    logger.info("[ÉTAPE 4/4] Prescriptions d'actions & Génération des relances...")
    run_prescriptive_engine()
    generate_all_alerts()

    logger.info("===================================================================")
    logger.info(">>> TOUTES LES ÉTAPES ONT ÉTÉ EXÉCUTÉES AVEC SUCCÈS [OK] <<<")
    logger.info("Pour lancer le tableau de bord web :")
    logger.info("   streamlit run app/streamlit_app.py")
    logger.info("   (ou double-cliquer sur run_dashboard.bat)")
    logger.info("===================================================================")

if __name__ == "__main__":
    run_full_pipeline()
