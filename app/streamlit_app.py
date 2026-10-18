"""
streamlit_app.py — Interface principale de ProPrism.

Application Streamlit permettant de prédire la durée et le coût d'un
projet informatique à partir d'un cahier des charges PDF.
"""

import os

import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from config import (
    DEFAULT_FEATURES,
    METHODOLOGIES,
    SECTEURS,
    TYPES_PROJETS,
    VALIDATION_RANGES,
)
from modules.llm_extractor import extract_features, extract_text_from_pdf
from modules.predictor import load_models, predict

# Chargement des variables d'environnement depuis .env
load_dotenv()

# ---------------------------------------------------------------------------
# Configuration de la page
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="ProPrism — Estimation Prédictive",
    page_icon="📊",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Chargement des modèles (mis en cache pour ne charger qu'une seule fois)
# ---------------------------------------------------------------------------


@st.cache_resource
def charger_modeles():
    """Charge les modèles Random Forest et les encodeurs depuis les fichiers .pkl."""
    return load_models()


# ---------------------------------------------------------------------------
# En-tête principal
# ---------------------------------------------------------------------------

st.title("📊 ProPrism — Estimation Prédictive de Projets Informatiques")
st.markdown(
    """
    Uploadez un **cahier des charges PDF** pour extraire automatiquement les
    caractéristiques de votre projet, puis obtenez une prédiction de sa
    **durée** (jours ouvrables) et de son **coût** (MAD) grâce à nos modèles
    Random Forest entraînés sur des données réelles.
    """
)

# Tentative de chargement des modèles
try:
    modele_duree, modele_cout, encodeurs = charger_modeles()
    modeles_disponibles = True
except FileNotFoundError as exc:
    st.error(
        f"⚠️ Modèles introuvables : {exc}\n\n"
        "Déposez `model_duree.pkl`, `model_cout.pkl` et `encoders.pkl` "
        "dans le dossier `app/models/` puis relancez l'application."
    )
    modeles_disponibles = False

# ---------------------------------------------------------------------------
# Initialisation du session state
# ---------------------------------------------------------------------------

if "extracted_features" not in st.session_state:
    st.session_state.extracted_features = None

if "prediction_result" not in st.session_state:
    st.session_state.prediction_result = None

# ---------------------------------------------------------------------------
# Sidebar — Upload PDF et extraction
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("📂 Cahier des charges")

    fichier_pdf = st.file_uploader(
        label="Uploader un fichier PDF (max 10 Mo)",
        type=["pdf"],
        help="Le texte sera analysé par Gemini pour extraire les caractéristiques du projet.",
    )

    # Vérification de la taille du fichier (10 Mo max)
    if fichier_pdf is not None and fichier_pdf.size > 10 * 1024 * 1024:
        st.error("Le fichier dépasse la limite de 10 Mo.")
        fichier_pdf = None

    bouton_extraction = st.button(
        "🔍 Extraire les features du PDF",
        disabled=(fichier_pdf is None),
        use_container_width=True,
    )

    if bouton_extraction and fichier_pdf is not None:
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            st.error(
                "Clé API Gemini manquante. "
                "Renseignez GEMINI_API_KEY dans votre fichier .env."
            )
        else:
            with st.spinner("Analyse du PDF par Gemini en cours…"):
                try:
                    texte_pdf = extract_text_from_pdf(fichier_pdf.read())
                    features_extraites = extract_features(texte_pdf, api_key)
                except ValueError as exc:
                    features_extraites = {"error": str(exc)}

            if "error" in features_extraites:
                st.error(f"Erreur lors de l'extraction : {features_extraites['error']}")
                # On conserve quand même les valeurs (defaults) pour le formulaire
                st.session_state.extracted_features = {
                    k: v for k, v in features_extraites.items() if k != "error"
                }
            else:
                st.session_state.extracted_features = features_extraites
                st.success("✅ Features extraites avec succès !")
                st.session_state.prediction_result = None  # réinitialiser

    # Badge de statut
    if st.session_state.extracted_features is not None:
        st.info("📋 Features chargées — vérifiez le formulaire à droite.")

    st.divider()
    st.markdown(
        "**Clé API Gemini (gratuite) :**  \n"
        "[aistudio.google.com](https://aistudio.google.com/)"
    )

# ---------------------------------------------------------------------------
# Récupération des valeurs courantes (extraites ou défauts)
# ---------------------------------------------------------------------------

vals = st.session_state.extracted_features or DEFAULT_FEATURES

# ---------------------------------------------------------------------------
# Colonnes principales
# ---------------------------------------------------------------------------

col_gauche, col_droite = st.columns([1, 1], gap="large")

# ---- COLONNE GAUCHE — Formulaire des 12 features -------------------------

with col_gauche:
    st.subheader("⚙️ Caractéristiques du projet")

    with st.form("formulaire_features"):
        # Variables catégorielles
        type_projet = st.selectbox(
            "Type de projet",
            options=TYPES_PROJETS,
            index=TYPES_PROJETS.index(vals.get("type_projet", "Web")),
        )

        secteur = st.selectbox(
            "Secteur d'activité",
            options=SECTEURS,
            index=SECTEURS.index(vals.get("secteur", "Tech")),
        )

        methodologie = st.selectbox(
            "Méthodologie",
            options=METHODOLOGIES,
            index=METHODOLOGIES.index(vals.get("methodologie", "Agile")),
        )

        st.divider()

        # Variables numériques — ligne 1
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            nb_modules = st.number_input(
                "Nombre de modules",
                min_value=VALIDATION_RANGES["nb_modules"]["min"],
                max_value=VALIDATION_RANGES["nb_modules"]["max"],
                value=int(vals.get("nb_modules", 8)),
                step=1,
            )
            taille_equipe = st.number_input(
                "Taille de l'équipe",
                min_value=VALIDATION_RANGES["taille_equipe"]["min"],
                max_value=VALIDATION_RANGES["taille_equipe"]["max"],
                value=int(vals.get("taille_equipe", 6)),
                step=1,
            )
            nb_livrables = st.number_input(
                "Nombre de livrables",
                min_value=VALIDATION_RANGES["nb_livrables"]["min"],
                max_value=VALIDATION_RANGES["nb_livrables"]["max"],
                value=int(vals.get("nb_livrables", 12)),
                step=1,
            )
            experience_chef = st.number_input(
                "Expérience chef de projet (ans)",
                min_value=VALIDATION_RANGES["experience_chef"]["min"],
                max_value=VALIDATION_RANGES["experience_chef"]["max"],
                value=int(vals.get("experience_chef", 5)),
                step=1,
            )

        with col_f2:
            nb_utilisateurs = st.number_input(
                "Nombre d'utilisateurs",
                min_value=VALIDATION_RANGES["nb_utilisateurs"]["min"],
                max_value=VALIDATION_RANGES["nb_utilisateurs"]["max"],
                value=int(vals.get("nb_utilisateurs", 500)),
                step=10,
            )
            complexite = st.number_input(
                "Complexité technique (1–5)",
                min_value=VALIDATION_RANGES["complexite"]["min"],
                max_value=VALIDATION_RANGES["complexite"]["max"],
                value=int(vals.get("complexite", 3)),
                step=1,
            )
            budget_initial = st.number_input(
                "Budget initial (MAD)",
                min_value=VALIDATION_RANGES["budget_initial"]["min"],
                max_value=VALIDATION_RANGES["budget_initial"]["max"],
                value=int(vals.get("budget_initial", 500_000)),
                step=10_000,
            )

        st.divider()

        # Variables binaires
        col_cb1, col_cb2 = st.columns(2)
        with col_cb1:
            integration_externe = st.checkbox(
                "Intégration externe",
                value=bool(vals.get("integration_externe", 0)),
            )
        with col_cb2:
            migration_donnees = st.checkbox(
                "Migration de données",
                value=bool(vals.get("migration_donnees", 0)),
            )

        soumission = st.form_submit_button(
            "⚡ Prédire la durée et le coût",
            use_container_width=True,
            disabled=(not modeles_disponibles),
        )

    # Traitement de la soumission du formulaire
    if soumission and modeles_disponibles:
        features_saisies = {
            "type_projet": type_projet,
            "secteur": secteur,
            "methodologie": methodologie,
            "nb_modules": nb_modules,
            "nb_utilisateurs": nb_utilisateurs,
            "taille_equipe": taille_equipe,
            "complexite": complexite,
            "nb_livrables": nb_livrables,
            "integration_externe": int(integration_externe),
            "migration_donnees": int(migration_donnees),
            "experience_chef": experience_chef,
            "budget_initial": budget_initial,
        }
        with st.spinner("Calcul des prédictions…"):
            st.session_state.prediction_result = predict(
                features_saisies, modele_duree, modele_cout, encodeurs
            )

# ---- COLONNE DROITE — Résultats ------------------------------------------

with col_droite:
    st.subheader("📈 Résultats de la prédiction")

    if st.session_state.prediction_result is None:
        st.info(
            "Remplissez le formulaire et cliquez sur "
            "**⚡ Prédire la durée et le coût** pour obtenir les estimations."
        )
    else:
        res = st.session_state.prediction_result

        # Métriques principales
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric(
                label="⏱️ Durée estimée",
                value=f"{res['duree_jours']} jours ouvrables",
            )
        with col_m2:
            cout_formate = f"{res['cout_mad']:,} MAD".replace(",", " ")
            st.metric(
                label="💰 Coût estimé",
                value=cout_formate,
            )

        st.divider()

        # Graphique importance des features — Durée
        def creer_graphique_importances(
            importances: list[dict], titre: str
        ) -> go.Figure:
            """Crée un graphique à barres horizontal des feature importances."""
            # On prend les 8 premières (déjà triées par importance décroissante)
            top8 = importances[:8]
            # Inverser pour que la plus importante soit en haut
            noms = [d["feature"] for d in reversed(top8)]
            valeurs = [d["importance"] for d in reversed(top8)]

            fig = go.Figure(
                go.Bar(
                    x=valeurs,
                    y=noms,
                    orientation="h",
                    marker_color="steelblue",
                    text=[f"{v:.3f}" for v in valeurs],
                    textposition="outside",
                )
            )
            fig.update_layout(
                title=titre,
                xaxis_title="Importance",
                yaxis_title="Feature",
                height=320,
                margin={"l": 10, "r": 60, "t": 40, "b": 10},
                plot_bgcolor="rgba(0,0,0,0)",
            )
            return fig

        st.plotly_chart(
            creer_graphique_importances(
                res["feature_importances_duree"],
                "Top 8 features — Prédiction de la durée",
            ),
            use_container_width=True,
        )

        st.plotly_chart(
            creer_graphique_importances(
                res["feature_importances_cout"],
                "Top 8 features — Prédiction du coût",
            ),
            use_container_width=True,
        )

        # Détail des features
        with st.expander("📋 Détail des features utilisées"):
            features_affichage = {
                "type_projet": type_projet if soumission else vals.get("type_projet"),
                "secteur": secteur if soumission else vals.get("secteur"),
                "methodologie": methodologie if soumission else vals.get("methodologie"),
                "nb_modules": nb_modules if soumission else vals.get("nb_modules"),
                "nb_utilisateurs": nb_utilisateurs if soumission else vals.get("nb_utilisateurs"),
                "taille_equipe": taille_equipe if soumission else vals.get("taille_equipe"),
                "complexite": complexite if soumission else vals.get("complexite"),
                "nb_livrables": nb_livrables if soumission else vals.get("nb_livrables"),
                "integration_externe": int(integration_externe) if soumission else vals.get("integration_externe"),
                "migration_donnees": int(migration_donnees) if soumission else vals.get("migration_donnees"),
                "experience_chef": experience_chef if soumission else vals.get("experience_chef"),
                "budget_initial": budget_initial if soumission else vals.get("budget_initial"),
            }
            st.json(features_affichage)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.divider()
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.85em;'>"
    "ETTAOUSSI Nouhaila &nbsp;|&nbsp; "
    "OUYHIA Ayoub &nbsp;|&nbsp; LAIOUEJ Anass<br>"
    "Encadrant : Pr. ESSABBAR Driss &nbsp;—&nbsp; EMSI 2025-2026"
    "</div>",
    unsafe_allow_html=True,
)
