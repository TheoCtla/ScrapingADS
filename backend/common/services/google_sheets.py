"""
Service Google Sheets - Gestion centralisée des opérations Google Sheets
"""

import logging
from typing import Optional, List, Dict, Any
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

from backend.config.settings import Config

class GoogleSheetsService:
    """Service pour gérer les interactions avec Google Sheets"""
    
    def __init__(self):
        self.service = None
        self.sheet_id = Config.API.GOOGLE_SHEET_ID
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialise le service Google Sheets"""
        try:
            credentials = Credentials.from_service_account_file(
                Config.API.GOOGLE_CREDENTIALS_FILE, 
                scopes=Config.API.GOOGLE_SCOPES
            )
            self.service = build('sheets', 'v4', credentials=credentials)
            logging.info("✅ Service Google Sheets initialisé avec succès")
        except Exception as e:
            logging.error(f"❌ Erreur lors de l'initialisation du service Google Sheets: {e}")
            raise
    
    def get_worksheet_names(self) -> List[str]:
        """Récupère la liste des noms d'onglets dans le spreadsheet"""
        try:
            spreadsheet = self.service.spreadsheets().get(spreadsheetId=self.sheet_id).execute()
            sheet_names = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
            logging.info(f"📋 Onglets trouvés: {sheet_names}")
            return sheet_names
        except Exception as e:
            logging.error(f"❌ Erreur lors de la récupération des onglets: {e}")
            raise
    
    def get_row_for_month(self, worksheet_name: str, month: str) -> Optional[int]:
        """
        Trouve le numéro de ligne contenant le mois spécifié dans la colonne A
        Convertit automatiquement le mois français en anglais pour la recherche
        
        Args:
            worksheet_name: Nom de l'onglet
            month: Mois à rechercher (peut être en français)
            
        Returns:
            Numéro de ligne (1-indexed) ou None si non trouvé
        """
        try:
            # Conversion des mois français vers anglais
            french_to_english_months = {
                'janvier': 'January',
                'février': 'February', 
                'mars': 'March',
                'avril': 'April',
                'mai': 'May',
                'juin': 'June',
                'juillet': 'July',
                'août': 'August',
                'septembre': 'September',
                'octobre': 'October',
                'novembre': 'November',
                'décembre': 'December'
            }
            
            # Convertir le mois en anglais si nécessaire
            month_to_search = month
            for french_month, english_month in french_to_english_months.items():
                if french_month in month.lower():
                    month_to_search = month.replace(french_month, english_month)
                    break
            
            range_name = f"'{worksheet_name}'!A:A"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            logging.info(f"🔍 Recherche du mois '{month_to_search}' (original: '{month}') dans l'onglet '{worksheet_name}'")
            
            for i, row in enumerate(values):
                if row and len(row) > 0 and row[0].strip() == month_to_search.strip():
                    row_number = i + 1  # 1-indexed
                    logging.info(f"✅ Mois '{month_to_search}' trouvé à la ligne {row_number}")
                    return row_number
            
            logging.warning(f"⚠️ Mois '{month_to_search}' non trouvé dans l'onglet '{worksheet_name}'")
            return None
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de la recherche du mois: {e}")
            raise
    
    def get_column_for_metric(self, worksheet_name: str, metric_name: str) -> Optional[str]:
        """
        Trouve la lettre de colonne contenant la métrique spécifiée dans la ligne 2
        
        Args:
            worksheet_name: Nom de l'onglet
            metric_name: Nom de la métrique à rechercher
            
        Returns:
            Lettre de colonne (A, B, C...) ou None si non trouvé
        """
        try:
            range_name = f"'{worksheet_name}'!2:2"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values or len(values) == 0:
                logging.warning(f"⚠️ Aucune donnée trouvée dans la ligne 2 de l'onglet '{worksheet_name}'")
                return None
            
            headers = values[0]
            logging.info(f"🔍 En-têtes trouvés dans '{worksheet_name}': {headers}")
            
            for i, header in enumerate(headers):
                if header and header.strip() == metric_name.strip():
                    # Convertir l'index en lettre de colonne
                    column_letter = self._index_to_column_letter(i)
                    logging.info(f"✅ Métrique '{metric_name}' trouvée dans la colonne {column_letter}")
                    return column_letter
            
            logging.warning(f"⚠️ Métrique '{metric_name}' non trouvée dans l'onglet '{worksheet_name}'")
            return None
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de la recherche de la métrique: {e}")
            raise
    
    def _index_to_column_letter(self, index: int) -> str:
        """Convertit un index numérique en lettre de colonne (A, B, ..., Z, AA, AB, etc.)"""
        column_letter = ""
        num = index
        while True:
            column_letter = chr(ord('A') + (num % 26)) + column_letter
            num = num // 26
            if num == 0:
                break
            num -= 1
        return column_letter
    
    def update_sheet_data(self, worksheet_name: str, updates: List[Dict[str, Any]]) -> List[str]:
        """
        Met à jour les cellules du sheet avec les données fournies
        
        Args:
            worksheet_name: Nom de l'onglet
            updates: Liste de dictionnaires avec 'range' et 'value'
            
        Returns:
            Liste des mises à jour effectuées
        """
        try:
            if not updates:
                logging.warning("⚠️ Aucune mise à jour à effectuer")
                return []

            # Préparer les données pour batchUpdate
            batch_update_data = {
                'valueInputOption': 'RAW',
                'data': []
            }
            
            for update in updates:
                batch_update_data['data'].append({
                    'range': f"'{worksheet_name}'!{update['range']}",
                    'values': [[update['value']]]
                })
            
            logging.info(f"📊 Préparation de la mise à jour batch pour {len(updates)} cellules")
            logging.info(f"📋 Données à mettre à jour: {batch_update_data}")
            
            # Exécuter la mise à jour
            result = self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=self.sheet_id,
                body=batch_update_data
            ).execute()
            
            updated_cells = result.get('totalUpdatedCells', 0)
            logging.info(f"✅ Mise à jour réussie: {updated_cells} cellules modifiées")
            
            return [f"{update['range']}: {update['value']}" for update in updates]
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de la mise à jour du sheet: {e}")
            raise
    
    def update_single_cell(self, worksheet_name: str, cell_range: str, value: Any) -> bool:
        """
        Met à jour une seule cellule
        
        Args:
            worksheet_name: Nom de l'onglet
            cell_range: Range de la cellule (ex: "A1")
            value: Valeur à insérer
            
        Returns:
            True si succès, False sinon
        """
        try:
            full_range = f"'{worksheet_name}'!{cell_range}"
            body = {'values': [[value]]}
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id,
                range=full_range,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logging.info(f"✅ Cellule {full_range} mise à jour avec la valeur {value}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de la mise à jour de la cellule: {e}")
            return False 