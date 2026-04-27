# Service d'intégration avec l'API Claude d'Anthropic
# Gère toutes les interactions IA pour la génération de contenu documentaire

import json
import logging
from anthropic import AsyncAnthropic
from config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL, COMPANY_NAME

logger = logging.getLogger(__name__)

# Client Anthropic global
client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)


async def generate_bom_content(
    project_description: str,
    budget: float,
    currency: str = "MGA",
    project_type: str = "infrastructure réseau",
    specific_equipment: str = ""
) -> list[dict]:
    """
    Génère une liste d'équipements BOM en utilisant Claude avec web_search.
    Recherche les équipements adaptés au projet sur internet.
    Retourne une liste JSON structurée.
    """
    try:
        prompt = f"""Tu es un expert en ingénierie IT et télécom à Madagascar. 
Génère un Bill of Materials (BOM) détaillé pour ce projet.

**Projet** : {project_description}
**Type** : {project_type}
**Budget** : {budget:,.0f} {currency}
{f"**Équipements souhaités** : {specific_equipment}" if specific_equipment else ""}

INSTRUCTIONS :
1. Utilise la recherche web pour trouver les équipements réels avec leurs prix actuels
2. Privilégie les fournisseurs accessibles depuis Madagascar
3. Reste dans le budget indiqué
4. Inclus tous les accessoires nécessaires (câbles, connecteurs, licences, etc.)

Retourne UNIQUEMENT un JSON valide (pas de markdown, pas de texte avant/après) avec cette structure :
[
  {{
    "reference": "REF-001",
    "designation": "Nom complet de l'équipement",
    "marque": "Marque",
    "modele": "Modèle exact",
    "quantite": 1,
    "prix_unitaire": 0,
    "devise": "{currency}",
    "fournisseur": "Nom du fournisseur",
    "url": "https://...",
    "description": "Description courte et technique"
  }}
]

Génère entre 5 et 15 lignes d'équipements selon le projet."""

        response = await client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=8192,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{"role": "user", "content": prompt}],
        )

        # Extraire le texte de la réponse (peut contenir plusieurs blocs)
        result_text = ""
        for block in response.content:
            if block.type == "text":
                result_text += block.text

        # Parser le JSON depuis la réponse
        bom_items = _extract_json_from_response(result_text)
        if isinstance(bom_items, list):
            # Calculer les prix totaux
            for i, item in enumerate(bom_items):
                item["reference"] = item.get("reference", f"REF-{i+1:03d}")
                item["prix_total"] = item.get("quantite", 1) * item.get("prix_unitaire", 0)
            return bom_items

        logger.warning("La réponse IA n'est pas une liste JSON valide pour le BOM")
        return []

    except Exception as e:
        logger.error(f"Erreur lors de la génération BOM via IA : {e}")
        raise


