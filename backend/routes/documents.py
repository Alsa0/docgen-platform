# Routes pour la génération de documents
# POST /generate, GET /templates, POST /preview

import json
import os
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from config.settings import TEMPLATES_DIR
from services import ai_service, doc_generator, excel_generator

logger = logging.getLogger(__name__)
router = APIRouter()


class GenerateRequest(BaseModel):
    """Requête de génération de document."""
    doc_type: str  # bom, sow, ot, ir, lld
    config: dict
    use_ai: bool = True
    include_bom: bool = False
    include_sow: bool = False
    bom_items: list[dict] = []
    export_format: str = "docx"  # docx or xlsx


class PreviewRequest(BaseModel):
    """Requête d'aperçu de document."""
    doc_type: str
    config: dict


class RFPRequest(BaseModel):
    """Requête d'analyse d'email RFP."""
    email_content: str


@router.get("/templates")
async def get_templates():
    """Retourne la liste des 5 templates avec leurs champs."""
    try:
        templates = {}
        for doc_type in ["bom", "sow", "ot", "ir", "lld"]:
            template_path = os.path.join(TEMPLATES_DIR, f"{doc_type}.json")
            if os.path.exists(template_path):
                with open(template_path, "r", encoding="utf-8") as f:
                    templates[doc_type] = json.load(f)
        return {"templates": templates}
    except Exception as e:
        logger.error(f"Erreur chargement templates : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate_document(request: GenerateRequest):
    """
    Génère un document DOCX selon le type et la configuration.
    Retourne le fichier en téléchargement.
    """
    try:
        config = request.config
        doc_type = request.doc_type.lower()
        bom_items = request.bom_items or []

        # --- BOM ---
        if doc_type == "bom":
            if request.use_ai and not bom_items:
                bom_items = await ai_service.generate_bom_content(
                    project_description=config.get("projet_description", ""),
                    budget=config.get("budget_total", 0),
                    currency=config.get("devise", "MGA"),
                    project_type=config.get("type_projet", ""),
                    specific_equipment=config.get("equipements_libres", ""),
                )
            
            if request.export_format == "xlsx":
                filepath = excel_generator.generate_excel_bom(config, bom_items)
            else:
                filepath = doc_generator.generate_bom_docx(config, bom_items)

        # --- SOW ---
        elif doc_type == "sow":
            sow_content = {}
            if request.use_ai:
                if request.include_bom and not bom_items:
                    bom_items = await ai_service.generate_bom_content(
                        project_description=config.get("projet_description", ""),
                        budget=config.get("budget_equipements", 0),
                        currency=config.get("devise", "MGA"),
                        project_type=config.get("type_projet", ""),
                    )
                    config=config,
                    bom_items=bom_items if request.include_bom else None,
                )
            
            if request.export_format == "xlsx":
                filepath = excel_generator.generate_excel_sow(config, sow_content, bom_items if request.include_bom else None)
            else:
                filepath = doc_generator.generate_sow_docx(
                    config, sow_content, bom_items if request.include_bom else None
                )

        # --- OT ---
        elif doc_type == "ot":
            sow_summary = None
            bom_summary = None
            if request.use_ai:
                if request.include_sow:
                    sow_summary = await ai_service.generate_sow_content(
                        project_description=config.get("projet_description", ""),
                        config=config,
                    )
                if request.include_bom and not bom_items:
                    bom_items = await ai_service.generate_bom_content(
                        project_description=config.get("projet_description", ""),
                        budget=config.get("budget_total", 0),
                        currency=config.get("devise", "MGA"),
                        project_type=config.get("type_projet", ""),
                    )
                    bom_summary = bom_items
                ot_content = await ai_service.generate_ot_content(
                    config=config,
                    sow_summary=sow_summary,
                    bom_summary=bom_summary,
                )
            else:
                ot_content = {}
            filepath = doc_generator.generate_ot_docx(config, ot_content, sow_summary, bom_summary)

        # --- IR ---
        elif doc_type == "ir":
            ir_content = {}
            if request.use_ai:
                ir_content = await ai_service.generate_ir_content(config=config)
            filepath = doc_generator.generate_ir_docx(config, ir_content)

        # --- LLD ---
        elif doc_type == "lld":
            if request.use_ai:
                if request.include_bom and not bom_items:
                    bom_items = await ai_service.generate_bom_content(
                        project_description=config.get("projet_description", ""),
                        budget=config.get("budget_total", 0),
                        currency=config.get("devise", "MGA"),
                        project_type=config.get("type_projet", ""),
                    )
                lld_content = await ai_service.generate_lld_content(
                    config=config,
                    bom_items=bom_items if request.include_bom else None,
                )
            else:
                lld_content = {}
            filepath = doc_generator.generate_lld_docx(
                config, lld_content, bom_items if request.include_bom else None
            )

        else:
            raise HTTPException(status_code=400, detail=f"Type de document inconnu : {doc_type}")

        # Retourner le fichier
        filename = os.path.basename(filepath)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        if filepath.endswith(".xlsx"):
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type=media_type,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur génération document {request.doc_type} : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de génération : {str(e)}")


@router.post("/preview")
async def preview_document(request: PreviewRequest):
    """Retourne un aperçu HTML du document (structure simplifiée)."""
    try:
        config = request.config
        doc_type = request.doc_type.lower()
        template_path = os.path.join(TEMPLATES_DIR, f"{doc_type}.json")

        if not os.path.exists(template_path):
            raise HTTPException(status_code=404, detail=f"Template {doc_type} introuvable")

        with open(template_path, "r", encoding="utf-8") as f:
            template = json.load(f)

        # Générer un aperçu HTML simple
        html = f"<h1>{template['title']}</h1>"
        html += f"<p><em>{template['description']}</em></p>"
        html += "<hr/>"

        for field_name, field_def in template.get("fields", {}).items():
            value = config.get(field_name, "")
            label = field_def.get("label", field_name)
            if value:
                if isinstance(value, list):
                    html += f"<p><strong>{label}</strong> :</p><ul>"
                    for item in value:
                        html += f"<li>{item}</li>"
                    html += "</ul>"
                else:
                    html += f"<p><strong>{label}</strong> : {value}</p>"

        return {"html": html, "doc_type": doc_type, "title": template["title"]}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur aperçu document : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-rfp")
async def analyze_rfp(request: RFPRequest):
    """
    Analyse un email RFP et retourne des propositions de BOM.
    """
    try:
        if not request.email_content:
            raise HTTPException(status_code=400, detail="Le contenu de l'email est requis")
            
        analysis = await ai_service.analyze_rfp_email(request.email_content)
        return analysis
    except Exception as e:
        logger.error(f"Erreur analyse RFP : {e}")
        raise HTTPException(status_code=500, detail=str(e))
