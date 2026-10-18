"""
test_llm_extractor.py — Tests unitaires pour le module llm_extractor.

Ces tests ne font pas d'appel réseau : ils vérifient la construction
du prompt et la cohérence des valeurs par défaut.
"""

import pytest

from app.config import DEFAULT_FEATURES, FEATURE_ORDER, VALIDATION_RANGES
from app.modules.llm_extractor import build_extraction_prompt


def test_build_prompt_contient_les_12_features():
    """Vérifie que le prompt contient bien les 12 noms de features."""
    texte_exemple = "Projet de développement d'une application web de gestion RH."
    prompt = build_extraction_prompt(texte_exemple)

    for nom_feature in FEATURE_ORDER:
        assert nom_feature in prompt, (
            f"Le nom de feature '{nom_feature}' est absent du prompt d'extraction."
        )


def test_build_prompt_contient_les_valeurs_categorielles():
    """Vérifie que le prompt mentionne les valeurs acceptées pour les catégorielles."""
    texte_exemple = "Système ERP pour une entreprise industrielle."
    prompt = build_extraction_prompt(texte_exemple)

    # Quelques valeurs représentatives
    for valeur in ["ERP", "Mobile", "Web", "Agile", "Waterfall", "Finance", "Tech"]:
        assert valeur in prompt, (
            f"La valeur catégorielle '{valeur}' devrait figurer dans le prompt."
        )


def test_default_values_respectent_les_plages_de_validation():
    """Vérifie que chaque valeur par défaut numérique respecte sa plage de validation."""
    for nom_feature, plage in VALIDATION_RANGES.items():
        valeur = DEFAULT_FEATURES.get(nom_feature)
        assert valeur is not None, (
            f"La valeur par défaut de '{nom_feature}' est manquante."
        )
        assert plage["min"] <= valeur <= plage["max"], (
            f"La valeur par défaut de '{nom_feature}' ({valeur}) est hors plage "
            f"[{plage['min']}, {plage['max']}]."
        )


def test_default_values_contiennent_toutes_les_features():
    """Vérifie que les valeurs par défaut couvrent les 12 features."""
    for nom_feature in FEATURE_ORDER:
        assert nom_feature in DEFAULT_FEATURES, (
            f"La feature '{nom_feature}' est absente des valeurs par défaut."
        )
