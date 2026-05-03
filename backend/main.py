# Point d'entrée principal de l'API DocGen Platform
# FastAPI avec CORS, inclusion des routers documents et search

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config.settings import ALLOWED_ORIGINS, APP_ENV, COMPANY_NAME, validate_config
from routes.documents import router as documents_router
from routes.search import router as search_router

# Créer l'application FastAPI
app = FastAPI(
    title="DocGen Platform API",
    description="Plateforme de génération de documents d'entreprise avec intégration IA Claude",
    version="1.0.0",
    docs_url="/docs" if APP_ENV == "development" else None,
    redoc_url="/redoc" if APP_ENV == "development" else None,
)

# Configuration CORS pour autoriser le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# Monter le dossier outputs comme fichiers statiques
outputs_dir = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(outputs_dir, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=outputs_dir), name="outputs")

# Inclure les routers
app.include_router(documents_router, prefix="/api/documents", tags=["Documents"])
app.include_router(search_router, prefix="/api/search", tags=["Recherche"])


@app.get("/", tags=["Santé"])
async def health_check():
    """Route de vérification de santé de l'API."""
    config_status = validate_config()
    return {
        "status": "ok",
        "application": "DocGen Platform",
        "version": "1.0.0",
        "company": COMPANY_NAME,
        "environment": APP_ENV,
        "config_valid": config_status["valid"],
        "config_errors": config_status["errors"],
    }


@app.get("/api/health", tags=["Santé"])
async def api_health():
    """Route de santé pour l'API."""
    return {"status": "healthy", "service": "docgen-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=(APP_ENV == "development"))
