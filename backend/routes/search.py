# Routes pour la recherche web d'équipements, datasheets et prix
# Utilise le service web_search avec Claude web_search tool

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services import web_search

logger = logging.getLogger(__name__)
router = APIRouter()


class EquipmentSearchRequest(BaseModel):
    """Requête de recherche d'équipements."""
    query: str
    project_type: str = ""
    budget_range: str = ""
    currency: str = "MGA"


class DatasheetSearchRequest(BaseModel):
    """Requête de recherche de datasheet."""
    equipment_name: str
    brand: str = ""
    model: str = ""


class PriceSearchRequest(BaseModel):
    """Requête de recherche de prix."""
    equipment_list: list[dict]


@router.post("/equipment")
async def search_equipment(request: EquipmentSearchRequest):
    """Recherche d'équipements sur internet avec prix et fournisseurs."""
    try:
        results = await web_search.search_equipment(
            query=request.query,
            project_type=request.project_type,
            budget_range=request.budget_range,
            currency=request.currency,
        )
        return {
            "results": results,
            "count": len(results),
            "query": request.query,
        }
    except Exception as e:
        logger.error(f"Erreur recherche équipements : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de recherche : {str(e)}")


@router.post("/datasheet")
async def search_datasheet(request: DatasheetSearchRequest):
    """Recherche de fiche technique / datasheet d'un équipement."""
    try:
        result = await web_search.search_datasheet(
            equipment_name=request.equipment_name,
            brand=request.brand,
            model=request.model,
        )
        return {"result": result}
    except Exception as e:
        logger.error(f"Erreur recherche datasheet : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de recherche : {str(e)}")


@router.post("/prices")
async def search_prices(request: PriceSearchRequest):
    """Enrichit une liste d'équipements avec les prix du marché."""
    try:
        results = await web_search.search_prices(
            equipment_list=request.equipment_list,
        )
        return {
            "results": results,
            "count": len(results),
        }
    except Exception as e:
        logger.error(f"Erreur recherche prix : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de recherche : {str(e)}")
