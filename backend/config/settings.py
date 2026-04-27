# Configuration de l'application DocGen Platform
# Charge toutes les variables d'environnement et les expose comme constantes

import os
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

# --- Clés API ---
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

# --- Configuration de l'application ---
APP_ENV: str = os.getenv("APP_ENV", "development")
ALLOWED_ORIGINS: list[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

# --- Informations de l'entreprise ---
COMPANY_NAME: str = os.getenv("COMPANY_NAME", "Ma Société")
COMPANY_LOGO_PATH: str = os.getenv("COMPANY_LOGO_PATH", "assets/logo.png")

# --- Modèle Claude ---
CLAUDE_MODEL: str = "claude-opus-4-6"

# --- Répertoire de sortie ---
OUTPUT_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")

# --- Répertoire des templates ---
TEMPLATES_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")

# Créer le dossier outputs s'il n'existe pas
os.makedirs(OUTPUT_DIR, exist_ok=True)


def validate_config() -> dict:
    """Valide que toutes les variables critiques sont configurées."""
    errors = []
    if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY.startswith("sk-ant-xxxx"):
        errors.append("ANTHROPIC_API_KEY non configurée")
    if not TAVILY_API_KEY or TAVILY_API_KEY.startswith("tvly-xxxx"):
        errors.append("TAVILY_API_KEY non configurée")
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "env": APP_ENV,
        "company": COMPANY_NAME
    }
