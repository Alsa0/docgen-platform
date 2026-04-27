# Service de recherche web pour équipements et datasheets
# Utilise l'API Gemini avec Google Search Grounding

import json
import logging
import google.generativeai as genai
from config.settings import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)
genai.configure(api_key=GEMINI_API_KEY)


async def search_equipment(
    query: str,
    project_type: str = "",
    budget_range: str = "",
    currency: str = "MGA"
) -> list[dict]:
    """
    Recherche des équipements sur internet via Gemini Google Search.
    Retourne une liste structurée d'équipements avec prix et fournisseurs.
    """
    try:
        prompt = f"""Recherche sur internet des équipements IT/Télécom correspondant à cette demande.

**Recherche** : {query}
**Type de projet** : {project_type}
**Budget** : {budget_range} {currency}

Trouve les équipements réels avec leurs prix actuels, marques, modèles et fournisseurs.

Retourne UNIQUEMENT un JSON valide contenant une liste d'objets :
[
  {{
    "nom": "Nom de l'équipement",
    "marque": "Marque",
    "modele": "Modèle",
    "prix_estime": 0,
    "devise": "{currency}",
    "fournisseur": "Nom du fournisseur/distributeur",
    "url": "URL source",
    "description": "Description courte",
    "confiance_prix": "vérifié"
  }}
]

Retourne 5 à 10 résultats pertinents."""

        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            tools='google_search_retrieval'
        )
        response = await model.generate_content_async(prompt)
        results = _parse_json(response.text)
        return results if isinstance(results, list) else []

    except Exception as e:
        logger.error(f"Erreur recherche équipements : {e}")
        raise


async def search_datasheet(
    equipment_name: str,
    brand: str = "",
    model: str = ""
) -> dict:
    """
    Recherche la fiche technique (datasheet) d'un équipement.
    """
    try:
        prompt = f"""Recherche la datasheet et les spécifications techniques de cet équipement :

**Équipement** : {equipment_name}
**Marque** : {brand}
**Modèle** : {model}

Trouve les spécifications techniques officielles du constructeur.

Retourne UNIQUEMENT un JSON valide :
{{
  "nom": "{equipment_name}",
  "marque": "{brand}",
  "modele": "{model}",
  "specifications": {{
    "description": "Description complète",
    "ports": "Détail des ports/interfaces",
    "performance": "Performances (débit, capacité...)",
    "dimensions": "Dimensions physiques",
    "alimentation": "Alimentation requise",
    "certifications": "Certifications",
    "fonctionnalites_cles": ["Fonctionnalité 1", "Fonctionnalité 2"]
  }},
  "datasheet_url": "URL de la datasheet PDF si trouvée",
  "source": "Site source de l'information"
}}"""

        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            tools='google_search_retrieval'
        )
        response = await model.generate_content_async(prompt)
        result = _parse_json(response.text)
        return result if isinstance(result, dict) else {"nom": equipment_name, "error": "Données non trouvées"}

    except Exception as e:
        logger.error(f"Erreur recherche datasheet : {e}")
        raise


async def search_prices(equipment_list: list[dict]) -> list[dict]:
    """
    Enrichit une liste d'équipements avec les prix du marché actuel.
    """
    try:
        equipments_str = "\n".join([
            f"- {eq.get('nom', eq.get('designation', ''))} ({eq.get('marque', '')} {eq.get('modele', '')})"
            for eq in equipment_list
        ])

        prompt = f"""Recherche les prix actuels du marché pour ces équipements :

{equipments_str}

Retourne UNIQUEMENT un JSON valide (liste dans le même ordre) :
[
  {{
    "nom": "Nom de l'équipement",
    "marque": "Marque",
    "modele": "Modèle",
    "prix_min": 0,
    "prix_max": 0,
    "prix_moyen": 0,
    "devise": "USD",
    "sources": [
      {{"fournisseur": "Nom", "prix": 0, "url": "URL"}}
    ]
  }}
]"""

        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            tools='google_search_retrieval'
        )
        response = await model.generate_content_async(prompt)
        results = _parse_json(response.text)
        return results if isinstance(results, list) else []

    except Exception as e:
        logger.error(f"Erreur recherche prix : {e}")
        raise


def _parse_json(text: str):
    """Parse un JSON depuis une réponse textuelle."""
    if not text:
        return None
    import re
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass
    match = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', text)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass
    for sc, ec in [('[', ']'), ('{', '}')]:
        si = text.find(sc)
        if si == -1:
            continue
        depth = 0
        for i in range(si, len(text)):
            if text[i] == sc:
                depth += 1
            elif text[i] == ec:
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[si:i+1])
                    except json.JSONDecodeError:
                        break
    return None
