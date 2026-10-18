"""
predictor.py — Chargement des modèles et prédiction pour ProPrism.

Expose deux fonctions publiques :
- load_models()  : charge les trois fichiers .pkl depuis app/models/
- predict()      : encode les features et retourne durée, coût et importances
"""

import logging
from typing import Any

import joblib
import pandas as pd

from config import (
    ENCODERS_PATH,
    FEATURE_ORDER,
    MODEL_COUT_PATH,
    MODEL_DUREE_PATH,
)

logger = logging.getLogger(__name__)


def load_models() -> tuple[Any, Any, dict]:
    """Charge les modèles Random Forest et les encodeurs depuis le disque.

    Returns
    -------
    tuple[Any, Any, dict]
        (model_duree, model_cout, encoders)
        - model_duree : RandomForestRegressor pour la durée en jours
        - model_cout  : RandomForestRegressor pour le coût en MAD
        - encoders    : dict { nom_feature: LabelEncoder } pour les 3 catégorielles

    Raises
    ------
    FileNotFoundError
        Si l'un des fichiers .pkl est absent du dossier app/models/.
    """
    logger.info("Chargement des modèles depuis %s", MODEL_DUREE_PATH.parent)

    if not MODEL_DUREE_PATH.exists():
        raise FileNotFoundError(f"Modèle durée introuvable : {MODEL_DUREE_PATH}")
    if not MODEL_COUT_PATH.exists():
        raise FileNotFoundError(f"Modèle coût introuvable : {MODEL_COUT_PATH}")
    if not ENCODERS_PATH.exists():
        raise FileNotFoundError(f"Encodeurs introuvables : {ENCODERS_PATH}")

    model_duree = joblib.load(MODEL_DUREE_PATH)
    model_cout = joblib.load(MODEL_COUT_PATH)
    encoders = joblib.load(ENCODERS_PATH)

    logger.info("Modèles chargés avec succès.")
    return model_duree, model_cout, encoders


def predict(
    features: dict,
    model_duree: Any,
    model_cout: Any,
    encoders: dict,
) -> dict:
    """Prédit la durée et le coût d'un projet à partir de ses features.

    Parameters
    ----------
    features : dict
        Dictionnaire contenant les 12 features du projet.  Il n'est pas muté.
    model_duree : RandomForestRegressor
        Modèle entraîné pour prédire la durée en jours ouvrables.
    model_cout : RandomForestRegressor
        Modèle entraîné pour prédire le coût en MAD.
    encoders : dict
        Dictionnaire { 'type_projet': LabelEncoder, 'secteur': ..., 'methodologie': ... }

    Returns
    -------
    dict avec les clés :
        - duree_jours                (int)  : durée prédite arrondie à l'entier
        - cout_mad                   (int)  : coût prédit arrondi à l'entier
        - feature_importances_duree  (list) : liste triée [{'feature', 'importance'}]
        - feature_importances_cout   (list) : liste triée [{'feature', 'importance'}]
    """
    # Copie pour ne pas muter le dict original
    data = dict(features)

    # --- Encodage des variables catégorielles ---
    variables_categorielles = ["type_projet", "secteur", "methodologie"]
    for colonne in variables_categorielles:
        encodeur = encoders[colonne]
        data[colonne] = encodeur.transform([data[colonne]])[0]

    # --- Construction du DataFrame dans l'ordre exact d'entraînement ---
    df = pd.DataFrame([data], columns=FEATURE_ORDER)

    # --- Prédiction ---
    duree_pred = model_duree.predict(df)[0]
    cout_pred = model_cout.predict(df)[0]

    # --- Feature importances triées par importance décroissante ---
    def _trier_importances(modele: Any) -> list[dict]:
        """Retourne les importances de features sous forme de liste triée."""
        paires = zip(FEATURE_ORDER, modele.feature_importances_)
        triees = sorted(paires, key=lambda x: x[1], reverse=True)
        return [{"feature": nom, "importance": float(imp)} for nom, imp in triees]

    return {
        "duree_jours": int(round(duree_pred)),
        "cout_mad": int(round(cout_pred)),
        "feature_importances_duree": _trier_importances(model_duree),
        "feature_importances_cout": _trier_importances(model_cout),
    }
