"""
Configuration centralisée pour le système de reporting
"""

import os
from pathlib import Path

# Répertoire de base du projet
BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"

def get_config_path(env_var: str, default_path: str) -> str:
    """
    Retourne le chemin de configuration en fonction de l'environnement.
    Détecte automatiquement si on est en local ou en production.
    
    Args:
        env_var: Nom de la variable d'environnement
        default_path: Chemin par défaut (local)
        
    Returns:
        Chemin vers le fichier de configuration
    """
    # Récupère le chemin depuis les variables d'environnement
    env_path = os.getenv(env_var)
    
    if env_path and Path(env_path).exists():
        # Le fichier existe au chemin spécifié (production)
        return env_path
    else:
        # Le fichier n'existe pas, utiliser le chemin par défaut (local)
        return default_path

# Configuration des APIs
class APIConfig:
    """Configuration des APIs externes"""
    
    # Meta Ads API
    META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
    META_BUSINESS_ID = os.getenv("META_BUSINESS_ID")
    
    # Google Ads API
    GOOGLE_ADS_YAML_PATH = get_config_path("GOOGLE_ADS_YAML_PATH", str(CONFIG_DIR / "google-ads.yaml"))
    
    # Google Sheets API
    GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
    GOOGLE_CREDENTIALS_FILE = get_config_path("GOOGLE_CREDENTIALS_FILE", str(CONFIG_DIR / "credentials.json"))
    GOOGLE_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class FlaskConfig:
    """Configuration Flask"""
    
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    PORT = int(os.getenv("FLASK_PORT", "5050"))
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS", 
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000,https://scrapping-rapport.vercel.app,https://scrapping-rapport-git-main-theoctla.vercel.app"
    ).split(",")

class PathConfig:
    """Configuration des chemins"""
    
    # Fichiers de mapping
    CLIENT_MAPPINGS_FILE = CONFIG_DIR / "client_mappings.json"
    META_MAPPINGS_FILE = CONFIG_DIR / "meta_mappings.json"
    
    # Répertoire d'export
    EXPORTS_DIR = BASE_DIR / "exports"

# Classe principale de configuration
class Config:
    """Configuration principale - Point d'accès unique"""
    
    API = APIConfig()
    FLASK = FlaskConfig()
    PATHS = PathConfig()
    
    @classmethod
    def ensure_directories(cls):
        """Crée les répertoires nécessaires s'ils n'existent pas"""
        cls.PATHS.EXPORTS_DIR.mkdir(exist_ok=True)
        CONFIG_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def validate_required_vars(cls):
        """Valide que toutes les variables sensibles sont définies"""
        missing_vars = []
        
        if not cls.API.META_ACCESS_TOKEN:
            missing_vars.append("META_ACCESS_TOKEN")
        if not cls.API.META_BUSINESS_ID:
            missing_vars.append("META_BUSINESS_ID")
        if not cls.API.GOOGLE_SHEET_ID:
            missing_vars.append("GOOGLE_SHEET_ID")
        
        if missing_vars:
            raise ValueError(
                f"Variables d'environnement manquantes : {', '.join(missing_vars)}\n"
                "Créez un fichier .env avec ces variables (voir le .env.exemple)"
            ) 