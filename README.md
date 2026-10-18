# ProPrism — Estimation Prédictive de Projets Informatiques

## Description

ProPrism est un outil d'aide à la décision qui prédit automatiquement la **durée**
(en jours ouvrables) et le **coût** (en MAD) d'un projet informatique à partir d'un
cahier des charges au format PDF.

Il combine :
- L'**API Google Gemini** (`gemini-2.5-flash`) pour extraire les caractéristiques du projet depuis le PDF
- Deux **modèles Random Forest** pré-entraînés (R²=0.80 durée, R²=0.93 coût)
- Une interface **Streamlit** interactive en français

---

## Prérequis

- Python **3.10** ou supérieur
- Une **clé API Google Gemini** — gratuite sur https://aistudio.google.com/ (le tier gratuit est suffisant)
- Les trois fichiers de modèles `.pkl` (fournis séparément par l'équipe)

---

## Installation

```bash
# 1. Cloner ou télécharger le projet
cd proprism-app

# 2. Créer et activer un environnement virtuel
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer la clé API
cp .env.example .env
# Éditer .env et renseigner votre GEMINI_API_KEY (obtenir sur aistudio.google.com)
```

---

## Utilisation

### Étape 1 — Déposer les modèles

Placer les trois fichiers suivants dans le dossier `app/models/` :

```
app/models/model_duree.pkl
app/models/model_cout.pkl
app/models/encoders.pkl
```

### Étape 2 — Lancer l'application

L'application doit être lancée **depuis le dossier `app/`** pour que les imports fonctionnent correctement :

```bash
cd app
streamlit run streamlit_app.py
```

Ou en une seule commande depuis la racine du projet :

```bash
cd app && streamlit run streamlit_app.py
```

### Étape 3 — Utiliser l'interface

1. Uploader un cahier des charges PDF dans la sidebar
2. Cliquer sur "🔍 Extraire les features du PDF" pour laisser Gemini analyser le document
3. Vérifier/ajuster les 12 features dans le formulaire
4. Cliquer sur "⚡ Prédire la durée et le coût"
5. Consulter les résultats et les graphiques d'importance des features

---

## Structure du projet

```
proprism-app/
├── CLAUDE.md                 # Documentation pour Claude Code
├── README.md                 # Ce fichier
├── requirements.txt          # Dépendances Python
├── .env.example              # Modèle de configuration
├── .gitignore
├── app/
│   ├── __init__.py
│   ├── streamlit_app.py      # Point d'entrée principal
│   ├── config.py             # Constantes globales
│   ├── models/               # Dossier des modèles .pkl (non versionnés)
│   │   └── .gitkeep
│   └── modules/
│       ├── __init__.py
│       ├── schemas.py        # Validation Pydantic
│       ├── predictor.py      # Chargement et prédiction
│       └── llm_extractor.py  # Extraction PDF + LLM
├── tests/
│   ├── __init__.py
│   ├── test_predictor.py
│   └── test_llm_extractor.py
└── outputs/
    └── .gitkeep
```

---

## Équipe

| Nom | Rôle |
|-----|------|
| ETTAOUSSI Nouhaila | Développement |
| OUYHIA Ayoub | Développement |
| LAIOUEJ Anass | Développement |

**Encadrant :** Pr. ESSABBAR Driss

*Projet académique — EMSI, 2025-2026*
