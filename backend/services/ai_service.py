import json
import logging
import google.generativeai as genai
from config.settings import GEMINI_API_KEY, GEMINI_MODEL, COMPANY_NAME

logger = logging.getLogger(__name__)

# Configurer l'API Gemini
genai.configure(api_key=GEMINI_API_KEY)


def _get_model(use_search: bool = False):
    """Retourne un modèle Gemini avec option de recherche web."""
    tools = None
    if use_search:
        tools = [{"google_search_retrieval": {}}]
    return genai.GenerativeModel(model_name=GEMINI_MODEL, tools=tools)


async def generate_bom_content(
    project_description: str,
    budget: float,
    currency: str = "MGA",
    project_type: str = "infrastructure réseau",
    specific_equipment: str = ""
) -> list[dict]:
    """Génère une liste d'équipements BOM en utilisant Gemini."""
    try:
        prompt = f"""Tu es un expert en ingénierie IT et télécom à Madagascar. 
Génère un Bill of Materials (BOM) détaillé pour ce projet.

**Projet** : {project_description}
**Type** : {project_type}
**Budget** : {budget:,.0f} {currency}
{f"**Équipements souhaités** : {specific_equipment}" if specific_equipment else ""}

INSTRUCTIONS :
1. Propose des équipements réels adaptés au projet
2. Privilégie les marques connues (Cisco, Ubiquiti, Dell, HP, Fortinet, etc.)
3. Reste dans le budget indiqué
4. Inclus les accessoires nécessaires (câbles, connecteurs, licences, etc.)

Retourne UNIQUEMENT un tableau JSON valide (sans texte avant ou après) :
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
    "url": "",
    "description": "Description courte et technique"
  }}
]

Génère entre 5 et 15 lignes d'équipements selon le projet."""

        model = _get_model()
        response = await model.generate_content_async(prompt)

        bom_items = _extract_json_from_response(response.text)
        if isinstance(bom_items, list):
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
    """Génère le contenu d'un Scope of Work structuré avec Gemini."""
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

Retourne UNIQUEMENT un objet JSON valide (sans texte avant ou après) :
{{
  "overview": "Résumé exécutif du projet...",
  "objectifs": ["Objectif 1", "Objectif 2"],
  "perimetre_inclus": ["Élément inclus 1"],
  "perimetre_exclus": ["Élément exclu 1"],
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
  "hypotheses": ["Hypothèse 1"],
  "conditions_paiement": "30% à la commande, 40% à mi-parcours, 30% à la livraison"
}}

