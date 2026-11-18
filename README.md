# Assistant de Suivi Prédictif des Livraisons Fournisseurs
## Projet IA & Automatisation Supply Chain Achats

**Auteur :** Darius Kabore · Master 1 Finance d'Entreprise, INSEEC Paris  
**Objectif :** Anticiper les retards de livraison fournisseurs avant la date promise, réduire les risques de ruptures de stock et automatiser les relances opérationnelles.

---

## 1. Architecture Fonctionnelle du Projet (4 Étapes)

```
┌────────────────────────────────────────────────────────────────────────┐
│                        0. FLUX ENTRANT ERP                             │
│ Fichier brut : data/raw/orders_raw.csv (700+ commandes, 5 fournisseurs)│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│         ÉTAPE 1 : PIPELINE DE NETTOYAGE & HARMONISATION                │
│ - Dédoublonnage sur order_id (15 doublons éliminés)                    │
│ - Standardisation des dates au format ISO YYYY-MM-DD                   │
│ - Normalisation des libellés fournisseurs via supplier_id              │
│ - Recalcul des retards réels (delay_days, is_late, lead_time)          │
│ -> data/processed/history_cleaned.csv (634 cmd closes)                 │
│ -> data/processed/open_orders.csv (66 cmd ouvertes)                    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│         ÉTAPE 2 : MOTEUR D'INDICATEURS HISTORIQUES (FEATURE STORE)     │
│ - Scorecard des 5 fournisseurs : OTD %, Retard moyen, Volatilité       │
│ - Tension sur les délais : Ratio (délai accordé / délai habituel)      │
│ - Enrichissement sans fuite de données (anti-leakage)                  │
│ -> data/processed/supplier_kpis.csv                                    │
│ -> data/processed/features_open_orders.csv                             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│         ÉTAPE 3 : MOTEUR HYBRIDE D'ALERTES & BENCHMARK IA              │
│ - Baseline v0 : Règle déterministe (Retard hist. > 2j OU J-3)          │
│ - Modèle IA v1 : Random Forest prédisant P(Retard > 0) de 0 à 100%     │
│ - Benchmark comparatif sur jeu de test holdout :                       │
│   * Division par 3 des fausses alertes (-66.7 points de FPR)           │
│   * Gain de +9.4 jours d'anticipation par rapport à la règle           │
│ -> data/processed/benchmark_results.json                               │
│ -> data/processed/scored_open_orders.csv                               │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│         ÉTAPE 4 : MOTEUR PRESCRIPTIF & TABLEAU DE BORD STREAMLIT       │
│ - Matrice d'Urgence : Risque IA x Criticité pièce & Enjeu financier    │
│ - Prescriptions d'actions intelligentes (Nominal, Relance, Alternative)│
│ - Génération automatique des emails de relance pré-remplis             │
│ - Application Web interactive Streamlit                                │
│ -> data/processed/prescriptions_open_orders.csv                        │
│ -> data/processed/generated_alerts.json                               │
│ -> app/streamlit_app.py                                                │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Benchmark Scientifique (Livrable Mémoire X / Y / Z)

| Métrique Métier (Y) | Baseline v0 (Règle simple) | Modèle IA v1 (Machine Learning) | Valeur Ajoutée Démontrée |
| :--- | :---: | :---: | :--- |
| **Garde-fou : Faux Positifs (Fausses alertes)** | **100.0%** *(bruit total)* | **33.3%** | **$-66.7$ points** *(suppression de la fatigue d'alerte)* |
| **Précision des Alertes** | 29.1% | **46.4%** | **$+17.3$ points** |
| **Délai Moyen d'Anticipation** | 8.2 jours | **17.6 jours** | **$+9.4$ jours** *(action précoce > 2 semaines)* |
| **ROC-AUC** | *Non applicable* | **0.735** | Modèle discriminant et robuste |

---

## 3. Lancement de l'Application

### Option 1 : Lancement direct par script Batch (Windows)
Double-cliquer sur le fichier :
```cmd
run_dashboard.bat
```

### Option 2 : Lancement en ligne de commande
```bash
streamlit run app/streamlit_app.py
```

### Rejouer l'ensemble du pipeline (Étapes 1 à 4)
```bash
python run_all_pipeline.py
```
