"""
Service d'authentification Meta Ads
"""

import logging
import requests
from typing import List, Dict, Any

from backend.config.settings import Config

class MetaAdsAuthService:
    """Service pour gérer l'authentification Meta Ads"""
    
    def __init__(self):
        self.access_token = Config.API.META_ACCESS_TOKEN
        self.business_id = Config.API.META_BUSINESS_ID
        self.api_version = "v19.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
    
    def get_owned_ad_accounts(self) -> List[Dict[str, Any]]:
        """Récupère les comptes publicitaires possédés par le Business Manager"""
        try:
            url = f"{self.base_url}/{self.business_id}/owned_ad_accounts"
            params = {
                "access_token": self.access_token,
                "fields": "account_id,name,account_status",
                "limit": 100
            }
            
            all_accounts = []
            
            while True:
                response = requests.get(url, params=params)
                if response.status_code != 200:
                    logging.error(f"❌ Erreur récupération comptes possédés BM: {response.status_code} - {response.text}")
                    break
                
                data = response.json()
                accounts = data.get("data", [])
                all_accounts.extend(accounts)
                
                # Vérifier s'il y a une page suivante
                paging = data.get("paging", {})
                next_url = paging.get("next")
                if not next_url:
                    break
                
                # Préparer la requête suivante
                url = next_url
                params = {}  # Les paramètres sont déjà dans l'URL next
            
            logging.info(f"📊 {len(all_accounts)} comptes possédés par le BM récupérés")
            return all_accounts
            
        except Exception as e:
            logging.error(f"❌ Exception lors de la récupération des comptes possédés: {e}")
            return []
    
    def get_business_managers(self) -> List[Dict[str, Any]]:
        """Retourne le Business Manager configuré"""
        try:
            url = f"{self.base_url}/{self.business_id}"
            params = {
                "access_token": self.access_token,
                "fields": "id,name"
            }
            
            response = requests.get(url, params=params)
            if response.status_code != 200:
                logging.error(f"❌ Erreur accès Business Manager {self.business_id}: {response.status_code} - {response.text}")
                return []
            
            business_data = response.json()
            businesses = [{
                "id": business_data.get("id", self.business_id),
                "name": business_data.get("name", f"Business Manager {self.business_id}")
            }]
            
            logging.info(f"🏢 Business Manager configuré: {businesses[0]['name']} ({businesses[0]['id']})")
            return businesses
            
        except Exception as e:
            logging.error(f"❌ Exception lors de l'accès au Business Manager: {e}")
            return []
    
    def get_client_ad_accounts_from_business(self, business_id: str) -> List[Dict[str, Any]]:
        """Récupère les comptes clients d'un Business Manager spécifique"""
        try:
            url = f"{self.base_url}/{business_id}/client_ad_accounts"
            params = {
                "access_token": self.access_token,
                "fields": "account_id,name,account_status",
                "limit": 100
            }
            
            all_accounts = []
            
            while True:
                response = requests.get(url, params=params)
                if response.status_code != 200:
                    logging.warning(f"⚠️ Erreur récupération comptes clients BM {business_id}: {response.status_code}")
                    break
                
                data = response.json()
                accounts = data.get("data", [])
                all_accounts.extend(accounts)
                
                # Vérifier s'il y a une page suivante
                paging = data.get("paging", {})
                next_url = paging.get("next")
                if not next_url:
                    break
                
                # Préparer la requête suivante
                url = next_url
                params = {}
            
            logging.info(f"📋 {len(all_accounts)} comptes clients trouvés pour BM {business_id}")
            return all_accounts
            
        except Exception as e:
            logging.error(f"❌ Exception lors de la récupération des comptes clients du BM {business_id}: {e}")
            return []
    
    def get_owned_ad_accounts_from_business(self, business_id: str) -> List[Dict[str, Any]]:
        """Récupère les comptes possédés directement par un Business Manager"""
        try:
            url = f"{self.base_url}/{business_id}/owned_ad_accounts"
            params = {
                "access_token": self.access_token,
                "fields": "account_id,name,account_status"
            }
            
            response = requests.get(url, params=params)
            if response.status_code != 200:
                logging.warning(f"⚠️ Erreur récupération comptes possédés BM {business_id}: {response.status_code}")
                return []
            
            accounts = response.json().get("data", [])
            logging.info(f"🏢 {len(accounts)} comptes possédés trouvés pour BM {business_id}")
            return accounts
            
        except Exception as e:
            logging.error(f"❌ Exception lors de la récupération des comptes possédés du BM {business_id}: {e}")
            return []
    
    def get_all_accessible_ad_accounts(self) -> List[Dict[str, Any]]:
        """
        Récupère TOUS les comptes Meta Ads accessibles :
        - Comptes propres (propriétaire direct)
        - Comptes clients via Business Managers (délégation)
        - Comptes possédés par les Business Managers
        
        Returns:
            Liste des comptes avec account_id, name, account_status, source
        """
        all_accounts = []
        seen_account_ids = set()
        
        # 1. Récupérer les comptes propres
        logging.info("🔄 Récupération des comptes propres...")
        owned_accounts = self.get_owned_ad_accounts()
        
        for account in owned_accounts:
            account_id = account.get("account_id") or account.get("id", "")
            if account_id and account_id not in seen_account_ids:
                seen_account_ids.add(account_id)
                all_accounts.append({
                    "account_id": account_id.replace("act_", ""),  # Nettoyer le préfixe
                    "name": account.get("name", ""),
                    "account_status": account.get("account_status", 1),
                    "source": "owned_direct"
                })
        
        # 2. Récupérer les Business Managers
        logging.info("🔄 Récupération des Business Managers...")
        business_managers = self.get_business_managers()
        
        # 3. Pour chaque BM, récupérer les comptes clients ET possédés
        for business in business_managers:
            business_id = business.get("id")
            business_name = business.get("name", "")
            
            if business_id:
                logging.info(f"🔄 Analyse complète du BM '{business_name}' ({business_id})...")
                
                # 3a. Récupérer les comptes clients
                client_accounts = self.get_client_ad_accounts_from_business(business_id)
                for account in client_accounts:
                    account_id = account.get("account_id") or account.get("id", "")
                    if account_id and account_id not in seen_account_ids:
                        seen_account_ids.add(account_id)
                        all_accounts.append({
                            "account_id": account_id.replace("act_", ""),
                            "name": account.get("name", ""),
                            "account_status": account.get("account_status", 1),
                            "source": f"client_of_{business_id}"
                        })
                
                # 3b. Récupérer les comptes possédés par le BM
                owned_by_business = self.get_owned_ad_accounts_from_business(business_id)
                for account in owned_by_business:
                    account_id = account.get("account_id") or account.get("id", "")
                    if account_id and account_id not in seen_account_ids:
                        seen_account_ids.add(account_id)
                        all_accounts.append({
                            "account_id": account_id.replace("act_", ""),
                            "name": account.get("name", ""),
                            "account_status": account.get("account_status", 1),
                            "source": f"owned_by_{business_id}"
                        })
        
        logging.info(f"✅ TOTAL: {len(all_accounts)} comptes Meta Ads accessibles")
        
        # Log de la répartition pour debug
        source_counts = {}
        for account in all_accounts:
            source_type = account["source"].split("_")[0] if "_" in account["source"] else account["source"]
            source_counts[source_type] = source_counts.get(source_type, 0) + 1
        
        for source, count in source_counts.items():
            logging.info(f"   - {source}: {count} comptes")
        
        return all_accounts 