Génère entre 5 et 10 tâches détaillées et réalistes."""

        model = _get_model()
        response = await model.generate_content_async(prompt)

        sow_content = _extract_json_from_response(response.text)
        if isinstance(sow_content, dict):
            return sow_content

        logger.warning("La réponse IA n'est pas un JSON valide pour le SOW")
        return {"overview": response.text, "taches": [], "jalons": []}

    except Exception as e:
        logger.error(f"Erreur lors de la génération SOW via IA : {e}")
        raise


async def generate_ot_content(
    config: dict,
    sow_summary: dict | None = None,
    bom_summary: list[dict] | None = None,
    use_search: bool = True
) -> dict:
    """Génère le contenu d'une Offre Technique ultra-détaillée avec recherche web."""
    try:
        # Préparation des données contextuelles
        client = config.get('client_nom', 'Client')
        projet = config.get('projet_titre', 'Projet')
        description = config.get('projet_description', '')
        
        sow_data = ""
        if sow_summary:
            sow_data = f"\n**INFOS SOW :** {json.dumps(sow_summary, ensure_ascii=False)[:2000]}"

        bom_data = ""
        if bom_summary:
            bom_data = f"\n**INFOS BOM :** {json.dumps(bom_summary, ensure_ascii=False)[:2000]}"

        prompt = f"""Tu es un expert avant-vente senior pour {COMPANY_NAME} à Madagascar.
Ta mission est de rédiger une Offre Technique (OT) d'exception pour convaincre le client.

**PROJET :**
- Client : {client}
- Titre : {projet}
- Description : {description}

{sow_data}
{bom_data}

**INSTRUCTIONS DE RÉDACTION :**
1. **RECHERCHE WEB OBLIGATOIRE** : Utilise Google Search pour trouver des détails précis sur les technologies présentes dans le BOM (ex: Proxmox, Cisco, Fortinet, etc.). Recherche leur fonctionnement, architecture type, avantages concurrentiels et derniers modèles.
2. **STYLE** : Professionnel, persuasif, technique mais accessible. Adapte le ton selon le contexte (sécurité, infrastructure, etc.).

**STRUCTURE JSON ATTENDUE :**
{{
  "section1_contexte": {{
    "contexte": "Description détaillée du contexte client.",
    "objectifs_techniques": ["Objectif 1", "Objectif 2"],
    "contraintes_enjeux": ["Contrainte 1", "Enjeu 2"],
    "analyse_besoin": "Analyse approfondie de la demande.",
    "hypotheses": ["Hypothèse structurante 1"],
    "criteres_selection": ["Critère 1 (Performance)", "Critère 2 (Coût)"]
  }},
  "section2_solutions": {{
    "solution1": {{
      "titre": "Nom de la solution principale",
      "presentation": "Présentation détaillée (issue de tes recherches).",
      "architecture": "Description de l'architecture technique proposée.",
      "fonctionnalites": ["Fonction 1", "Fonction 2"],
      "avantages_limites": "Comparaison forces/faiblesses.",
      "licence_support": "Détails sur le licensing et le support."
    }},
    "solution2": {{ "titre": "Alternative ou Option B", "presentation": "...", "architecture": "...", "fonctionnalites": [], "avantages_limites": "...", "licence_support": "..." }},
    "solution3": {{ "titre": "Option C (si pertinent)", "presentation": "...", "architecture": "...", "fonctionnalites": [], "avantages_limites": "...", "licence_support": "..." }},
    "comparaison_synthese": "Tableau ou paragraphe synthétisant pourquoi la solution 1 est recommandée."
  }},
  "section3_methodologie": {{
    "phases": [
      {{"nom": "Phase 1 : Préparation", "description": "...", "taches": []}},
      {{"nom": "Phase 2 : Implémentation", "description": "...", "taches": []}},
      {{"nom": "Phase 3 : Transfert et support", "description": "...", "taches": []}},
      {{"nom": "Phase 4 : Clôture du contrat", "description": "...", "taches": []}}
    ],
    "planning_previsionnel": "Description du calendrier global (ex: Durée totale X semaines)."
  }},
  "section4_finances": {{
    "recapitulatif": "Synthèse des coûts BOM et Prestations SOW.",
    "total_ht": 0,
    "devise": "MGA"
  }},
  "section5_annexes": ["Lien vers datasheets", "Certifications NextHope"]
}}

Retourne UNIQUEMENT le JSON."""

        model = _get_model(use_search=use_search)
        response = await model.generate_content_async(prompt)
        ot_content = _extract_json_from_response(response.text)
        
        if isinstance(ot_content, dict):
            return ot_content
        return {"error": "Format JSON invalide", "raw": response.text}

    except Exception as e:
        logger.error(f"Erreur lors de la génération OT via IA : {e}")
        raise


async def generate_ir_content(config: dict) -> dict:
    """Génère le contenu d'un Rapport d'Intervention."""
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

Retourne UNIQUEMENT un JSON valide (sans texte avant ou après) :
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
  "recommandations": ["Recommandation technique 1", "Recommandation technique 2"],
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

        model = _get_model()
        response = await model.generate_content_async(prompt)

        ir_content = _extract_json_from_response(response.text)
        if isinstance(ir_content, dict):
            return ir_content

        return {"resume_intervention": response.text}

    except Exception as e:
        logger.error(f"Erreur lors de la génération IR via IA : {e}")
        raise


async def generate_lld_content(
    config: dict,
    bom_items: list[dict] | None = None
) -> dict:
    """Génère le contenu d'un Low Level Design Document."""
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

