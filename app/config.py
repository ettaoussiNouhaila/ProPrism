"""
config.py — Constantes globales de ProPrism.

Ce module centralise tous les chemins, listes de valeurs et plages de validation
utilisés dans l'ensemble de l'application.  Il doit rester importable sans
dépendances externes (pas d'imports de scikit-learn, streamlit, etc.).
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Chemins
# ---------------------------------------------------------------------------

# Dossier racine de l'application (app/)
APP_DIR = Path(__file__).resolve().parent

# Dossier contenant les fichiers .pkl
MODELS_DIR = APP_DIR / "models"

# Chemins exacts des trois fichiers de modèles
MODEL_DUREE_PATH = MODELS_DIR / "model_duree.pkl"
MODEL_COUT_PATH = MODELS_DIR / "model_cout.pkl"
ENCODERS_PATH = MODELS_DIR / "encoders.pkl"

# ---------------------------------------------------------------------------
# Ordre des features (ne jamais modifier — doit correspondre à l'entraînement)
# ---------------------------------------------------------------------------

FEATURE_ORDER: list[str] = [
    "type_projet",
    "secteur",
    "methodologie",
    "nb_modules",
    "nb_utilisateurs",
    "taille_equipe",
    "complexite",
    "nb_livrables",
    "integration_externe",
    "migration_donnees",
    "experience_chef",
    "budget_initial",
]

# ---------------------------------------------------------------------------
# Valeurs acceptées pour les variables catégorielles
# ---------------------------------------------------------------------------

TYPES_PROJETS: list[str] = ["Data/BI", "DevOps/Infra", "ERP", "Mobile", "Web"]

SECTEURS: list[str] = [
    "Commerce",
    "Education",
    "Finance",
    "Immobilier",
    "Industrie",
    "Public",
    "Sante",
    "Tech",
]

METHODOLOGIES: list[str] = ["Agile", "Hybride", "Waterfall"]

# ---------------------------------------------------------------------------
# Plages de validation pour les variables numériques
# Format : { nom_feature: {"min": valeur_min, "max": valeur_max} }
# ---------------------------------------------------------------------------

VALIDATION_RANGES: dict[str, dict[str, int]] = {
    "nb_modules": {"min": 3, "max": 22},
    "nb_utilisateurs": {"min": 20, "max": 6000},
    "taille_equipe": {"min": 2, "max": 15},
    "complexite": {"min": 1, "max": 5},
    "nb_livrables": {"min": 4, "max": 30},
    "experience_chef": {"min": 1, "max": 20},
    "budget_initial": {"min": 50_000, "max": 2_000_000},
    "integration_externe": {"min": 0, "max": 1},
    "migration_donnees": {"min": 0, "max": 1},
}

# ---------------------------------------------------------------------------
# Valeurs par défaut (utilisées si l'extraction LLM est incomplète)
# ---------------------------------------------------------------------------

DEFAULT_FEATURES: dict[str, object] = {
    "type_projet": "Web",
    "secteur": "Tech",
    "methodologie": "Agile",
    "nb_modules": 8,
    "nb_utilisateurs": 500,
    "taille_equipe": 6,
    "complexite": 3,
    "nb_livrables": 12,
    "integration_externe": 0,
    "migration_donnees": 0,
    "experience_chef": 5,
    "budget_initial": 500_000,
}
