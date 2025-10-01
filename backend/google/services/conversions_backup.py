"""
Service de conversions Google Ads - Gestion des conversions Contact et Itinéraires
"""

import logging
from typing import Tuple, List, Dict, Any
from google.ads.googleads.errors import GoogleAdsException

from backend.google.services.authentication import GoogleAdsAuthService
from backend.common.services.google_sheets import GoogleSheetsService

class GoogleAdsConversionsService:
    """Service pour gérer les conversions Google Ads"""
    
    def __init__(self):
        self.auth_service = GoogleAdsAuthService()
        self.sheets_service = GoogleSheetsService()
        
        # Noms des conversions à chercher (insensible à la casse)
        self.TARGET_CONTACT_NAMES = [
            "appels",
            "cta", 
            "appel (cta)",
            "clicks to call"
        ]
        
        self.TARGET_DIRECTIONS_NAMES = [
            "itinéraires",
            "local actions - directions", 
            "itinéraires magasin",
            "click map"
        ]
    
    def get_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact pour un customer donné
        
        Args:
            customer_id: ID du client Google Ads
            start_date: Date de début (YYYY-MM-DD)
            end_date: Date de fin (YYYY-MM-DD)
            
        Returns:
            Tuple (total_conversions, found_conversions)
        """
        total_conversions = 0
        found_conversions = []
        
        try:
            # Requête pour récupérer les conversion actions et leurs métriques
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🔍 Recherche des conversions Contact pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for batch in response:
                for row in batch.results:
                    conversion_name = row.segments.conversion_action_name.lower().strip()
                    
                    # Vérifier si le nom correspond à l'un des noms cibles
                    if any(target_name in conversion_name for target_name in self.TARGET_CONTACT_NAMES):
                        conversions_value = row.metrics.all_conversions or 0
                        total_conversions += conversions_value
                        found_conversions.append({
                            'name': row.segments.conversion_action_name,
                            'id': row.segments.conversion_action,
                            'conversions': conversions_value
                        })
                        logging.info(f"✅ Conversion Contact trouvée: {row.segments.conversion_action_name} = {conversions_value}")
            
            if found_conversions:
                logging.info(f"📊 Total conversions Contact pour {customer_id}: {total_conversions}")
            else:
                logging.warning(f"⚠️ Aucune conversion de type 'Contact' trouvée pour le compte {customer_id}")
            
            return total_conversions, found_conversions
            
        except GoogleAdsException as ex:
            logging.error(f"❌ GoogleAds API error pour {customer_id}: {ex.error.code().name}")
            for error in ex.failure.errors:
                logging.error(f"   - {error.message}")
            # Retourner les données trouvées même en cas d'erreur
            if found_conversions:
                logging.info(f"🔄 Retour des données partielles trouvées: {total_conversions} conversions")
            return total_conversions, found_conversions
        except Exception as e:
            logging.error(f"❌ Erreur lors de la récupération des conversions Contact pour {customer_id}: {e}")
            # Retourner les données trouvées même en cas d'erreur
            if found_conversions:
                logging.info(f"🔄 Retour des données partielles trouvées: {total_conversions} conversions")
            return total_conversions, found_conversions
    
    def get_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires pour un customer donné
        
        Args:
            customer_id: ID du client Google Ads
            start_date: Date de début (YYYY-MM-DD)
            end_date: Date de fin (YYYY-MM-DD)
            
        Returns:
            Tuple (total_conversions, found_conversions)
        """
        total_conversions = 0
        found_conversions = []
        
        try:
            # Même requête que pour les contacts
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🔍 Recherche des conversions Itinéraires pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for batch in response:
                for row in batch.results:
                    conversion_name = row.segments.conversion_action_name.lower().strip()
                    
                    # Vérifier si le nom correspond à l'un des noms cibles d'Itinéraires
                    if any(target_name.lower() in conversion_name for target_name in self.TARGET_DIRECTIONS_NAMES):
                        conversions_value = row.metrics.all_conversions or 0
                        total_conversions += conversions_value
                        found_conversions.append({
                            'name': row.segments.conversion_action_name,
                            'id': row.segments.conversion_action,
                            'conversions': conversions_value
                        })
                        logging.info(f"✅ Conversion Itinéraires trouvée: {row.segments.conversion_action_name} = {conversions_value}")
            
            if found_conversions:
                logging.info(f"📊 Total conversions Itinéraires pour {customer_id}: {total_conversions}")
            else:
                print(f"[{customer_id}] Aucune conversion Itinéraires trouvée, valeur 0 envoyée.")
                logging.warning(f"⚠️ Aucune conversion de type 'Itinéraires' trouvée pour le compte {customer_id}")
            
            return total_conversions, found_conversions
            
        except GoogleAdsException as ex:
            logging.error(f"❌ GoogleAds API error pour {customer_id}: {ex.error.code().name}")
            for error in ex.failure.errors:
                logging.error(f"   - {error.message}")
            # Retourner les données trouvées même en cas d'erreur
            if found_conversions:
                logging.info(f"🔄 Retour des données partielles trouvées: {total_conversions} conversions")
            return total_conversions, found_conversions
        except Exception as e:
            logging.error(f"❌ Erreur lors de la récupération des conversions Itinéraires pour {customer_id}: {e}")
            # Retourner les données trouvées même en cas d'erreur
            if found_conversions:
                logging.info(f"🔄 Retour des données partielles trouvées: {total_conversions} conversions")
            return total_conversions, found_conversions
    
    def update_contact_conversions_in_sheet(self, client_name: str, month: str, conversions_total: int) -> bool:
        """
        Met à jour les conversions Contact dans le Google Sheet
        
        Args:
            client_name: Nom du client (onglet)
            month: Mois à mettre à jour
            conversions_total: Nombre total de conversions
            
        Returns:
            True si succès, False sinon
        """
        try:
            # Vérifier que l'onglet existe
            available_sheets = self.sheets_service.get_worksheet_names()
            if client_name not in available_sheets:
                logging.error(f"❌ Onglet '{client_name}' non trouvé dans le Google Sheet")
                return False
            
            # Trouver la ligne du mois
            row_number = self.sheets_service.get_row_for_month(client_name, month)
            if row_number is None:
                logging.error(f"❌ Mois '{month}' non trouvé dans l'onglet '{client_name}'")
                return False
            
            # Trouver la colonne "Contact" (essayer différentes variantes)
            column_letter = self.sheets_service.get_column_for_metric(client_name, "Contact")
            if column_letter is None:
                column_letter = self.sheets_service.get_column_for_metric(client_name, "contact")
            if column_letter is None:
                logging.error(f"❌ Colonne 'Contact' non trouvée dans l'onglet '{client_name}'")
                return False
            
            # Mettre à jour la cellule
            cell_range = f"{column_letter}{row_number}"
            success = self.sheets_service.update_single_cell(client_name, cell_range, conversions_total)
            
            if success:
                logging.info(f"✅ Conversions Contact mises à jour: {conversions_total} dans {client_name}")
            
            return success
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de la mise à jour Contact dans le Google Sheet: {e}")
            return False
    
    def update_directions_conversions_in_sheet(self, client_name: str, month: str, conversions_total: int) -> bool:
        """
        Met à jour les conversions Itinéraires dans le Google Sheet
        
        Args:
            client_name: Nom du client (onglet)
            month: Mois à mettre à jour
            conversions_total: Nombre total de conversions
            
        Returns:
            True si succès, False sinon
        """
        try:
            # Vérifier que l'onglet existe
            available_sheets = self.sheets_service.get_worksheet_names()
            if client_name not in available_sheets:
                logging.error(f"❌ Onglet '{client_name}' non trouvé dans le Google Sheet")
                return False
            
            # Trouver la ligne du mois
            row_number = self.sheets_service.get_row_for_month(client_name, month)
            if row_number is None:
                logging.error(f"❌ Mois '{month}' non trouvé dans l'onglet '{client_name}'")
                return False
            
            # Trouver la colonne "Itinéraires" (essayer différentes variantes)
            column_letter = self.sheets_service.get_column_for_metric(client_name, "Itinéraires")
            if column_letter is None:
                column_letter = self.sheets_service.get_column_for_metric(client_name, "itinéraires")
            if column_letter is None:
                # Essayer avec "Demande d'itineraires" 
                column_letter = self.sheets_service.get_column_for_metric(client_name, "Demande d'itineraires")
            if column_letter is None:
                # Essayer avec "demande d'itineraires" 
                column_letter = self.sheets_service.get_column_for_metric(client_name, "demande d'itineraires")
            
            if column_letter is None:
                logging.error(f"❌ Colonne 'Itinéraires' non trouvée dans l'onglet '{client_name}'")
                return False
            
            # Mettre à jour la cellule
            cell_range = f"{column_letter}{row_number}"
            success = self.sheets_service.update_single_cell(client_name, cell_range, conversions_total)
            
            if success:
                logging.info(f"✅ Conversions Itinéraires mises à jour: {conversions_total} dans {client_name}")
            
            return success
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de la mise à jour Itinéraires dans le Google Sheet: {e}")
            return False
    
    def scrape_contact_conversions_for_customer(self, customer_id: str, client_name: str, 
                                               start_date: str, end_date: str, month: str) -> Dict[str, Any]:
        """
        Fonction principale pour scraper les conversions Contact d'un client et les ajouter au Google Sheet
        
        Args:
            customer_id: ID du client Google Ads
            client_name: Nom du client (onglet)
            start_date: Date de début
            end_date: Date de fin
            month: Mois à mettre à jour
            
        Returns:
            Dictionnaire avec le résultat de l'opération
        """
        try:
            logging.info(f"🎯 Début du scraping Contact pour {client_name} (ID: {customer_id})")
            
            # Récupérer les données de conversions Contact
            total_conversions, found_conversions = self.get_contact_conversions_data(
                customer_id, start_date, end_date
            )
            
            # Mettre à jour le Google Sheet
            success = self.update_contact_conversions_in_sheet(client_name, month, total_conversions)
            
            if success:
                logging.info(f"🎉 Scraping Contact terminé avec succès pour {client_name}")
                return {
                    'success': True,
                    'total_conversions': total_conversions,
                    'found_conversions': found_conversions
                }
            else:
                logging.error(f"❌ Échec de la mise à jour du Google Sheet pour {client_name}")
                return {
                    'success': False,
                    'total_conversions': total_conversions,
                    'found_conversions': found_conversions
                }
        
        except Exception as e:
            logging.error(f"❌ Erreur lors du scraping Contact pour {client_name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def scrape_directions_conversions_for_customer(self, customer_id: str, client_name: str,
                                                  start_date: str, end_date: str, month: str) -> Dict[str, Any]:
        """
        Fonction principale pour scraper les conversions Itinéraires d'un client et les ajouter au Google Sheet
        
        Args:
            customer_id: ID du client Google Ads
            client_name: Nom du client (onglet)
            start_date: Date de début
            end_date: Date de fin
            month: Mois à mettre à jour
            
        Returns:
            Dictionnaire avec le résultat de l'opération
        """
        try:
            logging.info(f"🎯 Début du scraping Itinéraires pour {client_name} (ID: {customer_id})")
            
            # Récupérer les données de conversions Itinéraires
            total_conversions, found_conversions = self.get_directions_conversions_data(
                customer_id, start_date, end_date
            )
            
            # Mettre à jour le Google Sheet
            success = self.update_directions_conversions_in_sheet(client_name, month, total_conversions)
            
            if success:
                logging.info(f"🎉 Scraping Itinéraires terminé avec succès pour {client_name}")
                return {
                    'success': True,
                    'total_conversions': total_conversions,
                    'found_conversions': found_conversions
                }
            else:
                logging.error(f"❌ Échec de la mise à jour du Google Sheet pour {client_name}")
                return {
                    'success': False,
                    'total_conversions': total_conversions,
                    'found_conversions': found_conversions
                }
        
        except Exception as e:
            logging.error(f"❌ Erreur lors du scraping Itinéraires pour {client_name}: {e}")
            return {
                'success': False,
                'error': str(e)
            } 