Retourne UNIQUEMENT un objet JSON valide (sans texte avant ou après) :
{{
  "contexte_objectifs": "Description du contexte et des objectifs...",
  "architecture_generale": "Description de l'architecture...",
  "specifications_equipements": [
    {{
      "nom": "Nom de l'équipement",
      "marque_modele": "Marque Modèle",
      "role": "Rôle",
      "specs_techniques": "Spécifications clés",
      "datasheet_url": "",
      "configuration_principale": "Configuration recommandée"
    }}
  ],
  "plan_adressage": [
    {{
      "vlan_id": 10,
      "nom": "VLAN",
      "reseau": "192.168.10.0/24",
      "passerelle": "192.168.10.1",
      "plage_dhcp": "192.168.10.100-200",
      "usage": "Usage"
    }}
  ],
  "schema_interconnexion": "Description détaillée des interconnexions...",
  "configurations_detaillees": [
    {{
      "equipement": "Nom",
      "configuration": "Configuration détaillée"
    }}
  ],
  "procedures_installation": [
    {{
      "etape": 1,
      "titre": "Titre",
      "description": "Description",
      "validation": "Test de validation"
    }}
  ],
  "references_datasheets": [
    {{
      "equipement": "Nom",
      "url": "",
      "source": "Source"
    }}
  ]
}}"""

        model = _get_model()
        response = await model.generate_content_async(prompt)

        lld_content = _extract_json_from_response(response.text)
        if isinstance(lld_content, dict):
            return lld_content

        return {"contexte_objectifs": response.text}

    except Exception as e:
        logger.error(f"Erreur lors de la génération LLD via IA : {e}")
        raise


async def analyze_rfp_email(email_content: str) -> dict:
    """Analyse un email RFP et génère des propositions de BOM."""
    try:
        prompt = f"""Tu es un expert en ingénierie IT et avant-vente à Madagascar.
Analyse cet email de demande de proposition et génère 3 propositions techniques.

**Contenu de l'Email** :
{email_content}

INSTRUCTIONS :
1. Extrais les informations clés du projet (titre, client, budget estimé, type de projet)
2. Génère 3 propositions : Économique, Standard, Premium
3. Pour chaque proposition : liste d'équipements avec marques connues et prix estimés en MGA
4. Calcule le total de chaque proposition

Retourne UNIQUEMENT un objet JSON valide (sans texte avant ou après) :
{{
  "project_info": {{
    "title": "Titre suggéré du projet",
    "client": "Nom du client identifié",
    "type": "Type de projet",
    "description": "Résumé du besoin en 2-3 phrases"
  }},
  "proposals": [
    {{
      "id": 1,
      "label": "Solution Économique",
      "summary": "Justification courte de cette solution",
      "total_estimated": 15000000,
      "currency": "MGA",
      "bom_items": [
        {{
          "designation": "Nom complet de l'équipement",
          "marque": "Marque",
          "modele": "Modèle",
          "quantite": 1,
          "prix_unitaire": 500000,
          "description": "Description technique courte"
        }}
      ]
    }},
    {{
      "id": 2,
      "label": "Solution Standard",
      "summary": "Justification courte",
      "total_estimated": 25000000,
      "currency": "MGA",
      "bom_items": []
    }},
    {{
      "id": 3,
      "label": "Solution Premium",
      "summary": "Justification courte",
      "total_estimated": 45000000,
      "currency": "MGA",
      "bom_items": []
    }}
  ]
}}"""

        model = _get_model()
        response = await model.generate_content_async(prompt)

        analysis = _extract_json_from_response(response.text)
        if isinstance(analysis, dict):
            return analysis

        logger.warning("La réponse IA n'est pas un JSON valide pour l'analyse RFP")
        return {"project_info": {}, "proposals": []}

    except Exception as e:
        logger.error(f"Erreur lors de l'analyse RFP via IA : {e}")
        raise


def _extract_json_from_response(text: str) -> dict | list | None:
    """Extrait un objet JSON depuis une réponse textuelle de Gemini."""
    if not text:
        return None

    # Essai direct
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Chercher dans un bloc ```json ... ```
    import re
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