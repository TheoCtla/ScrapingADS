"""
Utilitaires de mapping Google Ads - Gestion des correspondances clients/onglets
"""

import json
import logging
from typing import Dict, List, Optional

from backend.config.settings import Config

class GoogleAdsMappingService:
    """Service pour gérer les mappings entre clients Google Ads et onglets Google Sheets"""
    
    def __init__(self):
        self.client_mappings = self._load_client_mappings()
    
    def _load_client_mappings(self) -> Dict[str, str]:
        """Charge les mappings personnalisés depuis le fichier de configuration JSON"""
        try:
            if Config.PATHS.CLIENT_MAPPINGS_FILE.exists():
                with open(Config.PATHS.CLIENT_MAPPINGS_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    mappings = config.get('mappings', {})
                    logging.info(f"📋 {len(mappings)} mappings clients Google chargés")
                    return mappings
            else:
                logging.info(f"📋 Fichier client_mappings.json non trouvé, utilisation des mappings par défaut")
        except Exception as e:
            logging.error(f"❌ Erreur lors du chargement de client_mappings.json: {e}")
        
        # Fallback : mappings par défaut en cas de problème avec le fichier JSON
        return {
            "1513412386": "Addario",  # "Addario Cuisines" -> "Addario" (plus court)
        }
    
    def get_client_sheet_mapping(self) -> Dict[str, str]:
        """Retourne les mappings clients chargés"""
        return self.client_mappings
    
    def get_sheet_name_for_customer(self, customer_id: str) -> Optional[str]:
        """
        Retourne le nom d'onglet pour un customer_id donné
        
        Args:
            customer_id: ID du client Google Ads
            
        Returns:
            Nom de l'onglet ou None si non trouvé
        """
        return self.client_mappings.get(customer_id)
    
    def clean_client_name(self, name: str) -> str:
        """
        Nettoie le nom du client pour le matching d'onglet
        
        Args:
            name: Nom du client à nettoyer
            
        Returns:
            Nom nettoyé
        """
        if not name:
            return ""
        
        # Supprimer le caractère spécial \ue83a
        cleaned = name.replace('\ue83a', '').strip()
        
        # Optionnel : autres nettoyages si nécessaire
        # cleaned = cleaned.replace(' - ', ' ')  # Exemple
        # cleaned = cleaned.replace('SAS', '').strip()  # Exemple
        
        return cleaned
    
    def find_best_sheet_match(self, client_name: str, available_sheets: List[str]) -> Optional[str]:
        """
        Trouve le meilleur onglet correspondant pour un nom de client
        
        Args:
            client_name: Nom du client
            available_sheets: Liste des onglets disponibles
            
        Returns:
            Nom de l'onglet correspondant ou None
        """
        if not client_name or not available_sheets:
            return None
        
        client_name_clean = self.clean_client_name(client_name).lower()
        
        # 1. Correspondance exacte
        for sheet in available_sheets:
            if sheet.lower() == client_name_clean:
                return sheet
        
        # 2. Correspondance contenant le nom (dans les deux sens)
        for sheet in available_sheets:
            sheet_lower = sheet.lower()
            if client_name_clean in sheet_lower or sheet_lower in client_name_clean:
                return sheet
        
        # 3. Correspondance par mots-clés principaux
        client_words = client_name_clean.split()
        for sheet in available_sheets:
            sheet_words = sheet.lower().split()
            # Si au moins 2 mots correspondent ou si le premier mot correspond
            common_words = set(client_words) & set(sheet_words)
            if len(common_words) >= 2 or (client_words and sheet_words and client_words[0] == sheet_words[0]):
                return sheet
        
        return None
    
    def add_mapping(self, customer_id: str, sheet_name: str, save_to_file: bool = True) -> bool:
        """
        Ajoute un nouveau mapping client/onglet
        
        Args:
            customer_id: ID du client Google Ads
            sheet_name: Nom de l'onglet
            save_to_file: Si True, sauvegarde dans le fichier JSON
            
        Returns:
            True si succès, False sinon
        """
        try:
            self.client_mappings[customer_id] = sheet_name
            
            if save_to_file:
                self._save_client_mappings()
            
            logging.info(f"✅ Mapping ajouté: {customer_id} -> {sheet_name}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de l'ajout du mapping: {e}")
            return False
    
    def remove_mapping(self, customer_id: str, save_to_file: bool = True) -> bool:
        """
        Supprime un mapping client/onglet
        
        Args:
            customer_id: ID du client Google Ads
            save_to_file: Si True, sauvegarde dans le fichier JSON
            
        Returns:
            True si succès, False sinon
        """
        try:
            if customer_id in self.client_mappings:
                del self.client_mappings[customer_id]
                
                if save_to_file:
                    self._save_client_mappings()
                
                logging.info(f"✅ Mapping supprimé pour: {customer_id}")
                return True
            else:
                logging.warning(f"⚠️ Aucun mapping trouvé pour: {customer_id}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Erreur lors de la suppression du mapping: {e}")
            return False
    
    def _save_client_mappings(self):
        """Sauvegarde les mappings dans le fichier JSON"""
        try:
            # Créer la structure complète du fichier
            config = {
                "_comment": "Configuration des mappings personnalisés entre clients Google Ads et onglets Google Sheet",
                "_usage": "Ajoutez ici SEULEMENT les cas où le nom Google Ads ≠ nom d'onglet souhaité",
                "_format": "customer_id: nom_onglet_souhaité",
                "mappings": self.client_mappings
            }
            
            # Créer le répertoire si nécessaire
            Config.PATHS.CLIENT_MAPPINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            with open(Config.PATHS.CLIENT_MAPPINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            logging.info(f"💾 Mappings sauvegardés dans {Config.PATHS.CLIENT_MAPPINGS_FILE}")
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de la sauvegarde des mappings: {e}")
            raise 