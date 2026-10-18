"""
llm_extractor.py — Extraction des features d'un projet depuis un PDF via Gemini.

Expose trois fonctions publiques :
- extract_text_from_pdf()    : convertit les bytes PDF en texte brut
- build_extraction_prompt()  : construit le prompt système pour Gemini
- extract_features()         : appelle l'API Google Gemini et valide le résultat
"""

import json
import logging
import re

import fitz  # PyMuPDF
from pydantic import ValidationError

from config import DEFAULT_FEATURES, METHODOLOGIES, SECTEURS, TYPES_PROJETS
from modules.schemas import ProjectFeatures

logger = logging.getLogger(__name__)

# Modèle Gemini utilisé pour l'extraction (rapide, gratuit, suffisant)
_GEMINI_MODEL = "gemini-2.5-flash"


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extrait le contenu textuel d'un fichier PDF.

    Parameters
    ----------
    pdf_bytes : bytes
        Contenu binaire du fichier PDF.

    Returns
    -------
    str
        Texte brut extrait de toutes les pages, séparées par des sauts de ligne.

    Raises
    ------
    ValueError
        Si le PDF est vide ou illisible.
    """
    document = fitz.open(stream=pdf_bytes, filetype="pdf")

    pages_texte = []
    for numero_page in range(len(document)):
        page = document[numero_page]
        pages_texte.append(page.get_text())

    document.close()

    texte_complet = "\n".join(pages_texte).strip()

    if not texte_complet:
        raise ValueError("Le PDF ne contient pas de texte extractible.")

    return texte_complet


def build_extraction_prompt(pdf_text: str) -> str:
    """Construit le prompt envoyé à Gemini pour extraire les features du projet.

    Le prompt exige un JSON strict contenant exactement les 12 clés définies,
    avec les contraintes de valeurs acceptées pour chaque champ.

    Parameters
    ----------
    pdf_text : str
        Texte brut extrait du cahier des charges PDF.

    Returns
    -------
    str
        Prompt complet prêt à être envoyé à l'API Google Gemini.
    """
    types_str = ", ".join(f'"{v}"' for v in TYPES_PROJETS)
    secteurs_str = ", ".join(f'"{v}"' for v in SECTEURS)
    methodes_str = ", ".join(f'"{v}"' for v in METHODOLOGIES)

    prompt = f"""Tu es un expert en gestion de projets informatiques.
Analyse le cahier des charges ci-dessous et extrais les 12 caractéristiques du projet.

INSTRUCTIONS STRICTES :
1. Réponds UNIQUEMENT avec un objet JSON valide, sans texte avant ni après.
2. Utilise exactement ces 12 clés, dans n'importe quel ordre.
3. Respecte scrupuleusement les valeurs et plages indiquées.

CHAMPS REQUIS :
{{
  "type_projet": <une valeur parmi {types_str}>,
  "secteur": <une valeur parmi {secteurs_str}>,
  "methodologie": <une valeur parmi {methodes_str}>,
  "nb_modules": <entier entre 3 et 22>,
  "nb_utilisateurs": <entier entre 20 et 6000>,
  "taille_equipe": <entier entre 2 et 15>,
  "complexite": <entier entre 1 et 5>,
  "nb_livrables": <entier entre 4 et 30>,
  "integration_externe": <0 ou 1>,
  "migration_donnees": <0 ou 1>,
  "experience_chef": <entier entre 1 et 20>,
  "budget_initial": <entier entre 50000 et 2000000, en MAD>
}}

Si une information est absente ou ambiguë dans le document, estime une valeur
plausible en te basant sur le contexte général du projet.

CAHIER DES CHARGES :
---
{pdf_text[:8000]}
---

Réponds uniquement avec le JSON :"""

    return prompt


def extract_features(pdf_text: str, api_key: str) -> dict:
    """Appelle l'API Google Gemini pour extraire et valider les features du projet.

    Utilise le mode JSON structuré de Gemini (response_schema) pour obtenir
    directement un objet Pydantic validé sans parsing manuel.

    Parameters
    ----------
    pdf_text : str
        Texte brut extrait du cahier des charges PDF.
    api_key : str
        Clé API Google Gemini valide (obtenir sur aistudio.google.com).

    Returns
    -------
    dict
        Dictionnaire des 12 features validées.  En cas d'erreur, retourne
        un dict avec une clé 'error' (str) décrivant le problème, plus les
        valeurs par défaut pour permettre une utilisation dégradée.
    """
    # Import local pour ne pas charger google-genai si le module n'est pas utilisé
    from google import genai  # noqa: PLC0415

    prompt = build_extraction_prompt(pdf_text)

    # --- Appel API Gemini ---
    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=_GEMINI_MODEL,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": ProjectFeatures,
            },
        )

    except Exception as exc:
        message_erreur = f"Erreur API Gemini : {exc}"
        logger.error(message_erreur)
        return {"error": message_erreur, **DEFAULT_FEATURES}

    # --- Parsing de la réponse ---
    try:
        # Chemin privilégié : response.parsed retourne directement l'objet Pydantic
        if response.parsed is not None:
            logger.info("Réponse Gemini parsée directement via response.parsed.")
            return response.parsed.model_dump()

        # Fallback : parser response.text manuellement
        contenu_brut = response.text.strip()
        logger.info("Réponse brute de Gemini : %s", contenu_brut[:200])

        correspondance = re.search(r"\{.*\}", contenu_brut, re.DOTALL)
        if not correspondance:
            raise ValueError("Aucun objet JSON trouvé dans la réponse de Gemini.")

        donnees_json = json.loads(correspondance.group())

    except (json.JSONDecodeError, ValueError) as exc:
        message_erreur = f"Erreur de parsing JSON : {exc}"
        logger.error(message_erreur)
        return {"error": message_erreur, **DEFAULT_FEATURES}

    # --- Application des valeurs par défaut pour les champs manquants ---
    features_completes = dict(DEFAULT_FEATURES)
    features_completes.update(donnees_json)

    # --- Validation via Pydantic ---
    try:
        modele_valide = ProjectFeatures(**features_completes)
        return modele_valide.model_dump()
    except ValidationError as exc:
        # En cas d'erreur de validation, on corrige avec les défauts
        logger.warning(
            "Validation Pydantic échouée, application des défauts. Erreurs : %s", exc
        )
        # On applique champ par champ en ignorant les valeurs invalides
        features_corrigees = dict(DEFAULT_FEATURES)
        for nom_champ, valeur in donnees_json.items():
            if nom_champ in DEFAULT_FEATURES:
                features_corrigees[nom_champ] = valeur
        try:
            modele_corrige = ProjectFeatures(**features_corrigees)
            return modele_corrige.model_dump()
        except ValidationError:
            # Dernier recours : retourner les valeurs par défaut
            return dict(DEFAULT_FEATURES)
