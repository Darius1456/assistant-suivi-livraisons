"""Générateur automatique de la présentation PowerPoint (Soutenance Master 1).

Projet : Assistant de suivi prédictif des livraisons fournisseurs
Auteur : Darius Kabore · Master 1 Finance d'Entreprise, INSEEC Paris
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck(output_path="Presentation_Soutenance_Assistant_Predictif.pptx"):
    prs = Presentation()
    # Format 16:9 écran large standard
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6]

    # Palette de couleurs corporate & moderne
    C_NAVY = RGBColor(15, 23, 42)       # Slate 900
    C_BLUE = RGBColor(37, 99, 235)      # Royal Blue 600
    C_LIGHT_BG = RGBColor(248, 250, 252) # Slate 50
    C_WHITE = RGBColor(255, 255, 255)
    C_DARK = RGBColor(30, 41, 59)       # Slate 800
    C_MUTED = RGBColor(100, 116, 139)   # Slate 500
    C_GREEN = RGBColor(16, 185, 129)    # Emerald 500
    C_RED = RGBColor(239, 68, 68)       # Red 500
    C_CARD_BG = RGBColor(241, 245, 249) # Slate 100

    def add_header(slide, title_text, category_text="MASTER 1 FINANCE D'ENTREPRISE · INSEEC PARIS"):
        # Header banner text
        box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.1))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_cat = tf.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_BLUE

        p_tit = tf.add_paragraph()
        p_tit.text = title_text
        p_tit.font.size = Pt(26)
        p_tit.font.bold = True
        p_tit.font.color.rgb = C_NAVY

    def add_card(slide, left, top, width, height, bg_color=C_CARD_BG, border_color=None):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        if border_color:
            shape.line.color.rgb = border_color
            shape.line.width = Pt(1.5)
        else:
            shape.line.fill.background()
        return shape

    # =========================================================================
    # SLIDE 1 : Titre / Page de Garde
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = C_NAVY
    bg1.line.fill.background()

    # Badge Catégorie
    badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(1.5), Inches(4.5), Inches(0.5))
    badge.fill.solid()
    badge.fill.fore_color.rgb = C_BLUE
    badge.line.fill.background()
    tf_b = badge.text_frame
    p_b = tf_b.paragraphs[0]
    p_b.text = "PROJET IA & AUTOMATISATION SUPPLY CHAIN"
    p_b.font.size = Pt(12)
    p_b.font.bold = True
    p_b.font.color.rgb = C_WHITE
    p_b.alignment = PP_ALIGN.CENTER

    tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(11.3), Inches(3.2))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "Assistant de Suivi Prédictif\ndes Livraisons Fournisseurs"
    p1.font.size = Pt(40)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE

    p2 = tf1.add_paragraph()
    p2.text = "Anticipation des retards d'approvisionnement, réduction des ruptures et automatisation des relances"
    p2.font.size = Pt(18)
    p2.font.color.rgb = RGBColor(203, 213, 225)
    p2.space_before = Pt(16)

    # Auteur & Formation
    tb_auth = s1.shapes.add_textbox(Inches(1.0), Inches(5.8), Inches(11.3), Inches(1.0))
    tf_a = tb_auth.text_frame
    p_a1 = tf_a.paragraphs[0]
    p_a1.text = "Darius Kabore  ·  Master 1 Finance d'Entreprise, INSEEC Paris"
    p_a1.font.size = Pt(15)
    p_a1.font.bold = True
    p_a1.font.color.rgb = C_WHITE

    p_a2 = tf_a.add_paragraph()
    p_a2.text = "Projet final avec démonstrateur WebApp & Code source GitHub"
    p_a2.font.size = Pt(13)
    p_a2.font.color.rgb = C_MUTED

    # =========================================================================
    # SLIDE 2 : Contexte & Problématique Métier
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Le Constat Métier : Une Gestion Subie et Chronophage", "CONTEXTE & PROBLÉMATIQUE")

    # 3 colonnes de friction
    cards_data = [
        ("Le Workflow Actuel", "Suivi Manuel Fragmenté", [
            "Fichiers Excel multiples dispersés entre acheteurs",
            "Relances manuelles par email au coup par coup",
            "Manque de visibilité globale sur les commandes en cours",
            "Détection des retards constatée a posteriori le jour J"
        ], C_BLUE),
        ("Les Conséquences", "Impacts Opérationnels & Financiers", [
            "Ruptures de stock imprévues sur lignes de production",
            "Expéditions express coûteuses pour pallier l'urgence",
            "Augmentation artificielle du Besoin en Fonds de Roulement (BFR)",
            "Pénalités clients pour retards de livraison finaux"
        ], C_RED),
        ("L'Opportunité IA", "Du Réactif au Prédictif", [
            "Anticiper les retards plusieurs semaines avant l'échéance",
            "Scorer le risque fournisseur grâce aux historiques réels",
            "Automatiser les relances ciblées pour libérer du temps acheteur",
            "Proposer immédiatement des fournisseurs alternatifs qualifiés"
        ], C_GREEN)
    ]

    col_w = Inches(3.6)
    gap = Inches(0.4)
    start_x = Inches(0.8)

    for i, (tag, title, bullets, color) in enumerate(cards_data):
        x = start_x + i * (col_w + gap)
        add_card(s2, x, Inches(1.8), col_w, Inches(5.0), bg_color=C_WHITE, border_color=color)

        tb = s2.shapes.add_textbox(x + Inches(0.2), Inches(2.0), col_w - Inches(0.4), Inches(4.5))
        tf = tb.text_frame
        tf.word_wrap = True

        p_t = tf.paragraphs[0]
        p_t.text = tag.upper()
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = color

        p_h = tf.add_paragraph()
        p_h.text = title
        p_h.font.size = Pt(17)
        p_h.font.bold = True
        p_h.font.color.rgb = C_NAVY
        p_h.space_before = Pt(4)
        p_h.space_after = Pt(14)

        for b in bullets:
            p_b = tf.add_paragraph()
            p_b.text = f"•  {b}"
            p_b.font.size = Pt(13)
            p_b.font.color.rgb = C_DARK
            p_b.space_after = Pt(8)

    # =========================================================================
    # SLIDE 3 : Méthodologie Scientifique (X / Y / Z)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "La Démarche Scientifique : Le Cadre X / Y / Z", "MÉTHODOLOGIE DU MÉMOIRE")

    xyz_cards = [
        ("X", "Ce que l'on met en place", "Assistant Prédictif & Prescriptif", [
            "Pipeline d'ingestion et de nettoyage des données ERP",
            "Moteur de scoring de risque par Machine Learning",
            "Génération d'alertes ciblées et d'emails de relance",
            "Recommandation automatique de fournisseurs alternatifs"
        ], C_BLUE),
        ("Y", "Ce que l'on mesure", "Indicateurs de Performance Clés", [
            "Délai d'anticipation moyen (en jours avant la date promise)",
            "Taux de détection (Rappel des vrais retards)",
            "Taux de fausses alertes (Garde-fou contre le bruit)",
            "Ruptures de stock évitées et heures gagnées en suivi"
        ], C_GREEN),
        ("Z", "Comparé à quoi", "Statu Quo & Règle Manuelle v0", [
            "Suivi manuel actuel (Excel, emails, relances urgence)",
            "Baseline déterministe v0 : Retard hist. > 2j OU J-3",
            "Garde-fou central : Prouver que l'IA surpasse la règle simple sans inonder l'acheteur de fausses alertes"
        ], C_NAVY)
    ]

    for i, (letter, subtitle, header, bullets, color) in enumerate(xyz_cards):
        x = start_x + i * (col_w + gap)
        add_card(s3, x, Inches(1.8), col_w, Inches(5.0), bg_color=C_CARD_BG)

        # Badge lettre
        badge_l = s3.shapes.add_shape(MSO_SHAPE.OVAL, x + Inches(0.2), Inches(2.0), Inches(0.7), Inches(0.7))
        badge_l.fill.solid()
        badge_l.fill.fore_color.rgb = color
        badge_l.line.fill.background()
        tf_l = badge_l.text_frame
        p_l = tf_l.paragraphs[0]
        p_l.text = letter
        p_l.font.size = Pt(18)
        p_l.font.bold = True
        p_l.font.color.rgb = C_WHITE
        p_l.alignment = PP_ALIGN.CENTER

        tb = s3.shapes.add_textbox(x + Inches(0.2), Inches(2.9), col_w - Inches(0.4), Inches(3.6))
        tf = tb.text_frame
        tf.word_wrap = True

        p_s = tf.paragraphs[0]
        p_s.text = subtitle.upper()
        p_s.font.size = Pt(10)
        p_s.font.bold = True
        p_s.font.color.rgb = color

        p_h = tf.add_paragraph()
        p_h.text = header
        p_h.font.size = Pt(16)
        p_h.font.bold = True
        p_h.font.color.rgb = C_NAVY
        p_h.space_after = Pt(10)

        for b in bullets:
            p_b = tf.add_paragraph()
            p_b.text = f"•  {b}"
            p_b.font.size = Pt(12)
            p_b.font.color.rgb = C_DARK
            p_b.space_after = Pt(6)

    # =========================================================================
    # SLIDE 4 : Architecture Globale en 4 Étapes
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "L'Architecture Système : Du Fichier ERP à l'Action", "ARCHITECTURE TECHNIQUE")

    steps = [
        ("ÉTAPE 1", "Nettoyage & Harmonisation", "src/etl_pipeline.py", [
            "Dédoublonnage sur order_id",
            "Standardisation dates ISO",
            "Normalisation des fournisseurs",
            "Recalcul delay_days & is_late",
            "Partition Clôturées vs Ouvertes"
        ]),
        ("ÉTAPE 2", "Feature Store & Scorecard", "src/feature_engine.py", [
            "Calcul OTD historique (%)",
            "Retard moyen & volatilité",
            "Ratio de compression délai",
            "Criticité et enjeu financier",
            "Matrice de features sans fuite"
        ]),
        ("ÉTAPE 3", "Moteur IA & Benchmark", "src/risk_engine.py", [
            "Baseline v0 déterministe",
            "Modèle IA Random Forest",
            "Scoring de probabilité (0-100%)",
            "Explicabilité des causes clés",
            "Benchmark scientifique formel"
        ]),
        ("ÉTAPE 4", "Prescriptions & WebApp", "src/prescriptive_engine.py", [
            "Matrice Risque x Criticité",
            "Relances emails pré-remplies",
            "Fournisseurs alternatifs",
            "WebApp interactive Streamlit",
            "Journal d'audit horodaté"
        ])
    ]

    step_w = Inches(2.7)
    step_gap = Inches(0.25)
    s_x = Inches(0.8)

    for i, (num, title, script, points) in enumerate(steps):
        x = s_x + i * (step_w + step_gap)
        add_card(s4, x, Inches(1.8), step_w, Inches(5.0), bg_color=C_WHITE, border_color=C_BLUE)

        tb = s4.shapes.add_textbox(x + Inches(0.15), Inches(2.0), step_w - Inches(0.3), Inches(4.5))
        tf = tb.text_frame
        tf.word_wrap = True

        p_n = tf.paragraphs[0]
        p_n.text = num
        p_n.font.size = Pt(11)
        p_n.font.bold = True
        p_n.font.color.rgb = C_BLUE

        p_t = tf.add_paragraph()
        p_t.text = title
        p_t.font.size = Pt(15)
        p_t.font.bold = True
        p_t.font.color.rgb = C_NAVY
        p_t.space_before = Pt(3)

        p_sc = tf.add_paragraph()
        p_sc.text = script
        p_sc.font.size = Pt(10)
        p_sc.font.color.rgb = C_MUTED
        p_sc.space_after = Pt(12)

        for pt in points:
            p_p = tf.add_paragraph()
            p_p.text = f"✓  {pt}"
            p_p.font.size = Pt(12)
            p_p.font.color.rgb = C_DARK
            p_p.space_after = Pt(6)

    # =========================================================================
    # SLIDE 5 : Étape 1 - Pipeline de Nettoyage
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Étape 1 : Pipeline de Nettoyage & Harmonisation des Données", "DATA ENGINEERING")

    # Colonne gauche : Traitements
    add_card(s5, Inches(0.8), Inches(1.8), Inches(6.0), Inches(5.0), bg_color=C_WHITE, border_color=C_BLUE)
    tb_e1 = s5.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.4), Inches(4.5))
    tf_e1 = tb_e1.text_frame
    tf_e1.word_wrap = True

    p = tf_e1.paragraphs[0]
    p.text = "TRAITEMENTS ET CONTRÔLES APPLIQUÉS"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_BLUE

    items_e1 = [
        ("Dédoublonnage Strict :", "Élimination des lignes redondantes sur order_id (15 doublons détectés et purgés)."),
        ("Standardisation Temporelle :", "Conversion au format ISO YYYY-MM-DD et validation de cohérence (promised_date >= order_date)."),
        ("Harmonisation Fournisseurs :", "Normalisation des variantes de raison sociale (Acme SAS, ACME Ltd -> Acme Components)."),
        ("Calcul des Écarts Factuels :", "delay_days = actual_delivery - promised ; is_late = 1 si retard, 0 à l'heure."),
        ("Partitionnement Métier :", "Séparation stricte : 634 commandes livrées (historique) vs 66 commandes ouvertes actives.")
    ]

    for title_i, desc_i in items_e1:
        p_t = tf_e1.add_paragraph()
        p_t.text = title_i
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = C_NAVY
        p_t.space_before = Pt(8)

        p_d = tf_e1.add_paragraph()
        p_d.text = desc_i
        p_d.font.size = Pt(12)
        p_d.font.color.rgb = C_DARK

    # Colonne droite : Chiffres clés de l'étape
    metrics_e1 = [
        ("715", "Lignes brutes ERP injectées", C_NAVY),
        ("15", "Doublons purgés par l'algorithme", C_RED),
        ("634", "Commandes closes pour l'apprentissage", C_BLUE),
        ("66", "Commandes ouvertes actives à scorer", C_GREEN)
    ]

    card_y = Inches(1.8)
    for num, lbl, col in metrics_e1:
        add_card(s5, Inches(7.2), card_y, Inches(5.3), Inches(1.05), bg_color=C_CARD_BG)
        tb_m = s5.shapes.add_textbox(Inches(7.4), card_y + Inches(0.15), Inches(4.9), Inches(0.8))
        tf_m = tb_m.text_frame
        p_nm = tf_m.paragraphs[0]
        p_nm.text = num
        p_nm.font.size = Pt(26)
        p_nm.font.bold = True
        p_nm.font.color.rgb = col

        p_lb = tf_m.add_paragraph()
        p_lb.text = lbl
        p_lb.font.size = Pt(12)
        p_lb.font.color.rgb = C_DARK
        card_y += Inches(1.3)

    # =========================================================================
    # SLIDE 6 : Étape 2 - Scorecard Fournisseurs & Features
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Étape 2 : Feature Store & Scorecard de Fiabilité Fournisseurs", "ANALYTIQUE FOURNISSEURS")

    # Table récapitulative des 5 fournisseurs
    add_card(s6, Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0), bg_color=C_WHITE, border_color=C_BLUE)

    tb_tab = s6.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(11.1), Inches(4.5))
    tf_tab = tb_tab.text_frame
    tf_tab.word_wrap = True

    p_th = tf_tab.paragraphs[0]
    p_th.text = "PROFIL HISTORIQUE CONSOLIDÉ (SUR LES 634 COMMANDES CLÔTURÉES)"
    p_th.font.size = Pt(12)
    p_th.font.bold = True
    p_th.font.color.rgb = C_BLUE
    p_th.space_after = Pt(10)

    rows_supp = [
        ("SUP-001", "Acme Components", "Composant critique", "92.1 %", "7.9 %", "+1.1 j", "0.96 j", "10.46 M€", "🟢 Exemplaire"),
        ("SUP-002", "LogiTech Solutions", "Électronique", "80.0 %", "20.0 %", "+2.0 j", "1.48 j", "8.23 M€", "🟢 Fiable"),
        ("SUP-004", "FastTrack Packaging", "Emballage", "67.0 %", "33.0 %", "+2.7 j", "2.06 j", "6.72 M€", "🟠 Surveillé"),
        ("SUP-003", "Global Metal Works", "Matière première", "56.7 %", "43.3 %", "+4.7 j", "3.49 j", "8.18 M€", "🔴 Instable"),
        ("SUP-005", "Apex Electronics", "Composant critique", "42.3 %", "57.7 %", "+6.3 j", "4.69 j", "4.60 M€", "🔴 Critique")
    ]

    p_header = tf_tab.add_paragraph()
    p_header.text = f"{'Code':<9} | {'Fournisseur':<22} | {'Catégorie':<20} | {'OTD %':<9} | {'Retard Moyen':<14} | {'Volatilité':<11} | {'Dépense':<10} | Statut"
    p_header.font.size = Pt(11)
    p_header.font.bold = True
    p_header.font.color.rgb = C_NAVY
    p_header.space_after = Pt(6)

    for code, name, cat, otd, late, delay, vol, spend, stat in rows_supp:
        p_r = tf_tab.add_paragraph()
        p_r.text = f"{code:<9} | {name:<22} | {cat:<20} | {otd:<9} | {delay:<14} | {vol:<11} | {spend:<10} | {stat}"
        p_r.font.size = Pt(11)
        p_r.font.color.rgb = C_DARK
        p_r.space_after = Pt(4)

    p_exp = tf_tab.add_paragraph()
    p_exp.text = "\n💡 Feature Avancée Clé : Le Ratio de Compression de Délai (Lead Time Ratio)\nL'IA compare le délai contractuel exigé par l'acheteur au délai réel habituel du fournisseur. Si l'acheteur demande 15j à un fournisseur qui met historiquement 25j (ratio = 0.60x), le risque d'aléa explose !"
    p_exp.font.size = Pt(12)
    p_exp.font.bold = True
    p_exp.font.color.rgb = C_BLUE

    # =========================================================================
    # SLIDE 7 : Étape 3 - Le Benchmark Scientifique v0 vs v1
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Étape 3 : Benchmark Scientifique — Baseline v0 vs Modèle IA v1", "RÉSULTATS DE RECHERCHE X / Y / Z")

    # Cartes résultats clés
    res_cards = [
        ("- 66.7 %", "FAUSSES ALERTES (FPR)", "Division par 3 du bruit. La règle v0 alertait sur 100% des cas, saturant l'acheteur.", C_GREEN),
        ("+ 9.4 j", "ANTICIPATION DU RISQUE", "L'IA détecte le risque 17.6 jours avant la date promise (vs 8.2 jours pour la règle).", C_BLUE),
        ("+ 17.3 %", "PRÉCISION DES ALERTES", "Les alertes transmises sont ciblées et crédibles auprès des équipes opérationnelles.", C_NAVY)
    ]

    for i, (val, title, desc, col) in enumerate(res_cards):
        x = Inches(0.8) + i * (Inches(3.7) + Inches(0.3))
        add_card(s7, x, Inches(1.8), Inches(3.7), Inches(1.8), bg_color=C_WHITE, border_color=col)
        tb_rc = s7.shapes.add_textbox(x + Inches(0.2), Inches(1.9), Inches(3.3), Inches(1.5))
        tf_rc = tb_rc.text_frame
        tf_rc.word_wrap = True

        p_v = tf_rc.paragraphs[0]
        p_v.text = val
        p_v.font.size = Pt(32)
        p_v.font.bold = True
        p_v.font.color.rgb = col

        p_t = tf_rc.add_paragraph()
        p_t.text = title
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = C_NAVY

        p_d = tf_rc.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = C_DARK
        p_d.space_before = Pt(4)

    # Tableau comparatif formel
    add_card(s7, Inches(0.8), Inches(3.9), Inches(11.7), Inches(2.9), bg_color=C_CARD_BG)
    tb_cp = s7.shapes.add_textbox(Inches(1.1), Inches(4.1), Inches(11.1), Inches(2.5))
    tf_cp = tb_cp.text_frame
    tf_cp.word_wrap = True

    p_cph = tf_cp.paragraphs[0]
    p_cph.text = "SYNTHÈSE STATISTIQUE COMPARATIVE SUR JEU DE TEST HOLDOUT"
    p_cph.font.size = Pt(12)
    p_cph.font.bold = True
    p_cph.font.color.rgb = C_BLUE
    p_cph.space_after = Pt(8)

    comp_lines = [
        ("Métrique Évaluée (Y)", "Baseline v0 (Règle simple)", "Modèle IA v1 (Random Forest)", "Gain Démontré pour l'Entreprise"),
        ("Taux de Fausses Alertes (FPR)", "100.0 % (Bruit total)", "33.3 %", "Élimination radicale de la fatigue d'alerte"),
        ("Précision des Alertes", "29.1 %", "46.4 %", "+ 17.3 points de pertinence opérationnelle"),
        ("Délai d'Anticipation Moyen", "8.2 jours", "17.6 jours", "+ 9.4 jours de réaction précoce (> 2 semaines)"),
        ("Capacité Discriminante ROC-AUC", "N/A (Règle déterministe)", "0.735", "Modèle robuste et généralisable")
    ]

    for m, v0, v1, g in comp_lines:
        p_l = tf_cp.add_paragraph()
        p_l.text = f"{m:<32} | {v0:<24} | {v1:<26} | {g}"
        p_l.font.size = Pt(11)
        p_l.font.color.rgb = C_NAVY if m.startswith("Métrique") else C_DARK
        p_l.font.bold = True if m.startswith("Métrique") else False
        p_l.space_after = Pt(3)

    # =========================================================================
    # SLIDE 8 : Étape 4 - Moteur Prescriptif & Automatisation
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Étape 4 : De la Prédiction à l'Action Prescriptive", "AIDE À LA DÉCISION & AUTOMATISATION")

    cards_p = [
        ("Niveau 1 : Nominal", "Flux Sécurisé (< 35%)", "24 commandes", [
            "Risque faible, conformité standard",
            "Aucun temps acheteur gaspillé",
            "Suivi passif dans le tableau de bord"
        ], C_GREEN),
        ("Niveau 2 : Surveillance", "Risque Modéré (35-65%)", "28 commandes", [
            "Fournisseur à surveiller",
            "Pointage lors de la revue logistique hebdo",
            "Contrôle d'avancement à J-5"
        ], RGBColor(245, 158, 11)),
        ("Niveau 3 : Relance", "Risque Élevé (> 65%)", "5 commandes", [
            "Alerte prioritaire acheteur",
            "Génération immédiate de l'email de relance",
            "Demande formelle du numéro de suivi"
        ], C_RED),
        ("Niveau 4 : Contingence", "Critique & Rupture", "9 commandes", [
            "Composant critique + Risque élevé",
            "Relance urgente au fournisseur",
            "Orientation automatique vers l'alternative référencée (ex: Acme Components 92% OTD)"
        ], C_NAVY)
    ]

    for i, (lvl, title, vol, pts, col) in enumerate(cards_p):
        x = Inches(0.8) + i * (Inches(2.7) + Inches(0.3))
        add_card(s8, x, Inches(1.8), Inches(2.7), Inches(5.0), bg_color=C_WHITE, border_color=col)
        tb_p = s8.shapes.add_textbox(x + Inches(0.15), Inches(2.0), Inches(2.4), Inches(4.5))
        tf_p = tb_p.text_frame
        tf_p.word_wrap = True

        p_lv = tf_p.paragraphs[0]
        p_lv.text = lvl.upper()
        p_lv.font.size = Pt(10)
        p_lv.font.bold = True
        p_lv.font.color.rgb = col

        p_ti = tf_p.add_paragraph()
        p_ti.text = title
        p_ti.font.size = Pt(14)
        p_ti.font.bold = True
        p_ti.font.color.rgb = C_NAVY
        p_ti.space_before = Pt(3)

        p_vl = tf_p.add_paragraph()
        p_vl.text = vol
        p_vl.font.size = Pt(16)
        p_vl.font.bold = True
        p_vl.font.color.rgb = col
        p_vl.space_after = Pt(10)

        for pt in pts:
            p_pt = tf_p.add_paragraph()
            p_pt.text = f"•  {pt}"
            p_pt.font.size = Pt(11)
            p_pt.font.color.rgb = C_DARK
            p_pt.space_after = Pt(5)

    # =========================================================================
    # SLIDE 9 : Scénario de Démonstration en Direct
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Scénario de la Démonstration en Direct (Live Demo)", "APPLICATION INTERACTIVE STREAMLIT")

    demo_steps = [
        ("1. Vue d'Ensemble & Alertes", "Onglet 1 : Cockpit Opérationnel", [
            "Afficher les 66 commandes ouvertes scorées en temps réel",
            "Mettre en évidence les 14 commandes à risque élevé (Rouge)",
            "Filtrer par fournisseur critique (ex: Apex Electronics)"
        ]),
        ("2. Automatisation en 1 Clic", "Dispatch des Relances & Audit", [
            "Cliquer sur '🚀 Déclencher l'Envoi Groupé des Relances'",
            "Montrer l'historique tracé dans l'onglet '📜 Journal d'Audit'",
            "Ouvrir une commande pour afficher l'email pré-rempli et le fournisseur alternatif"
        ]),
        ("3. Simulateur Prédictif", "Onglet 2 : « What-If Analysis »", [
            "Simuler une commande fictive de 400 pièces à Apex Electronics avec 15j de délai",
            "L'IA calcule immédiatement le score de risque (> 75%)",
            "L'IA propose immédiatement l'alternative Acme Components (92% OTD)"
        ]),
        ("4. Démonstrateur Scientifique", "Onglet 5 : Validation Mémoire", [
            "Afficher le benchmark formel v0 vs v1 pour le jury",
            "Prouver le gain de 9.4 jours et la division des fausses alertes",
            "Visualiser le Top 5 des variables d'explicabilité de l'IA"
        ])
    ]

    for i, (title_d, sub_d, points_d) in enumerate(demo_steps):
        col_idx = i % 2
        row_idx = i // 2
        x = Inches(0.8) + col_idx * (Inches(5.7) + Inches(0.3))
        y = Inches(1.8) + row_idx * (Inches(2.4) + Inches(0.2))

        add_card(s9, x, y, Inches(5.7), Inches(2.4), bg_color=C_CARD_BG)
        tb_d = s9.shapes.add_textbox(x + Inches(0.2), y + Inches(0.15), Inches(5.3), Inches(2.1))
        tf_d = tb_d.text_frame
        tf_d.word_wrap = True

        p_td = tf_d.paragraphs[0]
        p_td.text = title_d
        p_td.font.size = Pt(14)
        p_td.font.bold = True
        p_td.font.color.rgb = C_BLUE

        p_sd = tf_d.add_paragraph()
        p_sd.text = sub_d
        p_sd.font.size = Pt(12)
        p_sd.font.bold = True
        p_sd.font.color.rgb = C_NAVY
        p_sd.space_after = Pt(6)

        for pd in points_d:
            p_p = tf_d.add_paragraph()
            p_p.text = f"→  {pd}"
            p_p.font.size = Pt(11)
            p_p.font.color.rgb = C_DARK
            p_p.space_after = Pt(2)

    # =========================================================================
    # SLIDE 10 : Impact Financier & ROI pour l'Entreprise
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Impact Financier & Retour sur Investissement (ROI)", "VALEUR POUR L'ENTREPRISE")

    roi_cards = [
        ("Optimisation du BFR", "Moins de Stocks Tampons", [
            "La visibilité prédictive permet de réduire les stocks de sécurité surdimensionnés.",
            "Moins de capitaux immobilisés dans des stocks de précaution passifs.",
            "Amélioration directe du cycle de conversion du cash (Cash Conversion Cycle)."
        ], C_BLUE),
        ("Réduction des Coûts d'Urgence", "Fret Express & Pénalités", [
            "Élimination des expéditions express de dernière minute en avion ou taxi-colis.",
            "Suppression des pénalités contractuelles de retard facturées par les clients finaux.",
            "Évite les arrêts de ligne de production dont le coût horaire est prohibitif."
        ], C_GREEN),
        ("Productivité Acheteurs", "Automatisation à Forte Valeur", [
            "Suppression de 4 à 6 heures hebdomadaires passées sur des relances manuelles Excel.",
            "L'acheteur se focalise sur les négociations et la sécurisation des contrats critiques.",
            "Système reproductible et déployable à l'échelle sur n'importe quel ERP (SAP, Cegid)."
        ], C_NAVY)
    ]

    for i, (title_r, sub_r, points_r, col_r) in enumerate(roi_cards):
        x = Inches(0.8) + i * (col_w + gap)
        add_card(s10, x, Inches(1.8), col_w, Inches(5.0), bg_color=C_WHITE, border_color=col_r)

        tb_r = s10.shapes.add_textbox(x + Inches(0.2), Inches(2.0), col_w - Inches(0.4), Inches(4.5))
        tf_r = tb_r.text_frame
        tf_r.word_wrap = True

        p_tr = tf_r.paragraphs[0]
        p_tr.text = title_r.upper()
        p_tr.font.size = Pt(11)
        p_tr.font.bold = True
        p_tr.font.color.rgb = col_r

        p_sr = tf_r.add_paragraph()
        p_sr.text = sub_r
        p_sr.font.size = Pt(16)
        p_sr.font.bold = True
        p_sr.font.color.rgb = C_NAVY
        p_sr.space_before = Pt(4)
        p_sr.space_after = Pt(14)

        for pr in points_r:
            p_p = tf_r.add_paragraph()
            p_p.text = f"✓  {pr}"
            p_p.font.size = Pt(13)
            p_p.font.color.rgb = C_DARK
            p_p.space_after = Pt(10)

    # =========================================================================
    # SLIDE 11 : Conclusion & Dépôt GitHub
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    bg11 = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg11.fill.solid()
    bg11.fill.fore_color.rgb = C_NAVY
    bg11.line.fill.background()

    tb_c = s11.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(4.5))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True

    p_c1 = tf_c.paragraphs[0]
    p_c1.text = "CONCLUSION & PERSPECTIVES"
    p_c1.font.size = Pt(14)
    p_c1.font.bold = True
    p_c1.font.color.rgb = C_BLUE

    p_c2 = tf_c.add_paragraph()
    p_c2.text = "Un Projet Complet, Validé et Prêt pour l'Entreprise"
    p_c2.font.size = Pt(34)
    p_c2.font.bold = True
    p_c2.font.color.rgb = C_WHITE
    p_c2.space_before = Pt(8)
    p_c2.space_after = Pt(16)

    points_c = [
        "Preuve empirique établie : l'IA apporte un gain décisif (+9.4j d'anticipation, division par 3 des fausses alertes).",
        "Système déployable immédiatement : pipeline modulaire, zéro dépendance fragile, code audité.",
        "Code source intégral hébergé publiquement sur GitHub : github.com/Darius1456/assistant-suivi-livraisons",
        "Perspectives futures : Intégration en temps réel aux flux ERP (SAP/Cegid) et suivi géolocalisé des transporteurs."
    ]

    for pc in points_c:
        p_it = tf_c.add_paragraph()
        p_it.text = f"•   {pc}"
        p_it.font.size = Pt(16)
        p_it.font.color.rgb = RGBColor(226, 232, 240)
        p_it.space_after = Pt(10)

    # Remerciements
    tb_th = s11.shapes.add_textbox(Inches(1.0), Inches(6.0), Inches(11.3), Inches(0.8))
    tf_th = tb_th.text_frame
    p_th = tf_th.paragraphs[0]
    p_th.text = "Merci pour votre attention. Place à la démonstration en direct et aux questions !"
    p_th.font.size = Pt(18)
    p_th.font.bold = True
    p_th.font.color.rgb = C_GREEN

    prs.save(output_path)
    print(f"[SUCCÈS] Présentation PowerPoint générée avec succès : {output_path}")
    return output_path

if __name__ == "__main__":
    create_deck()