async def generate_sow_content(
    project_description: str,
    config: dict,
    bom_items: list[dict] | None = None
) -> dict:
    """
    Génère le contenu d'un Scope of Work structuré.
    Inclut : overview, objectifs, tâches détaillées, jalons, critères d'acceptation.
    """
    try:
        bom_section = ""
        if bom_items:
            bom_summary = "\n".join([
                f"- {item.get('designation', 'N/A')} ({item.get('marque', '')} {item.get('modele', '')}) x{item.get('quantite', 1)}"
                for item in bom_items
            ])
            bom_section = f"\n**Équipements prévus :**\n{bom_summary}"

        prompt = f"""Tu es un chef de projet IT senior. Génère un Scope of Work complet en français.

**Projet** : {config.get('projet_titre', 'Projet')}
**Description** : {project_description}
**Type** : {config.get('type_projet', 'infrastructure réseau')}
**Client** : {config.get('client_nom', 'Client')}
**Date début** : {config.get('date_debut', 'À définir')}
**Date fin** : {config.get('date_fin', 'À définir')}
**Budget service** : {config.get('budget_service', 0):,} {config.get('devise', 'MGA')}
**Livrables** : {', '.join(config.get('livrables', ['À définir']))}
**Critères d'acceptation** : {', '.join(config.get('criteres_acceptation', ['À définir']))}
{bom_section}

Retourne UNIQUEMENT un JSON valide avec cette structure :
{{
  "overview": "Résumé exécutif du projet...",
  "objectifs": ["Objectif 1", "Objectif 2", ...],
  "perimetre_inclus": ["Élément inclus 1", ...],
  "perimetre_exclus": ["Élément exclu 1", ...],
  "taches": [
    {{
      "numero": 1,
      "titre": "Titre de la tâche",
      "description": "Description détaillée",
      "responsable": "Rôle responsable",
      "duree_jours": 3,
      "dependances": [],
      "livrables": ["Livrable 1"],
      "criteres_acceptation": ["Critère 1"]
    }}
  ],
  "jalons": [
    {{
      "numero": 1,
      "titre": "Jalon",
      "date_prevue": "J+5",
      "livrables": ["Livrable associé"]
    }}
  ],
  "hypotheses": ["Hypothèse 1", ...],
  "conditions_paiement": "30% à la commande, 40% à mi-parcours, 30% à la livraison"
}}

Génère entre 5 et 10 tâches détaillées et réalistes."""

        response = await client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}],
        )

        result_text = ""
        for block in response.content:
            if block.type == "text":
                result_text += block.text

        sow_content = _extract_json_from_response(result_text)
        if isinstance(sow_content, dict):
            return sow_content

        logger.warning("La réponse IA n'est pas un JSON valide pour le SOW")
        return {"overview": result_text, "taches": [], "jalons": []}

    except Exception as e:
        logger.error(f"Erreur lors de la génération SOW via IA : {e}")
        raise


async def generate_ot_content(
    config: dict,
    sow_summary: dict | None = None,
    bom_summary: list[dict] | None = None
) -> dict:
    """
    Génère le contenu d'une Offre Technique complète.
    Sections : présentation entreprise, analyse besoin, solution, méthodologie, valeur ajoutée.
    """
    try:
        annexes = ""
        if sow_summary:
            annexes += f"\n**Résumé SOW disponible** : {json.dumps(sow_summary, ensure_ascii=False)[:1000]}"
        if bom_summary:
            total_bom = sum(item.get("prix_total", 0) for item in bom_summary)
            annexes += f"\n**Résumé BOM** : {len(bom_summary)} équipements, total : {total_bom:,.0f} {config.get('devise', 'MGA')}"

        prompt = f"""Tu es un directeur commercial d'une société IT ({COMPANY_NAME}) à Madagascar.
Génère une Offre Technique professionnelle et persuasive en français.

**Client** : {config.get('client_nom', 'Client')}
**Contact** : {config.get('client_contact', '')}
**Projet** : {config.get('projet_titre', 'Projet')}
**Description besoin** : {config.get('projet_description', '')}
**Type** : {config.get('type_projet', '')}
**Budget** : {config.get('budget_total', 0):,} {config.get('devise', 'MGA')}
**Délai** : {config.get('delai_jours', 30)} jours
**Équipe** : {', '.join(config.get('equipe', ['À définir']))}
{annexes}

Retourne UNIQUEMENT un JSON valide :
{{
  "presentation_entreprise": "Paragraphe de présentation de {COMPANY_NAME}...",
  "comprehension_besoin": "Analyse du besoin client...",
  "solution_proposee": "Description de la solution technique...",
  "methodologie": "Approche méthodologique...",
  "planning": [
    {{"phase": "Phase 1 - Préparation", "duree": "5 jours", "description": "..."}}
  ],
  "equipe_projet": [
    {{"nom_role": "Chef de projet", "responsabilites": "..."}}
  ],
  "budget_detail": [
    {{"poste": "Équipements", "montant": 0, "description": "..."}},
    {{"poste": "Main d'œuvre", "montant": 0, "description": "..."}},
    {{"poste": "Total", "montant": 0, "description": ""}}
  ],
  "valeur_ajoutee": "Nos atouts et différenciateurs...",
  "conditions_validite": "Cette offre est valide {config.get('validite_jours', 30)} jours...",
  "conditions_paiement": "{config.get('conditions_paiement', '30/40/30')}"
}}"""

        response = await client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}],
        )

        result_text = ""
        for block in response.content:
            if block.type == "text":
                result_text += block.text

        ot_content = _extract_json_from_response(result_text)
        if isinstance(ot_content, dict):
            return ot_content

        return {"presentation_entreprise": result_text}

    except Exception as e:
        logger.error(f"Erreur lors de la génération OT via IA : {e}")
        raise


