"""
Utilitaires de mapping Meta Ads - Gestion des correspondances comptes/onglets
"""

import json
import logging
from typing import Dict, Optional

from backend.config.settings import Config

class MetaAdsMappingService:
    """Service pour gérer les mappings entre comptes Meta Ads et onglets Google Sheets"""
    
    def __init__(self):
        self.meta_mappings = self._load_meta_mappings()
    
    def _load_meta_mappings(self) -> Dict[str, str]:
        """Charge les mappings Meta depuis un fichier de configuration"""
        try:
            if Config.PATHS.META_MAPPINGS_FILE.exists():
                with open(Config.PATHS.META_MAPPINGS_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    mappings = config.get('mappings', {})
                    logging.info(f"📋 {len(mappings)} mappings Meta chargés")
                    return mappings
            else:
                logging.info(f"📋 Fichier meta_mappings.json non trouvé, utilisation des mappings par défaut")
        except Exception as e:
            logging.error(f"❌ Erreur lors du chargement de meta_mappings.json: {e}")
        
        # Mappings par défaut vides - à remplir manuellement
        return {}
    
    def get_meta_client_mapping(self) -> Dict[str, str]:
        """Retourne les mappings Meta chargés"""
        return self.meta_mappings
    
    def get_sheet_name_for_account(self, ad_account_id: str) -> Optional[str]:
        """
        Retourne le nom d'onglet pour un ad_account_id donné
        
        Args:
            ad_account_id: ID du compte publicitaire Meta
            
        Returns:
            Nom de l'onglet ou None si non trouvé
        """
        return self.meta_mappings.get(ad_account_id)
    
    def get_meta_metrics_mapping(self) -> Dict[str, str]:
        """Mapping entre les valeurs frontend Meta et les noms de colonnes Google Sheet"""
        return {
            "meta.clicks": "Clics Meta",
            "meta.impressions": "Impressions Meta", 
            "meta.ctr": "CTR Meta",
            "meta.cpl": "CPL Meta",
            "meta.cpc": "CPC Meta",
            "meta.spend": "Cout Facebook ADS",
            "meta.contact": "Contact Meta",
            "meta.recherche_lieux": "Recherche de lieux",
        }
    
    def add_mapping(self, ad_account_id: str, sheet_name: str, save_to_file: bool = True) -> bool:
        """
        Ajoute un nouveau mapping compte Meta/onglet
        
        Args:
            ad_account_id: ID du compte publicitaire Meta
            sheet_name: Nom de l'onglet
            save_to_file: Si True, sauvegarde dans le fichier JSON
            
        Returns:
            True si succès, False sinon
        """
        try:
            self.meta_mappings[ad_account_id] = sheet_name
            
            if save_to_file:
                self._save_meta_mappings()
            
            logging.info(f"✅ Mapping Meta ajouté: {ad_account_id} -> {sheet_name}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de l'ajout du mapping Meta: {e}")
            return False
    
    def remove_mapping(self, ad_account_id: str, save_to_file: bool = True) -> bool:
        """
        Supprime un mapping compte Meta/onglet
        
        Args:
            ad_account_id: ID du compte publicitaire Meta
            save_to_file: Si True, sauvegarde dans le fichier JSON
            
        Returns:
            True si succès, False sinon
        """
        try:
            if ad_account_id in self.meta_mappings:
                del self.meta_mappings[ad_account_id]
                
                if save_to_file:
                    self._save_meta_mappings()
                
                logging.info(f"✅ Mapping Meta supprimé pour: {ad_account_id}")
                return True
            else:
                logging.warning(f"⚠️ Aucun mapping Meta trouvé pour: {ad_account_id}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Erreur lors de la suppression du mapping Meta: {e}")
            return False
    
    def _save_meta_mappings(self):
        """Sauvegarde les mappings Meta dans le fichier JSON"""
        try:
            # Créer la structure complète du fichier
            config = {
                "description": "Mappings des comptes Meta Ads vers les onglets Google Sheets",
                "version": "2.0",
                "last_updated": "Auto-generated",
                "mappings": self.meta_mappings,
                "notes": [
                    "Les account_ids Meta sont récupérés via /list-meta-accounts",
                    "Les noms d'onglets doivent correspondre exactement à ceux du Google Sheet",
                    "Ce fichier est utilisé par get_meta_client_mapping() dans les services Meta",
                    f"Généré automatiquement avec {len(self.meta_mappings)} mappings"
                ]
            }
            
            # Créer le répertoire si nécessaire
            Config.PATHS.META_MAPPINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            with open(Config.PATHS.META_MAPPINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logging.info(f"💾 Mappings Meta sauvegardés dans {Config.PATHS.META_MAPPINGS_FILE}")
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de la sauvegarde des mappings Meta: {e}")
            raise 