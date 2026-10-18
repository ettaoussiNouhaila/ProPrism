"""
test_predictor.py — Tests unitaires pour le module predictor.

Les tests qui dépendent des fichiers .pkl sont skippés automatiquement
si ces fichiers ne sont pas présents (pour ne pas bloquer la CI).
"""

import pytest

from app.config import ENCODERS_PATH, MODEL_COUT_PATH, MODEL_DUREE_PATH

# Condition de skip : au moins un des .pkl est absent
_PKL_MANQUANTS = not (
    MODEL_DUREE_PATH.exists() and MODEL_COUT_PATH.exists() and ENCODERS_PATH.exists()
)
_RAISON_SKIP = "Fichiers .pkl absents du dossier app/models/"

# ---------------------------------------------------------------------------
# Données de test
# ---------------------------------------------------------------------------

_PROJET_ERP_COMPLEXE = {
    "type_projet": "ERP",
    "secteur": "Finance",
    "methodologie": "Waterfall",
    "nb_modules": 20,
    "nb_utilisateurs": 5000,
    "taille_equipe": 14,
    "complexite": 5,
    "nb_livrables": 28,
    "integration_externe": 1,
    "migration_donnees": 1,
    "experience_chef": 15,
    "budget_initial": 1_800_000,
}

_PROJET_MOBILE_SIMPLE = {
    "type_projet": "Mobile",
    "secteur": "Commerce",
    "methodologie": "Agile",
    "nb_modules": 4,
    "nb_utilisateurs": 200,
    "taille_equipe": 3,
    "complexite": 2,
    "nb_livrables": 6,
    "integration_externe": 0,
    "migration_donnees": 0,
    "experience_chef": 3,
    "budget_initial": 100_000,
}

_PROJET_ERP_MOYEN = {
    "type_projet": "ERP",
    "secteur": "Industrie",
    "methodologie": "Hybride",
    "nb_modules": 12,
    "nb_utilisateurs": 1000,
    "taille_equipe": 8,
    "complexite": 3,
    "nb_livrables": 15,
    "integration_externe": 1,
    "migration_donnees": 0,
    "experience_chef": 7,
    "budget_initial": 700_000,
}

_PROJET_MOBILE_MOYEN = {
    "type_projet": "Mobile",
    "secteur": "Tech",
    "methodologie": "Agile",
    "nb_modules": 12,
    "nb_utilisateurs": 1000,
    "taille_equipe": 8,
    "complexite": 3,
    "nb_livrables": 15,
    "integration_externe": 1,
    "migration_donnees": 0,
    "experience_chef": 7,
    "budget_initial": 700_000,
}

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(_PKL_MANQUANTS, reason=_RAISON_SKIP)
def test_load_models():
    """Vérifie que les trois objets sont correctement chargés depuis les .pkl."""
    from app.modules.predictor import load_models

    modele_duree, modele_cout, encodeurs = load_models()

    # Vérification que les objets ne sont pas None
    assert modele_duree is not None, "Le modèle de durée ne doit pas être None."
    assert modele_cout is not None, "Le modèle de coût ne doit pas être None."
    assert encodeurs is not None, "Les encodeurs ne doivent pas être None."

    # Vérification que les encodeurs contiennent les 3 clés attendues
    assert "type_projet" in encodeurs, "L'encodeur type_projet est manquant."
    assert "secteur" in encodeurs, "L'encodeur secteur est manquant."
    assert "methodologie" in encodeurs, "L'encodeur methodologie est manquant."


@pytest.mark.skipif(_PKL_MANQUANTS, reason=_RAISON_SKIP)
def test_predict_erp_project():
    """Un projet ERP complexe doit retourner une durée supérieure à 250 jours."""
    from app.modules.predictor import load_models, predict

    modele_duree, modele_cout, encodeurs = load_models()
    resultat = predict(_PROJET_ERP_COMPLEXE, modele_duree, modele_cout, encodeurs)

    assert "duree_jours" in resultat, "La clé 'duree_jours' doit être présente."
    assert "cout_mad" in resultat, "La clé 'cout_mad' doit être présente."
    assert (
        resultat["duree_jours"] > 250
    ), f"Durée ERP complexe attendue > 250j, obtenu : {resultat['duree_jours']}j"


@pytest.mark.skipif(_PKL_MANQUANTS, reason=_RAISON_SKIP)
def test_predict_mobile_project():
    """Un projet Mobile simple doit retourner une durée inférieure à 180 jours."""
    from app.modules.predictor import load_models, predict

    modele_duree, modele_cout, encodeurs = load_models()
    resultat = predict(_PROJET_MOBILE_SIMPLE, modele_duree, modele_cout, encodeurs)

    assert (
        resultat["duree_jours"] < 180
    ), f"Durée Mobile simple attendue < 180j, obtenu : {resultat['duree_jours']}j"


@pytest.mark.skipif(_PKL_MANQUANTS, reason=_RAISON_SKIP)
def test_coherence_erp_vs_mobile():
    """À complexité égale, ERP doit être plus long ET plus cher que Mobile."""
    from app.modules.predictor import load_models, predict

    modele_duree, modele_cout, encodeurs = load_models()

    res_erp = predict(_PROJET_ERP_MOYEN, modele_duree, modele_cout, encodeurs)
    res_mobile = predict(_PROJET_MOBILE_MOYEN, modele_duree, modele_cout, encodeurs)

    assert res_erp["duree_jours"] > res_mobile["duree_jours"], (
        f"ERP ({res_erp['duree_jours']}j) devrait durer plus longtemps "
        f"que Mobile ({res_mobile['duree_jours']}j)."
    )
    assert res_erp["cout_mad"] > res_mobile["cout_mad"], (
        f"ERP ({res_erp['cout_mad']} MAD) devrait coûter plus cher "
        f"que Mobile ({res_mobile['cout_mad']} MAD)."
    )
