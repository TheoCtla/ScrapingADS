"""
Authentification Google Analytics Data API (GA4) via OAuth2.
Réutilise le token utilisateur partagé avec Sheets/Drive.
"""

import logging
from typing import Optional

from google.analytics.data_v1beta import BetaAnalyticsDataClient

from backend.common.auth_utils import get_user_credentials
from backend.config.settings import Config


class GoogleAnalyticsAuthService:
    """Initialise et expose un client GA4 Data API authentifié."""

    def __init__(self):
        self._client: Optional[BetaAnalyticsDataClient] = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        try:
            credentials = get_user_credentials(Config.API.GOOGLE_SCOPES)
            self._client = BetaAnalyticsDataClient(credentials=credentials)
            logging.info("✅ Service Google Analytics initialisé avec succès (OAuth2)")
        except Exception as e:
            logging.error(f"❌ Erreur lors de l'initialisation du service Google Analytics: {e}")
            raise

    def get_client(self) -> BetaAnalyticsDataClient:
        return self._client