async def generate_ir_content(config: dict) -> dict:
    """
    Génère le contenu d'un Rapport d'Intervention.
    Analyse les travaux réalisés, problèmes et recommandations.
    """
    try:
        prompt = f"""Tu es un ingénieur terrain senior en IT/Télécom.
Génère un rapport d'intervention technique professionnel en français.

**Client** : {config.get('client_nom', 'Client')}
**Site** : {config.get('site_intervention', '')}
**Date** : {config.get('date_intervention', '')}
**Heure** : {config.get('heure_debut', '')} - {config.get('heure_fin', '')}
**Techniciens** : {', '.join(config.get('techniciens', ['Technicien']))}
**Type** : {config.get('type_intervention', 'maintenance')}
**Mission** : {config.get('description_mission', '')}
**Travaux réalisés** : {', '.join(config.get('travaux_realises', []))}
**Observations** : {config.get('observations', 'Aucune')}
**Problèmes** : {config.get('problemes_rencontres', 'Aucun')}
**Solutions** : {config.get('solutions_appliquees', 'N/A')}
**Statut** : {config.get('statut', 'terminé')}

Retourne UNIQUEMENT un JSON valide :
{{
  "resume_intervention": "Résumé concis de l'intervention...",
  "travaux_details": [
    {{
      "numero": 1,
      "tache": "Description de la tâche",
      "statut": "terminé",
      "observations": "Observations spécifiques"
    }}
  ],
  "analyse_problemes": "Analyse technique des problèmes rencontrés...",
  "solutions_detaillees": "Détail des solutions mises en place...",
  "recommandations": [
    "Recommandation technique 1",
    "Recommandation technique 2"
  ],
  "actions_requises": [
    {{
      "action": "Description de l'action",
      "priorite": "haute/moyenne/basse",
      "responsable": "Rôle",
      "echeance": "Date ou délai"
    }}
  ],
  "conclusion": "Conclusion générale de l'intervention..."
}}"""

        response = await client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}],
        )

        result_text = ""
        for block in response.content:
            if block.type == "text":
                result_text += block.text

        ir_content = _extract_json_from_response(result_text)
        if isinstance(ir_content, dict):
            return ir_content

        return {"resume_intervention": result_text}

    except Exception as e:
        logger.error(f"Erreur lors de la génération IR via IA : {e}")
        raise


