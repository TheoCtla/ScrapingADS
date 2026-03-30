"""
Service dédié à l'upload des rapports PPTX sur Google Drive.
Gère la création du dossier mensuel et l'upload des fichiers.
"""

import logging
from io import BytesIO
from typing import Optional

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from backend.config.settings import Config

REPORTS_PARENT_FOLDER_ID = "1l627RHHdt1Ob-9qqCgfJfpGlJOCxtW27"

PPTX_MIME_TYPE = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"


class DriveReportService:
    """Upload des rapports PPTX vers Google Drive."""

    def __init__(self):
        self.service = None
        self._initialize_service()

    def _initialize_service(self) -> None:
        try:
            from backend.common.auth_utils import get_user_credentials

            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]
            credentials = get_user_credentials(scopes)
            self.service = build("drive", "v3", credentials=credentials)
            logging.info("Service DriveReport initialisé")
        except Exception as e:
            logging.error(f"Erreur initialisation DriveReportService: {e}")
            raise

    def find_or_create_month_folder(self, folder_name: str) -> str:
        """
        Trouve ou crée le sous-dossier mensuel (ex: '2026-02') dans _RAPPORTS.

        Args:
            folder_name: Nom du dossier au format 'YYYY-MM'.

        Returns:
            ID du dossier Google Drive.
        """
        query = (
            f"name='{folder_name}' "
            f"and '{REPORTS_PARENT_FOLDER_ID}' in parents "
            f"and mimeType='{FOLDER_MIME_TYPE}' "
            f"and trashed=false"
        )
        results = self.service.files().list(
            q=query, spaces="drive", fields="files(id, name)"
        ).execute()

        files = results.get("files", [])
        if files:
            folder_id = files[0]["id"]
            logging.info(f"Dossier '{folder_name}' existant: {folder_id}")
            return folder_id

        file_metadata = {
            "name": folder_name,
            "mimeType": FOLDER_MIME_TYPE,
            "parents": [REPORTS_PARENT_FOLDER_ID],
        }
        folder = self.service.files().create(
            body=file_metadata, fields="id"
        ).execute()

        folder_id = folder["id"]
        logging.info(f"Dossier '{folder_name}' créé: {folder_id}")
        return folder_id

    def upload_pptx(
        self,
        file_bytes: bytes,
        filename: str,
        folder_id: str,
    ) -> str:
        """
        Upload un fichier PPTX dans un dossier Drive.

        Args:
            file_bytes: Contenu du PPTX en bytes.
            filename: Nom du fichier (ex: 'Rapport_FLBordeaux_Février2026.pptx').
            folder_id: ID du dossier Drive de destination.

        Returns:
            ID du fichier uploadé.
        """
        file_metadata = {
            "name": filename,
            "parents": [folder_id],
        }
        media = MediaIoBaseUpload(
            BytesIO(file_bytes),
            mimetype=PPTX_MIME_TYPE,
            resumable=True,
        )
        uploaded = self.service.files().create(
            body=file_metadata, media_body=media, fields="id, webViewLink"
        ).execute()

        file_id = uploaded["id"]
        link = uploaded.get("webViewLink", "")
        logging.info(f"Rapport '{filename}' uploadé: {link}")
        return file_id

    def get_file_link(self, file_id: str) -> Optional[str]:
        """Récupère le lien web d'un fichier Drive."""
        try:
            file_info = self.service.files().get(
                fileId=file_id, fields="webViewLink"
            ).execute()
            return file_info.get("webViewLink")
        except Exception as e:
            logging.warning(f"Impossible de récupérer le lien pour {file_id}: {e}")
            return None
