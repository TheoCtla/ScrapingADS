"""
Service Google Drive pour l'upload de fichiers CSV
"""

import logging
from typing import Optional, Dict, Any
from io import BytesIO
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.service_account import Credentials

from backend.config.settings import Config


class GoogleDriveService:
    """Service pour gérer l'upload de fichiers vers Google Drive"""
    
    def __init__(self):
        self.service = None
        self.folder_id = Config.API.GOOGLE_DRIVE_FOLDER_ID
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialise le service Google Drive avec les credentials utilisateur (OAuth2)"""
        try:
            from backend.common.auth_utils import get_user_credentials
            
            # Utiliser les mêmes credentials que Google Sheets avec le scope Drive
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive.file'
            ]
            
            credentials = get_user_credentials(scopes)
            
            self.service = build('drive', 'v3', credentials=credentials)
            logging.info("✅ Service Google Drive initialisé avec succès (OAuth2)")
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de l'initialisation du service Google Drive: {e}")
            raise
    
    def find_or_create_client_folder(self, client_name: str, parent_folder_id: str) -> str:
        """
        Trouve ou crée un dossier pour le client dans le dossier parent
        
        Args:
            client_name: Nom du client
            parent_folder_id: ID du dossier parent
            
        Returns:
            ID du dossier client
        """
        try:
            # Rechercher si le dossier existe déjà
            query = f"name='{client_name}' and '{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                supportsAllDrives=True,
                includeItemsFromAllDrives=True
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                # Le dossier existe déjà
                folder_id = folders[0]['id']
                logging.info(f"📁 Dossier client '{client_name}' trouvé: {folder_id}")
                return folder_id
            else:
                # Créer le dossier
                file_metadata = {
                    'name': client_name,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [parent_folder_id]
                }
                
                folder = self.service.files().create(
                    body=file_metadata,
                    fields='id',
                    supportsAllDrives=True
                ).execute()
                
                folder_id = folder.get('id')
                logging.info(f"✅ Dossier client '{client_name}' créé: {folder_id}")
                return folder_id
                
        except Exception as e:
            logging.error(f"❌ Erreur lors de la recherche/création du dossier client: {e}")
            raise
    
    def find_or_create_folder(self, folder_name: str, parent_folder_id: str) -> str:
        """
        Trouve ou crée un dossier dans le dossier parent
        
        Args:
            folder_name: Nom du dossier
            parent_folder_id: ID du dossier parent
            
        Returns:
            ID du dossier
        """
        # Réutiliser la logique existante car elle est identique
        return self.find_or_create_client_folder(folder_name, parent_folder_id)

    def upload_csv_to_drive(self, csv_content: str, filename: str, folder_id: str) -> Dict[str, Any]:
        """
        Upload un fichier CSV vers Google Drive
        
        Args:
            csv_content: Contenu du CSV (string)
            filename: Nom du fichier (ex: Google_Campagne_Test_2026-01-27.csv)
            folder_id: ID du dossier de destination
            
        Returns:
            Dictionnaire avec les informations du fichier uploadé
        """
        try:
            # Convertir le contenu CSV en bytes
            csv_bytes = csv_content.encode('utf-8')
            fh = BytesIO(csv_bytes)
            
            # Métadonnées du fichier
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            
            # Upload du fichier
            media = MediaIoBaseUpload(
                fh,
                mimetype='text/csv',
                resumable=False
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink',
                supportsAllDrives=True
            ).execute()
            
            file_info = {
                'id': file.get('id'),
                'name': file.get('name'),
                'link': file.get('webViewLink')
            }
            
            logging.info(f"✅ Fichier '{filename}' uploadé avec succès: {file_info['id']}")
            return file_info
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de l'upload du fichier '{filename}': {e}")
            raise
    
    
    def create_campaign_folder(self, campaign_name: str, client_folder_id: str) -> str:
        """
        Crée un sous-dossier pour une campagne dans le dossier client
        
        Args:
            campaign_name: Nom de la campagne
            client_folder_id: ID du dossier client
            
        Returns:
            ID du dossier campagne
        """
        try:
            # Rechercher si le dossier existe déjà
            query = f"name='{campaign_name}' and '{client_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                supportsAllDrives=True,
                includeItemsFromAllDrives=True
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                # Le dossier existe déjà
                folder_id = folders[0]['id']
                logging.info(f"📁 Dossier campagne '{campaign_name}' trouvé: {folder_id}")
                return folder_id
            else:
                # Créer le dossier
                file_metadata = {
                    'name': campaign_name,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [client_folder_id]
                }
                
                folder = self.service.files().create(
                    body=file_metadata,
                    fields='id',
                    supportsAllDrives=True
                ).execute()
                
                folder_id = folder.get('id')
                logging.info(f"✅ Dossier campagne '{campaign_name}' créé: {folder_id}")
                return folder_id
                
        except Exception as e:
            logging.error(f"❌ Erreur lors de la création du dossier campagne: {e}")
            raise
    
    def upload_media_file(self, file_bytes: bytes, filename: str, folder_id: str, mime_type: str) -> Dict[str, Any]:
        """
        Upload un fichier média (image, vidéo) vers Google Drive
        
        Args:
            file_bytes: Contenu du fichier en bytes
            filename: Nom du fichier
            folder_id: ID du dossier de destination
            mime_type: Type MIME du fichier (ex: 'image/jpeg', 'video/mp4')
            
        Returns:
            Dictionnaire avec les informations du fichier uploadé
        """
        try:
            fh = BytesIO(file_bytes)
            
            # Métadonnées du fichier
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            
            # Upload du fichier avec resumable upload pour les gros fichiers
            media = MediaIoBaseUpload(
                fh,
                mimetype=mime_type,
                resumable=False
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink',
                supportsAllDrives=True
            ).execute()
            
            file_info = {
                'id': file.get('id'),
                'name': file.get('name'),
                'link': file.get('webViewLink')
            }
            
            file_size_mb = len(file_bytes) / (1024 * 1024)
            logging.info(f"✅ Fichier média '{filename}' uploadé ({file_size_mb:.2f} MB): {file_info['id']}")
            return file_info
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de l'upload du fichier média '{filename}': {e}")
            raise
    
    def delete_file(self, file_id: str) -> bool:
        """
        Supprime un fichier de Google Drive (utile pour les tests)
        
        Args:
            file_id: ID du fichier à supprimer
            
        Returns:
            True si succès, False sinon
        """
        try:
            self.service.files().delete(fileId=file_id, supportsAllDrives=True).execute()
            logging.info(f"🗑️ Fichier {file_id} supprimé avec succès")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de la suppression du fichier {file_id}: {e}")
            return False

