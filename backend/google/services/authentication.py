"""
Service d'authentification Google Ads
"""

import logging
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

from backend.config.settings import Config

class GoogleAdsAuthService:
    """Service pour gérer l'authentification Google Ads"""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialise le client Google Ads"""
        try:
            self.client = GoogleAdsClient.load_from_storage(str(Config.API.GOOGLE_ADS_YAML_PATH))
            logging.info("✅ Client Google Ads initialisé avec succès")
        except Exception as e:
            logging.error(f"❌ Erreur lors de l'initialisation du client Google Ads: {e}")
            raise
    
    def get_client(self) -> GoogleAdsClient:
        """Retourne le client Google Ads authentifié"""
        if self.client is None:
            self._initialize_client()
        return self.client
    
    def fetch_report_data(self, customer_id: str, query: str):
        """
        Exécute une requête GAQL et retourne les résultats
        
        Args:
            customer_id: ID du client Google Ads
            query: Requête GAQL à exécuter
            
        Returns:
            Résultats de la requête
        """
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            response = ga_service.search_stream(customer_id=customer_id, query=query)
            return response
        except GoogleAdsException as ex:
            for error in ex.failure.errors:
                logging.error(f"❌ GoogleAdsException during fetch_report_data: {error.message}")
            raise
        except Exception as e:
            logging.error(f"❌ Exception during fetch_report_data: {str(e)}")
            raise
    
    def list_customers(self) -> list:
        """
        Récupère la liste des clients Google Ads accessibles
        
        Returns:
            Liste des clients avec customer_id, name et manager
        """
        try:
            ga_service = self.client.get_service("GoogleAdsService")

            query = """
            SELECT
                customer_client.client_customer,
                customer_client.level,
                customer_client.descriptive_name,
                customer_client.manager
            FROM customer_client
            WHERE customer_client.level <= 1
            """

            response = ga_service.search(customer_id=self.client.login_customer_id, query=query)

            customers_info = []
            for row in response:
                customers_info.append({
                    "customer_id": row.customer_client.client_customer.replace("customers/", ""),
                    "name": row.customer_client.descriptive_name,
                    "manager": row.customer_client.manager
                })

            logging.info(f"📋 {len(customers_info)} clients Google Ads récupérés")
            return customers_info

        except GoogleAdsException as ex:
            for error in ex.failure.errors:
                logging.error(f"❌ GoogleAds API error in list_customers: {error.message}")
            raise
        except Exception as e:
            logging.error(f"❌ Unexpected error in list_customers: {str(e)}")
            raise 