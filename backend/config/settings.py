# Configuration de l'application DocGen Platform
# Charge toutes les variables d'environnement et les expose comme constantes

import os
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

# --- Clés API ---
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

# --- Configuration de l'application ---
APP_ENV: str = os.getenv("APP_ENV", "development")
ALLOWED_ORIGINS: list[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

# --- Informations de l'entreprise ---
COMPANY_NAME: str = os.getenv("COMPANY_NAME", "Ma Société")
COMPANY_LOGO_PATH: str = os.getenv("COMPANY_LOGO_PATH", "assets/logo.png")

# --- Modèle Gemini ---
GEMINI_MODEL: str = "gemini-2.5-flash"

# --- Répertoire de sortie ---
OUTPUT_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")

# --- Répertoire des templates ---
TEMPLATES_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")

# Créer le dossier outputs s'il n'existe pas
os.makedirs(OUTPUT_DIR, exist_ok=True)


def validate_config() -> dict:
    errors = []
    if not GEMINI_API_KEY:
        errors.append("GEMINI_API_KEY non configurée")
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "env": APP_ENV,
        "company": COMPANY_NAME
    }
