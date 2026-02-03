import os
import json
import yaml
import logging
from pathlib import Path
from typing import List, Optional
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from backend.config.settings import Config

def get_user_credentials(scopes: List[str]) -> Credentials:
    """
    Obtient les crédentiels utilisateur via OAuth2 (avec fenêtre de login si nécessaire).
    Réutilise les identifiants présents dans google-ads.yaml pour éviter un nouveau fichier JSON.
    Sauvegarde le token dans token.json pour les prochaines fois.
    """
    creds = None
    token_path = Config.API.GOOGLE_TOKEN_PATH
    
    # 1. Charger le token existant s'il y en a un
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, scopes)
            logging.info("✅ Token OAuth existant chargé")
            
            # Vérifier s'il est valide et contient les bons scopes
            if creds and creds.valid:
                # Vérification basique des scopes (si nécessaire, on peut forcer le refresh)
                return creds
        except Exception as e:
            logging.warning(f"⚠️ Erreur chargement token, nouvelle connexion requise: {e}")

    # 2. Si pas de token valide, on lance le flow de connexion
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                logging.info("🔄 Rafraîchissement du token OAuth...")
                creds.refresh(Request())
            except Exception as e:
                logging.warning(f"⚠️ Échec du rafraîchissement: {e}")
                creds = None

        if not creds:
            logging.info("🚀 Lancement du flow d'authentification OAuth2 (navigateur)...")
            
            # Récupérer client_id/secret depuis google-ads.yaml
            client_config = _get_client_config_from_yaml()
            
            flow = InstalledAppFlow.from_client_config(
                client_config,
                scopes
            )
            
            # Lance un serveur local pour recevoir le callback
            creds = flow.run_local_server(port=0)
        
        # 3. Sauvegarder le nouveau token
        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())
            logging.info(f"💾 Nouveau token sauvegardé dans {token_path}")

    return creds

def _get_client_config_from_yaml() -> dict:
    """
    Extrait client_id et client_secret de google-ads.yaml et construit
    la structure attendue par InstalledAppFlow (format client_secret.json).
    """
    yaml_path = Config.API.GOOGLE_ADS_YAML_PATH
    
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"Fichier de config introuvable: {yaml_path}")
        
    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)
        
    client_id = config.get('client_id')
    client_secret = config.get('client_secret')
    
    if not client_id or not client_secret:
        raise ValueError("client_id ou client_secret manquant dans google-ads.yaml")
        
    # Structure "Web application" ou "Installed application" pour google-auth-oauthlib
    return {
        "installed": {
            "client_id": client_id,
            "project_id": "scrappingrapport", # Valeur par défaut, peu importe pour le flow
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": client_secret,
            "redirect_uris": ["http://localhost"]
        }
    }
