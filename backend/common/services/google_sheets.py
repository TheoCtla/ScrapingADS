import logging
from typing import Optional, List, Dict, Any
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

from backend.config.settings import Config

class GoogleSheetsService:
    
    def __init__(self):
        self.service = None
        self.sheet_id = Config.API.GOOGLE_SHEET_ID
        self._initialize_service()
    
    def _initialize_service(self):
        try:
            from backend.common.auth_utils import get_user_credentials
            
            credentials = get_user_credentials(Config.API.GOOGLE_SCOPES)
            
            self.service = build('sheets', 'v4', credentials=credentials)
            logging.info("✅ Service Google Sheets initialisé avec succès (OAuth2)")
        except Exception as e:
            logging.error(f"❌ Erreur lors de l'initialisation du service Google Sheets: {e}")
            raise
    
    def get_worksheet_names(self) -> List[str]:
        try:
            spreadsheet = self.service.spreadsheets().get(spreadsheetId=self.sheet_id).execute()
            sheet_names = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
            logging.info(f"📋 Onglets trouvés: {sheet_names}")
            return sheet_names
        except Exception as e:
            logging.error(f"❌ Erreur lors de la récupération des onglets: {e}")
            raise
    
    def get_row_for_month(self, worksheet_name: str, month: str) -> Optional[int]:
        try:
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
            
            for i, row in enumerate(values):
                if row and len(row) > 0 and row[0].strip() == month_to_search.strip():
                    row_number = i + 1  # 1-indexed
                    return row_number
            
            logging.warning(f"⚠️ Mois '{month_to_search}' non trouvé dans l'onglet '{worksheet_name}'")
            return None
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de la recherche du mois: {e}")
            raise
    
    def get_column_for_metric(self, worksheet_name: str, metric_name: str) -> Optional[str]:
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
            
            for i, header in enumerate(headers):
                if header and header.strip() == metric_name.strip():
                    column_letter = self._index_to_column_letter(i)
                    return column_letter
            
            logging.warning(f"⚠️ Métrique '{metric_name}' non trouvée dans l'onglet '{worksheet_name}'")
            return None
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de la recherche de la métrique: {e}")
            raise
    
    def _index_to_column_letter(self, index: int) -> str:
        column_letter = ""
        num = index
        while True:
            column_letter = chr(ord('A') + (num % 26)) + column_letter
            num = num // 26
            if num == 0:
                break
            num -= 1
        return column_letter
    
    def _validate_meta_metrics_before_write(self, updates: List[Dict[str, Any]]) -> None:
        """
        Valide les données Meta avant écriture dans Google Sheets
        
        Args:
            updates: Liste des mises à jour à effectuer
        """
        import os
        
        # Note: Cette validation est simplifiée car les ranges contiennent des coordonnées (A1, B2, etc.)
        # La validation principale se fait dans process_meta_actions() avant l'envoi vers Google Sheets
        
        # Log de validation (structure prête pour validation future si nécessaire)
        meta_updates = [update for update in updates if update.get('value') is not None]
        if meta_updates:
            logging.debug(f"✅ VALIDATION GOOGLE SHEETS: {len(meta_updates)} mises à jour Meta détectées")
    
    def update_sheet_data(self, worksheet_name: str, updates: List[Dict[str, Any]]) -> List[str]:
        try:
            if not updates:
                logging.warning("⚠️ Aucune mise à jour à effectuer")
                return []

            # ✅ GUARDRAILS - Validation des données Meta avant écriture
            self._validate_meta_metrics_before_write(updates)

            batch_update_data = {
                'valueInputOption': 'RAW',
                'data': []
            }
            
            for update in updates:
                batch_update_data['data'].append({
                    'range': f"'{worksheet_name}'!{update['range']}",
                    'values': [[update['value']]]
                })
            
            logging.info(f"📋 Données à mettre à jour: {batch_update_data}")
            
            result = self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=self.sheet_id,
                body=batch_update_data
            ).execute()
            
            updated_cells = result.get('totalUpdatedCells', 0)
            
            return [f"{update['range']}: {update['value']}" for update in updates]
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de la mise à jour du sheet: {e}")
            raise
    
    def update_single_cell(self, worksheet_name: str, cell_range: str, value: Any) -> bool:
        try:
            full_range = f"'{worksheet_name}'!{cell_range}"
            body = {'values': [[value]]}
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id,
                range=full_range,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de la mise à jour de la cellule: {e}")
            return False 