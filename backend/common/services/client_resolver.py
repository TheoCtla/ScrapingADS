"""
Service de résolution des clients autorisés
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from backend.config.settings import Config

class ClientResolverService:
    """Service pour résoudre les noms de clients vers leurs IDs Google Ads et Meta Ads"""
    
    def __init__(self):
        self.allowlist_path = Path(__file__).parent.parent.parent / "config" / "client_allowlist.json"
        self._load_allowlist()
    
    def _load_allowlist(self) -> None:
        """Charge la liste blanche et les mappings depuis le fichier de configuration"""
        try:
            with open(self.allowlist_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.allowlist = config.get("allowlist", [])
            self.mappings = config.get("mappings", {})
            
            logging.info(f"✅ Liste blanche chargée: {len(self.allowlist)} clients autorisés")
            logging.info(f"✅ Mappings chargés: {len(self.mappings)} configurations")
            
        except FileNotFoundError:
            logging.error(f"❌ Fichier de configuration non trouvé: {self.allowlist_path}")
            self.allowlist = []
            self.mappings = {}
        except json.JSONDecodeError as e:
            logging.error(f"❌ Erreur de parsing JSON dans {self.allowlist_path}: {e}")
            self.allowlist = []
            self.mappings = {}
        except Exception as e:
            logging.error(f"❌ Erreur lors du chargement de la liste blanche: {e}")
            self.allowlist = []
            self.mappings = {}
    
    def get_allowlist(self) -> List[str]:
        """Retourne la liste blanche des clients autorisés (triée alphabétiquement)"""
        return sorted(self.allowlist)
    
    def is_client_authorized(self, client_name: str) -> bool:
        """Vérifie si un client est dans la liste blanche"""
        return client_name in self.allowlist
    
    def resolve_client_accounts(self, client_name: str) -> Dict[str, Optional[Dict[str, str]]]:
        """
        Résout un nom de client vers ses IDs Google Ads et Meta Ads
        
        Args:
            client_name: Nom du client à résoudre
            
        Returns:
            Dict avec les clés 'googleAds' et 'metaAds', chacune contenant les IDs ou None
        """
        if not self.is_client_authorized(client_name):
            logging.warning(f"⚠️ Client non autorisé: {client_name}")
            return {"googleAds": None, "metaAds": None}
        
        client_mapping = self.mappings.get(client_name, {})
        
        resolved_accounts = {
            "googleAds": client_mapping.get("googleAds"),
            "metaAds": client_mapping.get("metaAds")
        }
        
        # Log de la résolution
        google_id = resolved_accounts["googleAds"]["customerId"] if resolved_accounts["googleAds"] else "Non configuré"
        meta_id = resolved_accounts["metaAds"]["adAccountId"] if resolved_accounts["metaAds"] else "Non configuré"
        
        logging.info(f"🔍 Résolution client '{client_name}': Google={google_id}, Meta={meta_id}")
        
        return resolved_accounts
    
    def get_available_platforms(self, client_name: str) -> List[str]:
        """
        Retourne les plateformes disponibles pour un client
        
        Args:
            client_name: Nom du client
            
        Returns:
            Liste des plateformes disponibles ('googleAds', 'metaAds')
        """
        if not self.is_client_authorized(client_name):
            return []
        
        client_mapping = self.mappings.get(client_name, {})
        available_platforms = []
        
        if client_mapping.get("googleAds"):
            available_platforms.append("googleAds")
        
        if client_mapping.get("metaAds"):
            available_platforms.append("metaAds")
        
        return available_platforms
    
    def validate_client_selection(self, client_name: str) -> Tuple[bool, str]:
        """
        Valide la sélection d'un client et retourne un message d'erreur si nécessaire
        
        Args:
            client_name: Nom du client à valider
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if not client_name:
            return False, "Aucun client sélectionné"
        
        if not self.is_client_authorized(client_name):
            return False, f"Client '{client_name}' non autorisé"
        
        available_platforms = self.get_available_platforms(client_name)
        if not available_platforms:
            return False, f"Client '{client_name}' configuré mais aucune plateforme disponible"
        
        return True, ""
    
    def get_client_info(self, client_name: str) -> Dict[str, any]:
        """
        Retourne les informations complètes d'un client
        
        Args:
            client_name: Nom du client
            
        Returns:
            Dict avec les informations du client
        """
        if not self.is_client_authorized(client_name):
            return {}
        
        client_mapping = self.mappings.get(client_name, {})
        available_platforms = self.get_available_platforms(client_name)
        
        return {
            "name": client_name,
            "authorized": True,
            "available_platforms": available_platforms,
            "google_ads": {
                "configured": bool(client_mapping.get("googleAds")),
                "customer_id": client_mapping.get("googleAds", {}).get("customerId") if client_mapping.get("googleAds") else None
            },
            "meta_ads": {
                "configured": bool(client_mapping.get("metaAds")),
                "ad_account_id": client_mapping.get("metaAds", {}).get("adAccountId") if client_mapping.get("metaAds") else None
            }
        }
