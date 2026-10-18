"""
schemas.py — Schémas de validation Pydantic pour ProPrism.

Définit le modèle ProjectFeatures qui valide les 12 features extraites
depuis le cahier des charges PDF avant de les passer aux modèles.
"""

from typing import Literal

from pydantic import BaseModel, Field


class ProjectFeatures(BaseModel):
    """Représente les 12 caractéristiques d'un projet informatique.

    Les champs catégoriels sont contraints par Literal pour n'accepter
    que les valeurs connues des LabelEncoders de la Phase 1.
    Les champs numériques utilisent Field(ge=..., le=...) pour valider
    les plages correspondant aux données d'entraînement.
    """

    # --- Variables catégorielles ---

    type_projet: Literal["Data/BI", "DevOps/Infra", "ERP", "Mobile", "Web"] = Field(
        default="Web",
        description="Type de projet informatique",
    )

    secteur: Literal[
        "Commerce",
        "Education",
        "Finance",
        "Immobilier",
        "Industrie",
        "Public",
        "Sante",
        "Tech",
    ] = Field(
        default="Tech",
        description="Secteur d'activité du client",
    )

    methodologie: Literal["Agile", "Hybride", "Waterfall"] = Field(
        default="Agile",
        description="Méthodologie de gestion de projet",
    )

    # --- Variables numériques entières ---

    nb_modules: int = Field(
        default=8,
        ge=3,
        le=22,
        description="Nombre de modules fonctionnels (3–22)",
    )

    nb_utilisateurs: int = Field(
        default=500,
        ge=20,
        le=6000,
        description="Nombre d'utilisateurs finaux (20–6 000)",
    )

    taille_equipe: int = Field(
        default=6,
        ge=2,
        le=15,
        description="Taille de l'équipe projet (2–15)",
    )

    complexite: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Niveau de complexité technique (1–5)",
    )

    nb_livrables: int = Field(
        default=12,
        ge=4,
        le=30,
        description="Nombre de livrables attendus (4–30)",
    )

    # --- Variables binaires ---

    integration_externe: int = Field(
        default=0,
        ge=0,
        le=1,
        description="Présence d'une intégration externe (0 ou 1)",
    )

    migration_donnees: int = Field(
        default=0,
        ge=0,
        le=1,
        description="Présence d'une migration de données (0 ou 1)",
    )

    # --- Variables numériques continues ---

    experience_chef: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Années d'expérience du chef de projet (1–20)",
    )

    budget_initial: int = Field(
        default=500_000,
        ge=50_000,
        le=2_000_000,
        description="Budget initial en MAD (50 000–2 000 000)",
    )
