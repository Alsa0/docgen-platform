# Service de recherche web pour équipements et datasheets
# Utilise l'API Claude avec web_search tool natif

import json
import logging
from anthropic import AsyncAnthropic
from config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL

logger = logging.getLogger(__name__)
client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)


async def search_equipment(
    query: str,
    project_type: str = "",
    budget_range: str = "",
    currency: str = "MGA"
) -> list[dict]:
    """
    Recherche des équipements sur internet via Claude web_search.
    Retourne une liste structurée d'équipements avec prix et fournisseurs.
    """
    try:
        prompt = f"""Recherche sur internet des équipements IT/Télécom correspondant à cette demande.

**Recherche** : {query}
**Type de projet** : {project_type}
**Budget** : {budget_range} {currency}

Trouve les équipements réels avec leurs prix actuels, marques, modèles et fournisseurs.
Privilégie les sources fiables (sites constructeurs, distributeurs officiels).

Retourne UNIQUEMENT un JSON valide :
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

        response = await client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{"role": "user", "content": prompt}],
        )

        result_text = ""
        for block in response.content:
            if block.type == "text":
                result_text += block.text

        results = _parse_json(result_text)
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
    Retourne les spécifications techniques détaillées.
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

        response = await client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{"role": "user", "content": prompt}],
        )

        result_text = ""
        for block in response.content:
            if block.type == "text":
                result_text += block.text

        result = _parse_json(result_text)
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

Pour chaque équipement, trouve le prix actuel chez différents fournisseurs.

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

        response = await client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{"role": "user", "content": prompt}],
        )

        result_text = ""
        for block in response.content:
            if block.type == "text":
                result_text += block.text

        results = _parse_json(result_text)
        return results if isinstance(results, list) else []

    except Exception as e:
        logger.error(f"Erreur recherche prix : {e}")
        raise


def _parse_json(text: str):
    """Parse un JSON depuis une réponse textuelle."""
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