async def generate_lld_content(
    config: dict,
    bom_items: list[dict] | None = None
) -> dict:
    """
    Génère le contenu d'un Low Level Design Document.
    Utilise web_search pour les datasheets et specs techniques.
    """
    try:
        equipements_str = "\n".join(config.get("equipements_principaux", []))
        vlans_str = "\n".join(config.get("vlan_list", []))
        bom_str = ""
        if bom_items:
            bom_str = "\n".join([
                f"- {item.get('designation', '')} ({item.get('marque', '')} {item.get('modele', '')})"
                for item in bom_items
            ])

        prompt = f"""Tu es un architecte réseau/système senior.
Génère un document Low Level Design (LLD) technique détaillé en français.

**Client** : {config.get('client_nom', 'Client')}
**Projet** : {config.get('projet_titre', '')}
**Description** : {config.get('projet_description', '')}
**Type** : {config.get('type_projet', '')}
**Auteur** : {config.get('auteur', 'Ingénieur')}
**Plage IP** : {config.get('plage_ip', '192.168.0.0/16')}
**Topologie** : {config.get('topologie', 'hiérarchique 2 couches')}

**VLANs** :
{vlans_str or "À définir selon le projet"}

**Équipements principaux** :
{equipements_str}

{f"**BOM détaillé** :{chr(10)}{bom_str}" if bom_str else ""}

**Exigences sécurité** : {config.get('exigences_securite', 'Standards')}
**Exigences performance** : {config.get('exigences_performance', 'Standards')}
**Contraintes** : {config.get('contraintes', 'Aucune')}

INSTRUCTIONS :
1. Recherche les datasheets et spécifications techniques des équipements mentionnés
2. Propose un plan d'adressage IP complet et cohérent
3. Détaille les configurations par équipement

Retourne UNIQUEMENT un JSON valide :
{{
  "contexte_objectifs": "Description du contexte et des objectifs du projet...",
  "architecture_generale": "Description de l'architecture générale...",
  "specifications_equipements": [
    {{
      "nom": "Nom de l'équipement",
      "marque_modele": "Marque Modèle",
      "role": "Rôle dans l'architecture",
      "specs_techniques": "Spécifications clés (ports, débit, etc.)",
      "datasheet_url": "URL de la datasheet si trouvée",
      "configuration_principale": "Configuration recommandée"
    }}
  ],
  "plan_adressage": [
    {{
      "vlan_id": 10,
      "nom": "Nom du VLAN",
      "reseau": "192.168.10.0/24",
      "passerelle": "192.168.10.1",
      "plage_dhcp": "192.168.10.100-200",
      "usage": "Description de l'usage"
    }}
  ],
  "schema_interconnexion": "Description textuelle détaillée des interconnexions...",
  "configurations_detaillees": [
    {{
      "equipement": "Nom",
      "configuration": "Configuration détaillée (commandes ou paramètres)"
    }}
  ],
  "procedures_installation": [
    {{
      "etape": 1,
      "titre": "Titre de l'étape",
      "description": "Description détaillée",
      "validation": "Test de validation"
    }}
  ],
  "references_datasheets": [
    {{
      "equipement": "Nom",
      "url": "URL de la datasheet",
      "source": "Site source"
    }}
  ]
}}"""

        response = await client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=16384,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{"role": "user", "content": prompt}],
        )

        result_text = ""
        for block in response.content:
            if block.type == "text":
                result_text += block.text

        lld_content = _extract_json_from_response(result_text)
        if isinstance(lld_content, dict):
            return lld_content

        return {"contexte_objectifs": result_text}

    except Exception as e:
        logger.error(f"Erreur lors de la génération LLD via IA : {e}")
        raise


def _extract_json_from_response(text: str) -> dict | list | None:
    """
    Extrait un objet JSON depuis une réponse textuelle de Claude.
    Gère les cas où le JSON est entouré de markdown ou de texte.
    """
    # Essayer de parser directement
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Chercher un bloc JSON dans le texte (entre ``` ou entre [ ] ou { })
    import re
    # Chercher un bloc ```json ... ```
    json_block = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', text)
    if json_block:
        try:
            return json.loads(json_block.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Chercher le premier [ ... ] ou { ... } complet
    for start_char, end_char in [('[', ']'), ('{', '}')]:
        start_idx = text.find(start_char)
        if start_idx == -1:
            continue
        # Trouver la fermeture correspondante
        depth = 0
        for i in range(start_idx, len(text)):
            if text[i] == start_char:
                depth += 1
            elif text[i] == end_char:
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start_idx:i + 1])
                    except json.JSONDecodeError:
                        break

    logger.warning(f"Impossible d'extraire le JSON de la réponse IA (longueur: {len(text)})")
    return None
