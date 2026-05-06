"""
Service de rapports Meta Ads - Gestion des insights et métriques
"""

import logging
import requests
import time
from typing import Dict, Any, Optional

from backend.config.settings import Config

class MetaAdsReportsService:
    """Service pour gérer les rapports et métriques Meta Ads"""
    
    def __init__(self):
        self.access_token = Config.API.META_ACCESS_TOKEN
        self.api_version = "v19.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
    
    def _handle_meta_rate_limit(self, response, max_retries=3):
        """Gère les limites de taux Meta avec retry intelligent"""
        if response.status_code == 403:
            try:
                error_data = response.json()
                if error_data.get("error", {}).get("code") == 4:  # Rate limit
                    error_subcode = error_data.get("error", {}).get("error_subcode")
                    
                    if error_subcode == 1504022:  # Application request limit
                        logging.warning("⚠️ Limite de taux Meta atteinte - Application request limit")
                        return True, 300  # Attendre 5 minutes
                    elif error_subcode == 1504023:  # User request limit  
                        logging.warning("⚠️ Limite de taux Meta atteinte - User request limit")
                        return True, 60   # Attendre 1 minute
                    else:
                        logging.warning("⚠️ Limite de taux Meta atteinte - Autre erreur")
                        return True, 120  # Attendre 2 minutes
            except:
                logging.warning("⚠️ Limite de taux Meta atteinte - Format d'erreur inconnu")
                return True, 180  # Attendre 3 minutes
        return False, 0
    
    def _make_meta_request_with_retry(self, url, params=None, max_retries=3):
        """Effectue une requête Meta avec gestion des quotas"""
        for attempt in range(max_retries + 1):
            try:
                # Timeout de 30 secondes pour éviter les blocages
                response = requests.get(url, params=params, timeout=30)
                
                # Vérifier les limites de taux
                is_rate_limited, wait_time = self._handle_meta_rate_limit(response)
                
                if is_rate_limited:
                    if attempt < max_retries:
                        logging.info(f"⏳ Attente de {wait_time}s avant retry {attempt + 1}/{max_retries}")
                        time.sleep(wait_time)
                        continue
                    else:
                        logging.error(f"❌ Limite de taux Meta dépassée après {max_retries} tentatives")
                        return None
                
                if response.status_code == 200:
                    return response
                else:
                    # Vérifier si c'est une erreur de permissions (code 200)
                    error_message = ""
                    try:
                        error_data = response.json().get("error", {})
                        error_code = error_data.get("code")
                        error_msg = error_data.get("message", "")
                        
                        if error_code == 200 and ("ads_management" in error_msg or "ads_read" in error_msg):
                            error_message = (
                                f"❌ PERMISSIONS MANQUANTES - Le propriétaire du compte publicitaire "
                                f"n'a pas autorisé l'application Meta à accéder au compte.\n"
                                f"   Solution: Le propriétaire du compte doit autoriser l'application "
                                f"(App ID: 3610369945767313) via Meta Business Manager.\n"
                                f"   Voir: backend/scripts/GUIDE_AUTORISATION_META.md"
                            )
                            logging.error(error_message)
                        else:
                            logging.error(f"❌ Erreur API Meta: {response.status_code} - {response.text}")
                    except:
                        logging.error(f"❌ Erreur API Meta: {response.status_code} - {response.text}")
                    return None
                    
            except Exception as e:
                logging.error(f"❌ Exception lors de la requête Meta: {e}")
                if attempt < max_retries:
                    time.sleep(30)  # Attendre 30s avant retry
                    continue
                return None
        
        return None
    
    def get_meta_insights(self, ad_account_id: str, start_date: str, end_date: str, only_active: bool = False, name_contains_ci: str = None) -> Optional[Dict[str, Any]]:
        """
        Récupère les insights Meta Ads par campagne et les agrège manuellement
        
        Args:
            ad_account_id: ID du compte publicitaire Meta
            start_date: Date de début (YYYY-MM-DD)
            end_date: Date de fin (YYYY-MM-DD)
            
        Returns:
            Dictionnaire des données agrégées ou None si erreur
        """
        try:
            url = f"{self.base_url}/act_{ad_account_id}/insights"
            
            params = {
                "access_token": self.access_token,
                "fields": "impressions,clicks,ctr,cpc,spend,actions,campaign_name,conversions,conversion_values",
                "level": "campaign",  # Récupérer au niveau campagne pour additionner nous-mêmes
                "time_range": f'{{"since":"{start_date}","until":"{end_date}"}}',
                "limit": 100  # Augmenter la limite pour récupérer toutes les campagnes
            }
            if only_active:
                params["effective_status"] = ["ACTIVE"]
            
            # Appel API Meta pour {ad_account_id}: {start_date} à {end_date} (niveau campagne)
            
            # ✅ NOUVELLE APPROCHE - Récupération directe au niveau compte
            response = self._make_meta_request_with_retry(url, params)
            
            if response is None:
                logging.error(f"❌ Échec de la requête Meta après retry")
                return None
            
            response_data = response.json()
            data = response_data.get("data", [])

            # Filtrer par nom de campagne si demandé (insensible à la casse)
            if name_contains_ci:
                needle = name_contains_ci.lower()
                before_count = len(data)
                data = [c for c in data if needle in str(c.get('campaign_name', '')).lower()]
                logging.info(f"🔎 Filtre nom campagne contient '{needle}': {before_count} → {len(data)}")
            
            if not data:
                logging.warning(f"⚠️ Aucune donnée trouvée pour {ad_account_id}")
                return None
            
            # ✅ NOUVELLE APPROCHE - Traitement par campagne et agrégation manuelle
            logging.info(f"🔍 DONNÉES META CAMPAGNES TROUVÉES: {len(data)} campagnes")
            
            # Variables d'agrégation
            total_impressions = 0
            total_clicks = 0
            total_spend = 0
            total_contact_conversions = 0
            total_search_conversions = 0
            campaign_names = []
            
            # Traiter chaque campagne
            for i, campaign_data in enumerate(data):
                campaign_name = campaign_data.get('campaign_name', f'Campagne {i+1}')
                campaign_names.append(campaign_name)
                
                logging.info(f"📋 TRAITEMENT CAMPAGNE {i+1}/{len(data)}: '{campaign_name}'")
                
                # Agrégation des métriques de base
                campaign_impressions = int(campaign_data.get('impressions', 0))
                campaign_clicks = int(campaign_data.get('clicks', 0))
                campaign_spend = float(campaign_data.get('spend', 0))
                
                total_impressions += campaign_impressions
                total_clicks += campaign_clicks
                total_spend += campaign_spend
                
                logging.info(f"  📈 Métriques de base: {campaign_impressions} impressions, {campaign_clicks} clics, {campaign_spend}€")
                
                # Traitement des conversions par campagne
                campaign_contacts, campaign_searches = self._extract_campaign_metrics(campaign_data, campaign_name)
                total_contact_conversions += campaign_contacts
                total_search_conversions += campaign_searches
                
                logging.info(f"  📊 RÉSULTAT FINAL CAMPAGNE '{campaign_name}': {campaign_contacts} contacts, {campaign_searches} recherches")
                logging.info(f"  📈 TOTAUX CUMULÉS: {total_contact_conversions} contacts, {total_search_conversions} recherches")
            
            # Calcul des métriques agrégées
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
            
            # Créer les données agrégées
            aggregated_data = {
                'impressions': total_impressions,
                'clicks': total_clicks,
                'ctr': ctr,
                'cpc': cpc,
                'spend': total_spend,
                'conversions': [
                    {'action_type': 'contact_total', 'value': str(total_contact_conversions)},
                    {'action_type': 'find_location_total', 'value': str(total_search_conversions)}
                ],
                'campaign_names': campaign_names,
                'campaign_count': len(data)
            }
            
            logging.info(f"📊 DONNÉES META AGRÉGÉES:")
            logging.info(f"  🎯 Total Contacts: {total_contact_conversions}")
            logging.info(f"  📍 Total Recherches: {total_search_conversions}")
            logging.info(f"  📈 Total Impressions: {total_impressions}")
            logging.info(f"  🖱️ Total Clics: {total_clicks}")
            logging.info(f"  💰 Total Spend: {total_spend}")
            logging.info(f"  📋 Campagnes: {len(data)}")
            
            return aggregated_data
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de la récupération des insights Meta: {e}")
            return None
    
    def _extract_campaign_metrics(self, campaign_data: dict, campaign_name: str) -> tuple:
        """
        Extrait les métriques de contacts et recherches de lieux pour une campagne
        
        Args:
            campaign_data: Données de la campagne
            campaign_name: Nom de la campagne
            
        Returns:
            Tuple (contacts, recherches_lieux)
        """
        contacts = 0
        searches = 0
        
        logging.info(f"🔍 ANALYSE CAMPAGNE: '{campaign_name}'")
        
        # Extraire les contacts depuis les conversions de la campagne
        if 'conversions' in campaign_data and campaign_data['conversions']:
            conversions_data = campaign_data['conversions']
            logging.info(f"  📊 Conversions trouvées: {len(conversions_data)} actions")
            
            if isinstance(conversions_data, list):
                # Actions de contact
                contact_action_types = ['contact_total', 'contact_website', 'onsite_web_lead', 'lead', 'offsite_conversion.fb_pixel_lead']
                logging.info(f"  🎯 RECHERCHE CONTACTS dans {len(conversions_data)} actions...")
                
                for action in conversions_data:
                    if isinstance(action, dict) and action.get('action_type') in contact_action_types:
                        value = int(action.get('value', 0))
                        action_type = action.get('action_type', '')
                        logging.info(f"    ✅ Action contact trouvée: '{action_type}' = {value}")
                        if value > contacts:
                            contacts = value
                            logging.info(f"    🎯 Nouveau max contacts: {contacts}")
                
                # Actions de recherche de lieux
                search_action_types = ['find_location_total', 'find_location_website', 'offsite_conversion.fb_pixel_custom', 'onsite_web_location_search', 'location_search']
                logging.info(f"  📍 RECHERCHE LIEUX dans {len(conversions_data)} actions...")
                
                for action in conversions_data:
                    if isinstance(action, dict) and action.get('action_type') in search_action_types:
                        value = int(action.get('value', 0))
                        action_type = action.get('action_type', '')
                        logging.info(f"    ✅ Action recherche trouvée: '{action_type}' = {value}")
                        if value > searches:
                            searches = value
                            logging.info(f"    📍 Nouveau max recherches: {searches}")
        
        # Fallback vers les actions si pas de conversions
        elif 'actions' in campaign_data and campaign_data['actions']:
            actions = campaign_data.get('actions', [])
            logging.info(f"  📊 Actions trouvées: {len(actions)} actions (fallback)")
            
            # Actions de contact
            contact_action_types = ['contact_total', 'contact_website', 'onsite_web_lead', 'lead', 'offsite_conversion.fb_pixel_lead']
            logging.info(f"  🎯 RECHERCHE CONTACTS dans {len(actions)} actions (fallback)...")
            
            for action in actions:
                if isinstance(action, dict) and action.get('action_type') in contact_action_types:
                    value = int(action.get('value', 0))
                    action_type = action.get('action_type', '')
                    logging.info(f"    ✅ Action contact trouvée: '{action_type}' = {value}")
                    if value > contacts:
                        contacts = value
                        logging.info(f"    🎯 Nouveau max contacts: {contacts}")
            
            # Actions de recherche de lieux
            search_action_types = ['find_location_total', 'find_location_website', 'offsite_conversion.fb_pixel_custom', 'onsite_web_location_search', 'location_search']
            logging.info(f"  📍 RECHERCHE LIEUX dans {len(actions)} actions (fallback)...")
            
            for action in actions:
                if isinstance(action, dict) and action.get('action_type') in search_action_types:
                    value = int(action.get('value', 0))
                    action_type = action.get('action_type', '')
                    logging.info(f"    ✅ Action recherche trouvée: '{action_type}' = {value}")
                    if value > searches:
                        searches = value
                        logging.info(f"    📍 Nouveau max recherches: {searches}")
        else:
            logging.info(f"  ⚠️ Aucune conversion ni action trouvée pour '{campaign_name}'")
        
        logging.info(f"  📊 RÉSULTAT CAMPAGNE '{campaign_name}': {contacts} contacts, {searches} recherches")
        return contacts, searches
    
    
    def get_meta_campaigns_cpl_average(self, ad_account_id: str, start_date: str, end_date: str) -> float:
        """
        Récupère le CPL moyen des campagnes Meta Ads en utilisant cost_per_result directement
        
        Args:
            ad_account_id: ID du compte publicitaire
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            CPL moyen ou 0 si aucun résultat
        """
        try:
            url = f"{self.base_url}/act_{ad_account_id}/insights"
            
            params = {
                "access_token": self.access_token,
                "fields": "campaign_name,cost_per_result,spend,impressions,actions",
                "level": "campaign",
                "time_range": f'{{"since":"{start_date}","until":"{end_date}"}}'
            }
            
            # DEBUG: Appel API Meta campagnes pour CPL moyen {ad_account_id}: {start_date} à {end_date}
            
            response = self._make_meta_request_with_retry(url, params)
            if response is None:
                logging.error(f"❌ Échec de la requête Meta campagnes après retry")
                return 0
            
            response_data = response.json()
            data = response_data.get("data", [])
            
            # DEBUG: Données campagnes Meta reçues: {len(data)} campagnes
            
            valid_cpls = []
            
            for i, campaign in enumerate(data):
                campaign_name = campaign.get('campaign_name', 'Unknown')
                cost_per_result = campaign.get('cost_per_result')
                spend = float(campaign.get('spend', 0))
                impressions = int(campaign.get('impressions', 0))
                actions = campaign.get('actions', [])
                
                # DEBUG Campagne {i+1}: '{campaign_name}'
                # Debug: Spend: {spend}€
                # Debug: Impressions: {impressions}
                # Debug: Actions: {actions}
                # Debug: Cost_per_result brut: {cost_per_result}
                
                # Condition pour campagne active : spend > 0 ET impressions > 0
                is_active = spend > 0 and impressions > 0
                # Debug: Campagne active ? {is_active}
                
                if not is_active:
                    logging.info(f"   ❌ Campagne '{campaign_name}' ignorée (inactive)")
                    continue
                
                # Analyser cost_per_result
                if cost_per_result:
                    # Debug: Cost_per_result existe, longueur: {len(cost_per_result) if isinstance(cost_per_result, list) else 'Not a list'}
                    
                    if isinstance(cost_per_result, list) and len(cost_per_result) > 0:
                        for j, cpr_item in enumerate(cost_per_result):
                            logging.info(f"     [Résultat {j}]: {cpr_item}")
                            
                            # Structure correcte : {'indicator': '...', 'values': [{'value': '19.48', 'attribution_windows': [...]}]}
                            indicator = cpr_item.get('indicator', 'unknown')
                            values = cpr_item.get('values', [])
                            
                            if values and len(values) > 0:
                                cpl_value = float(values[0].get('value', 0))
                                
                                if cpl_value > 0:
                                    valid_cpls.append(cpl_value)
                                    logging.info(f"   ✅ CPL trouvé: {cpl_value:.2f}€ (indicator: {indicator})")
                                else:
                                    logging.info(f"   ⚠️ CPL = 0 (indicator: {indicator})")
                            else:
                                logging.info(f"   ❌ Pas de values dans cost_per_result: {cpr_item}")
                    else:
                        logging.info(f"   ❌ Cost_per_result vide ou pas une liste")
                else:
                    logging.info(f"   ❌ Pas de cost_per_result pour '{campaign_name}'")
            
            # Calculer la moyenne des CPL valides
            logging.info(f"🧮 DEBUG: CPL collectés: {valid_cpls}")
            logging.info(f"🧮 DEBUG: Nombre de CPL valides: {len(valid_cpls)}")
            
            if valid_cpls:
                average_cpl = sum(valid_cpls) / len(valid_cpls)
                logging.info(f"📈 CPL moyen calculé: {average_cpl:.2f}€ sur {len(valid_cpls)} campagnes actives")
                # Détail des CPL: {[round(cpl, 2) for cpl in valid_cpls]}
                # RÉSULTAT FINAL: {round(average_cpl, 2)}€
                return round(average_cpl, 2)
            else:
                logging.warning(f"⚠️ AUCUNE campagne active avec cost_per_result trouvée pour {ad_account_id}")
                return 0
                
        except Exception as e:
            logging.error(f"❌ Erreur lors de la récupération du CPL moyen des campagnes: {e}")
            import traceback
            logging.error(f"❌ Traceback: {traceback.format_exc()}")
            return 0
    
    def process_meta_actions(self, insights_data: dict) -> tuple:
        """
        Traite les données Meta Insights pour extraire les recherches de lieux uniquement
        NOTE: Les contacts sont maintenant récupérés via getContactsResults() avec le champ results
        
        Args:
            insights_data: Données d'insights Meta agrégées
            
        Returns:
            Tuple (contact_conversions, search_conversions)
        """
        # Les contacts sont maintenant récupérés via getContactsResults() avec le champ results
        contact_conversions = 0  # Désactivé - utilise getContactsResults()
        search_conversions = self._extract_location_search_from_meta(insights_data)
        
        logging.info(f"📊 MÉTRIQUES META (ancienne méthode):")
        logging.info(f"  🎯 Contact Meta: {contact_conversions} (désactivé - utilise getContactsResults())")
        logging.info(f"  📍 Recherche de lieux: {search_conversions}")
        
        return contact_conversions, search_conversions
    
    
    def _extract_location_search_from_meta(self, insights_data: dict) -> int:
        """
        Extrait les recherches de lieux depuis les données Meta Insights
        
        Args:
            insights_data: Données d'insights Meta au niveau compte
            
        Returns:
            Nombre de recherches de lieux extraites
        """
        if not insights_data:
            logging.debug("🔍 Aucune donnée Meta fournie pour extraction Recherche de lieux")
            return 0
        
        # ✅ APPROCHE DIRECTE - Utiliser les vraies métriques Meta au niveau compte
        search_conversions = 0
        
        # 1. PRIORITÉ - Utiliser les conversion_values (champ valide de l'API)
        if 'conversion_values' in insights_data and insights_data['conversion_values']:
            conversion_values_data = insights_data['conversion_values']
            # Gérer le cas où conversion_values est une liste d'actions
            if isinstance(conversion_values_data, list):
                # Traiter les actions de conversion_values pour extraire les recherches de lieux
                search_action_types = ['find_location_total', 'find_location_website', 'offsite_conversion.fb_pixel_custom', 'onsite_web_location_search', 'location_search']
                
                for action in conversion_values_data:
                    if isinstance(action, dict) and action.get('action_type') in search_action_types:
                        value = int(action.get('value', 0))
                        search_conversions += value
                        logging.debug(f"📍 RECHERCHE VIA CONVERSION_VALUES ACTION: '{action.get('action_type')}' → {value}")
                
                logging.info(f"📍 RECHERCHE VIA CONVERSION_VALUES (actions): {search_conversions}")
            # Gérer le cas où conversion_values est un dictionnaire simple
            elif isinstance(conversion_values_data, dict):
                # Extraire la valeur du dictionnaire (généralement 'value' ou 'count')
                if 'value' in conversion_values_data:
                    search_conversions = int(conversion_values_data['value'])
                elif 'count' in conversion_values_data:
                    search_conversions = int(conversion_values_data['count'])
                else:
                    # Prendre la première valeur numérique trouvée
                    for key, value in conversion_values_data.items():
                        if isinstance(value, (int, float)) and value > 0:
                            search_conversions = int(value)
                            break
                logging.info(f"📍 RECHERCHE VIA CONVERSION_VALUES (dict): {search_conversions}")
            else:
                search_conversions = int(conversion_values_data)
                logging.info(f"📍 RECHERCHE VIA CONVERSION_VALUES: {search_conversions}")
        
        # 1.5. FALLBACK - Chercher aussi dans les conversions pour les actions de recherche de lieux
        elif 'conversions' in insights_data and insights_data['conversions']:
            conversions_data = insights_data['conversions']
            if isinstance(conversions_data, list):
                # Traiter les actions de conversions pour extraire les recherches de lieux
                # PRIORITÉ: Prendre find_location_total en priorité, sinon find_location_website
                search_action_types = ['find_location_total', 'find_location_website', 'offsite_conversion.fb_pixel_custom', 'onsite_web_location_search', 'location_search']
                
                for action in conversions_data:
                    if isinstance(action, dict) and action.get('action_type') in search_action_types:
                        value = int(action.get('value', 0))
                        # Si on a déjà une valeur et qu'on trouve find_location_total, on la remplace
                        if action.get('action_type') == 'find_location_total' or search_conversions == 0:
                            search_conversions = value
                            logging.debug(f"📍 RECHERCHE VIA CONVERSIONS ACTION: '{action.get('action_type')}' → {value}")
                        elif action.get('action_type') == 'find_location_website' and search_conversions == 0:
                            search_conversions = value
                            logging.debug(f"📍 RECHERCHE VIA CONVERSIONS ACTION: '{action.get('action_type')}' → {value}")
                
                logging.info(f"📍 RECHERCHE VIA CONVERSIONS (actions): {search_conversions}")
        
        # 2. FALLBACK - Calculer depuis les actions de recherche
        elif 'actions' in insights_data and insights_data['actions']:
            actions = insights_data.get('actions', [])
            search_action_types = [
                'offsite_conversion.fb_pixel_custom',
                'onsite_web_location_search',
                'location_search',
                'location_actions'
            ]
            
            for action in actions:
                action_type = action.get('action_type', '')
                value = int(action.get('value', 0))
                
                if action_type in search_action_types:
                    search_conversions += value
                    logging.debug(f"📍 RECHERCHE VIA ACTION: '{action_type}' → {value}")
        
        # 3. FALLBACK - Chercher dans d'autres champs possibles
        else:
            possible_fields = ['location_searches', 'search_conversions', 'place_actions', 'location_actions']
            for field in possible_fields:
                if field in insights_data and insights_data[field]:
                    field_data = insights_data[field]
                    # Gérer le cas où le champ est une liste
                    if isinstance(field_data, list):
                        search_conversions = sum(int(item) for item in field_data if item)
                        logging.info(f"📍 RECHERCHE VIA {field.upper()} (liste): {search_conversions}")
                    # Gérer le cas où le champ est un dictionnaire
                    elif isinstance(field_data, dict):
                        if 'value' in field_data:
                            search_conversions = int(field_data['value'])
                        elif 'count' in field_data:
                            search_conversions = int(field_data['count'])
                        else:
                            # Prendre la première valeur numérique trouvée
                            for key, value in field_data.items():
                                if isinstance(value, (int, float)) and value > 0:
                                    search_conversions = int(value)
                                    break
                        logging.info(f"📍 RECHERCHE VIA {field.upper()} (dict): {search_conversions}")
                    else:
                        search_conversions = int(field_data)
                        logging.info(f"📍 RECHERCHE VIA {field.upper()}: {search_conversions}")
                    break
        
        logging.info(f"📊 Recherches de lieux extraites: {search_conversions}")
        return search_conversions
    
    def get_lyleoo_interest_retarget_data(self, ad_account_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Pour LyleOO uniquement : récupère les "Résultats" (objectif de campagne) par adset
        pour les campagnes 'Interaction Interest' et 'Interaction CM Retarget',
        regroupés par 'facebook' / 'insta' dans le nom de l'adset.

        Le budget retourné est le spend TOTAL de chaque campagne (somme de tous les adsets,
        peu importe leur nom).

        Returns:
            Dict avec 6 clés : interest_facebook, interest_insta, interest_budget,
            retarget_facebook, retarget_insta, retarget_budget.
        """
        result = {
            "interest_facebook": 0,
            "interest_insta": 0,
            "interest_budget": 0.0,
            "retarget_facebook": 0,
            "retarget_insta": 0,
            "retarget_budget": 0.0,
        }

        try:
            url = f"{self.base_url}/act_{ad_account_id}/insights"
            params = {
                "access_token": self.access_token,
                "fields": "campaign_name,adset_name,spend,results,actions",
                "level": "adset",
                "time_range": f'{{"since":"{start_date}","until":"{end_date}"}}',
                "limit": 500,
            }
            logging.info(f"🦄 LyleOO — récupération adsets Interest/Retarget pour {ad_account_id} ({start_date} → {end_date})")
            response = self._make_meta_request_with_retry(url, params)
            if response is None:
                logging.warning("⚠️ LyleOO — pas de réponse Meta pour les adsets")
                return result

            data = response.json().get("data", [])
            logging.info(f"🦄 LyleOO — {len(data)} adsets retournés")

            for adset in data:
                campaign_name = (adset.get("campaign_name") or "").lower()
                adset_name = (adset.get("adset_name") or "").lower()
                try:
                    spend = float(adset.get("spend") or 0)
                except (TypeError, ValueError):
                    spend = 0.0

                # Le vrai nom contient "INTÉRACTION CM (Interest)" / "INTÉRACTION CM (Retarget)"
                # On matche sur "cm (interest)" / "cm (retarget)" pour gérer la casse + accent
                # et exclure les autres campagnes type "Campagne Opticiens (Retarget)"
                is_interest = "cm (interest)" in campaign_name
                is_retarget = "cm (retarget)" in campaign_name
                if not (is_interest or is_retarget):
                    continue

                # Somme des "Résultats" (objectif de campagne) pour cet adset
                total_results = 0
                for r in adset.get("results", []) or []:
                    for v in r.get("values", []) or []:
                        try:
                            total_results += int(float(v.get("value") or 0))
                        except (TypeError, ValueError):
                            pass

                if is_interest:
                    result["interest_budget"] += spend
                    if "facebook" in adset_name:
                        result["interest_facebook"] += total_results
                        logging.info(f"  ✅ Interest Facebook | adset='{adset.get('adset_name')}' | results=+{total_results} | spend=+{spend}€")
                    elif "insta" in adset_name:
                        result["interest_insta"] += total_results
                        logging.info(f"  ✅ Interest Insta | adset='{adset.get('adset_name')}' | results=+{total_results} | spend=+{spend}€")
                    else:
                        logging.info(f"  ⏭️  Interest skip (ni facebook ni insta) | adset='{adset.get('adset_name')}' | spend=+{spend}€")
                elif is_retarget:
                    result["retarget_budget"] += spend
                    if "facebook" in adset_name:
                        result["retarget_facebook"] += total_results
                        logging.info(f"  ✅ Retarget Facebook | adset='{adset.get('adset_name')}' | results=+{total_results} | spend=+{spend}€")
                    elif "insta" in adset_name:
                        result["retarget_insta"] += total_results
                        logging.info(f"  ✅ Retarget Insta | adset='{adset.get('adset_name')}' | results=+{total_results} | spend=+{spend}€")
                    else:
                        logging.info(f"  ⏭️  Retarget skip (ni facebook ni insta) | adset='{adset.get('adset_name')}' | spend=+{spend}€")

            # Arrondir les budgets
            result["interest_budget"] = round(result["interest_budget"], 2)
            result["retarget_budget"] = round(result["retarget_budget"], 2)

            logging.info(f"🦄 LyleOO TOTAUX — {result}")
            return result

        except Exception as e:
            logging.error(f"❌ Erreur get_lyleoo_interest_retarget_data: {e}")
            return result

    def get_action_total_for_account(self, ad_account_id: str, start_date: str, end_date: str, action_type_name: str) -> int:
        """
        Récupère le total d'une action_type spécifique (ex: 'auxerre_engaged_10s')
        sur toutes les campagnes du compte Meta sur la période.

        Le matching est tolérant : Meta peut retourner l'action_type sous plusieurs formes
        - exact: 'auxerre_engaged_10s'
        - préfixé pixel custom: 'offsite_conversion.fb_pixel_custom.auxerre_engaged_10s'
        - autre préfixe: 'offsite_conversion.custom.auxerre_engaged_10s', etc.
        On accepte tout suffixe `.auxerre_engaged_10s` ou égalité directe.

        Args:
            ad_account_id: ID du compte publicitaire Meta
            start_date: Date de début (YYYY-MM-DD)
            end_date: Date de fin (YYYY-MM-DD)
            action_type_name: Nom de l'event Meta (ex: 'auxerre_engaged_10s')

        Returns:
            Total des résultats (entier), 0 si non trouvé ou erreur
        """
        def _matches(at: str) -> bool:
            if not at:
                return False
            return at == action_type_name or at.endswith("." + action_type_name)

        try:
            url = f"{self.base_url}/act_{ad_account_id}/insights"
            params = {
                "access_token": self.access_token,
                "fields": "actions,conversions,campaign_name",
                "level": "campaign",
                "time_range": f'{{"since":"{start_date}","until":"{end_date}"}}',
                "limit": 100,
            }
            logging.info(f"🔍 Récupération action_type '{action_type_name}' Meta pour {ad_account_id} ({start_date} → {end_date})")
            response = self._make_meta_request_with_retry(url, params)
            if response is None:
                logging.warning(f"⚠️ Pas de réponse Meta pour action_type '{action_type_name}'")
                return 0

            data = response.json().get("data", [])
            total = 0
            for campaign in data:
                campaign_name = campaign.get("campaign_name", "?")
                # On regarde d'abord 'conversions', puis 'actions' en fallback
                # (les events custom apparaissent souvent dans 'conversions')
                for field in ("conversions", "actions"):
                    items = campaign.get(field, []) or []
                    if not isinstance(items, list):
                        continue
                    for item in items:
                        if not isinstance(item, dict):
                            continue
                        at = item.get("action_type", "")
                        if _matches(at):
                            try:
                                v = float(item.get("value", 0))
                                total += int(v)
                                logging.info(f"  ✅ Match {field}.{at} sur '{campaign_name}': +{int(v)}")
                            except (TypeError, ValueError):
                                pass

            logging.info(f"📊 Total '{action_type_name}': {total} (sur {len(data)} campagnes)")
            return total
        except Exception as e:
            logging.error(f"❌ Erreur get_action_total_for_account ('{action_type_name}'): {e}")
            return 0

    def getContactsResults(self, ad_account_id: str, since: str, until: str, level: str = 'campaign', only_active: bool = False, name_contains_ci: str = None) -> list:
        """
        Récupère les contacts Meta via l'endpoint /insights avec le champ results
        
        Args:
            ad_account_id: ID du compte publicitaire Meta
            since: Date de début (YYYY-MM-DD)
            until: Date de fin (YYYY-MM-DD)
            level: Niveau de granularité (campaign par défaut)
            
        Returns:
            Liste des campagnes avec leurs contacts Meta
        """
        try:
            url = f"{self.base_url}/act_{ad_account_id}/insights"
            
            params = {
                "access_token": self.access_token,
                "fields": "campaign_id,campaign_name,results",
                "level": level,
                "time_range": f'{{"since":"{since}","until":"{until}"}}',
                "limit": 5000
            }
            if only_active:
                params["effective_status"] = ["ACTIVE"]
            
            logging.info(f"🔍 Récupération contacts Meta via /insights pour {ad_account_id}: {since} à {until}")
            
            all_campaigns = []
            next_cursor = None
            
            while True:
                # Ajouter le cursor pour la pagination
                if next_cursor:
                    params["after"] = next_cursor
                
                response = self._make_meta_request_with_retry(url, params)
                if response is None:
                    logging.error(f"❌ Échec de la requête Meta /insights après retry")
                    return []
                
                response_data = response.json()
                data = response_data.get("data", [])
                
                if not data:
                    logging.warning(f"⚠️ Aucune donnée trouvée pour {ad_account_id}")
                    break
                
                # Traiter chaque campagne
                for campaign_data in data:
                    campaign_id = campaign_data.get('campaign_id', '')
                    campaign_name = campaign_data.get('campaign_name', 'Campagne inconnue')
                    
                    # Filtrer par nom si demandé (insensible à la casse)
                    if name_contains_ci and name_contains_ci.lower() not in str(campaign_name).lower():
                        continue
                    
                    results = campaign_data.get('results', [])
                    
                    # Calculer le total des contacts depuis le champ results
                    contacts_meta = 0
                    
                    if results and isinstance(results, list):
                        for result_item in results:
                            if isinstance(result_item, dict):
                                values = result_item.get('values', [])
                                if values and isinstance(values, list):
                                    for value_item in values:
                                        if isinstance(value_item, dict):
                                            value_str = value_item.get('value', '0')
                                            try:
                                                value_num = int(value_str)
                                                contacts_meta += value_num
                                                logging.debug(f"  📊 Résultat: {value_num} contacts")
                                            except (ValueError, TypeError):
                                                logging.warning(f"  ⚠️ Valeur non numérique: {value_str}")
                    
                    all_campaigns.append({
                        "campaign_id": campaign_id,
                        "campaign_name": campaign_name,
                        "contacts_meta": contacts_meta
                    })
                    
                    logging.info(f"📋 Campagne '{campaign_name}': {contacts_meta} contacts")
                
                # Vérifier s'il y a une page suivante
                paging = response_data.get('paging', {})
                next_cursor = paging.get('cursors', {}).get('after')
                
                if not next_cursor:
                    break
                
                logging.info(f"📄 Page suivante disponible, continuation...")
            
            # Calculer le total des contacts
            total_contacts = sum(campaign['contacts_meta'] for campaign in all_campaigns)
            logging.info(f"📊 Total contacts Meta: {total_contacts} sur {len(all_campaigns)} campagnes")
            
            return all_campaigns
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de la récupération des contacts Meta: {e}")
            return []

    def get_campaign_specific_metrics(
        self, ad_account_id: str, start_date: str, end_date: str, name_contains: str
    ) -> Dict[str, Any]:
        """
        Récupère spend, add_to_cart et CTR pour une campagne filtrée par nom.

        Args:
            ad_account_id: ID du compte publicitaire Meta.
            start_date: Date de début (YYYY-MM-DD).
            end_date: Date de fin (YYYY-MM-DD).
            name_contains: Filtre insensible à la casse sur le nom de campagne.

        Returns:
            {"spend": float, "add_to_cart": int, "ctr": float}
        """
        try:
            url = f"{self.base_url}/act_{ad_account_id}/insights"
            params = {
                "access_token": self.access_token,
                "fields": "campaign_name,spend,ctr,actions",
                "level": "campaign",
                "time_range": f'{{"since":"{start_date}","until":"{end_date}"}}',
                "limit": 100,
            }

            response = self._make_meta_request_with_retry(url, params)
            if response is None:
                return {"spend": 0, "add_to_cart": 0, "ctr": 0}

            data = response.json().get("data", [])
            needle = name_contains.lower()
            data = [c for c in data if needle in str(c.get("campaign_name", "")).lower()]

            if not data:
                logging.warning(f"⚠️ Aucune campagne '{name_contains}' trouvée pour {ad_account_id}")
                return {"spend": 0, "add_to_cart": 0, "ctr": 0}

            total_spend = 0
            total_add_to_cart = 0
            total_search = 0
            total_impressions = 0
            total_clicks = 0

            for camp in data:
                total_spend += float(camp.get("spend", 0))

                actions = camp.get("actions", [])
                # Extraire add_to_cart (prendre le max pour éviter les doublons)
                camp_add_to_cart = 0
                # Extraire recherches de lieu (prendre le max)
                camp_search = 0
                if isinstance(actions, list):
                    for action in actions:
                        if not isinstance(action, dict):
                            continue
                        atype = action.get("action_type", "")
                        value = int(action.get("value", 0))
                        if atype in ("add_to_cart", "offsite_conversion.fb_pixel_add_to_cart"):
                            if value > camp_add_to_cart:
                                camp_add_to_cart = value
                        if atype in ("find_location", "find_location_total", "find_location_website",
                                     "onsite_web_location_search", "location_search",
                                     "offsite_conversion.fb_pixel_custom"):
                            if value > camp_search:
                                camp_search = value
                total_add_to_cart += camp_add_to_cart
                total_search += camp_search

            # Refaire un appel avec impressions/clicks pour calculer le CTR agrégé
            params2 = {
                "access_token": self.access_token,
                "fields": "campaign_name,impressions,clicks",
                "level": "campaign",
                "time_range": f'{{"since":"{start_date}","until":"{end_date}"}}',
                "limit": 100,
            }
            response2 = self._make_meta_request_with_retry(url, params2)
            if response2:
                data2 = response2.json().get("data", [])
                data2 = [c for c in data2 if needle in str(c.get("campaign_name", "")).lower()]
                for camp in data2:
                    total_impressions += int(camp.get("impressions", 0))
                    total_clicks += int(camp.get("clicks", 0))

            ctr = round((total_clicks / total_impressions * 100), 2) if total_impressions > 0 else 0

            logging.info(
                f"📊 Campagne '{name_contains}': spend={total_spend}, "
                f"add_to_cart={total_add_to_cart}, search={total_search}, CTR={ctr}%"
            )

            return {
                "spend": round(total_spend, 2),
                "add_to_cart": total_add_to_cart,
                "search": total_search,
                "ctr": ctr,
            }

        except Exception as e:
            logging.error(f"❌ Erreur get_campaign_specific_metrics: {e}")
            return {"spend": 0, "add_to_cart": 0, "search": 0, "ctr": 0}

    def calculate_meta_metrics(self, insights_data: Optional[Dict[str, Any]], cpl_average: float = 0, ad_account_id: str = None, start_date: str = None, end_date: str = None, contacts_total: int = None) -> Dict[str, Any]:
        """
        Calcule les métriques Meta formatées pour le Google Sheet
        
        Args:
            insights_data: Données d'insights Meta
            cpl_average: CPL moyen calculé
            ad_account_id: ID du compte Meta (pour scraping interface)
            start_date: Date de début (pour scraping interface)
            end_date: Date de fin (pour scraping interface)
            
        Returns:
            Dictionnaire des métriques formatées
        """
        if not insights_data:
            return {}
        
        # Métriques de base
        clicks = int(insights_data.get('clicks', 0))
        link_clicks = int(insights_data.get('link_clicks', 0))
        impressions = int(insights_data.get('impressions', 0))
        ctr = float(insights_data.get('ctr', 0))
        cpc = float(insights_data.get('cpc', 0))  # Maintenant basé sur link_clicks
        spend = float(insights_data.get('spend', 0))
        spend_with_contacts = float(insights_data.get('spend_with_contacts', 0))

        logging.info("META → COMPOSITION SOURCES (avant calcul métriques)")
        logging.info(f"  clicks (total): {clicks}")
        logging.info(f"  link_clicks (base cpc): {link_clicks}")
        logging.info(f"  impressions: {impressions}")
        logging.info(f"  ctr (% brut): {ctr}")
        logging.info(f"  cpc (basé link_clicks): {cpc}")
        logging.info(f"  spend (euros): {spend}")
        logging.info(f"  spend_with_contacts (euros, campagnes avec contacts): {spend_with_contacts}")
        
        # Actions (conversions) - APPROCHE SIMPLIFIÉE
        logging.info("🔍 DÉBUT EXTRACTION MÉTRIQUES META")
        
        # Extraction via API Meta pour les recherches de lieux uniquement
        # Les contacts sont maintenant récupérés via getContactsResults() avec le champ results
        api_contacts, api_searches = self.process_meta_actions(insights_data)
        logging.info(f"📊 DONNÉES API META:")
        logging.info(f"  🎯 Contacts API (ancienne méthode): {api_contacts} (désactivé - utilise getContactsResults())")
        logging.info(f"  📍 Recherches de lieux (extraites): {api_searches}")
        
        # Extraire les contacts depuis insights_data si disponibles (calculés dans get_meta_insights)
        contact_conversions = 0
        contacts_extracted_from_insights = False
        
        # D'abord, essayer d'extraire depuis insights_data (calculés dans get_meta_insights)
        # Cette méthode est plus fiable car elle filtre correctement contacts vs recherches
        if 'conversions' in insights_data and insights_data['conversions']:
            conversions_list = insights_data['conversions']
            logging.info(f"  🔍 DEBUG: conversions_list trouvé, type: {type(conversions_list)}, longueur: {len(conversions_list) if isinstance(conversions_list, list) else 'N/A'}")
            if isinstance(conversions_list, list):
                for conv in conversions_list:
                    logging.info(f"  🔍 DEBUG: conversion item: {conv}")
                    if isinstance(conv, dict):
                        action_type = conv.get('action_type', '')
                        value = conv.get('value', 0)
                        logging.info(f"  🔍 DEBUG: action_type='{action_type}', value='{value}' (type: {type(value)})")
                        if action_type == 'contact_total':
                            try:
                                contact_conversions = int(value)
                                contacts_extracted_from_insights = True
                                logging.info(f"  🎯 Contacts extraits depuis insights_data.conversions: {contact_conversions}")
                                break
                            except (ValueError, TypeError) as e:
                                logging.warning(f"  ⚠️ Erreur conversion valeur contact '{value}': {e}")
            else:
                logging.warning(f"  ⚠️ conversions_list n'est pas une liste: {type(conversions_list)}")
        else:
            logging.info(f"  🔍 DEBUG: Pas de 'conversions' dans insights_data ou vide. Clés disponibles: {list(insights_data.keys()) if insights_data else 'insights_data est None'}")
        
        # Si contacts_total est fourni ET qu'on n'a pas pu extraire depuis insights_data, l'utiliser
        # Note: getContactsResults() peut être moins fiable car il additionne toutes les valeurs de results
        # (y compris les recherches de lieux), donc on préfère les données de insights_data si disponibles
        if contacts_total and contacts_total > 0 and not contacts_extracted_from_insights:
            contact_conversions = contacts_total
            logging.info(f"  🎯 Contacts utilisés depuis contacts_total (getContactsResults): {contact_conversions}")
        elif contacts_total and contacts_total > 0 and contacts_extracted_from_insights:
            logging.info(f"  ⚠️ contacts_total ({contacts_total}) ignoré car contacts déjà extraits depuis insights_data ({contact_conversions}) - insights_data est plus fiable")
        
        # Utiliser directement les données API (plus de scraping d'interface)
        search_conversions = api_searches
        
        logging.info(f"🎯 MÉTRIQUES FINALES SÉLECTIONNÉES:")
        logging.info(f"  🎯 Contact Meta: {contact_conversions}")
        logging.info(f"  📍 Recherche de lieux: {search_conversions}")
        
        # CPL (Cost Per Lead)
        # Si on a un total de contacts, utiliser un CPL pondéré basé sur les dépenses et le total contacts
        cpl = cpl_average
        if contacts_total and contacts_total > 0:
            spend_source = spend_with_contacts if spend_with_contacts > 0 else spend
            if spend_source > 0:
                cpl = round(spend_source / contacts_total, 2)
                logging.info(f"  🧮 CPL recalculé (pondéré): {cpl} = {spend_source}€ / {contacts_total} contacts")
            else:
                logging.info("  🧮 CPL: aucune dépense disponible pour calcul pondéré, fallback cpl_average")
        
        # Métriques formatées selon le tableau demandé
        metrics = {
            "Clics Meta": clicks,
            "Impressions Meta": impressions,
            "CTR Meta": f"{ctr:.2f}%",  # Format pourcentage (ctr est déjà en %)
            "CPC Meta": round(cpc, 2),
            "CPL Meta": cpl,
            "Cout Facebook ADS": round(spend, 2),  # Nom correct de la colonne dans le sheet
            "Contact Meta": contact_conversions,
            "Recherche de lieux": search_conversions
        }
        
        # Log de vérification finale
        logging.info(f"🔍 DEBUG FINAL - Valeurs dans metrics dict:")
        logging.info(f"  Contact Meta = {metrics.get('Contact Meta')}")
        logging.info(f"  Recherche de lieux = {metrics.get('Recherche de lieux')}")
        
        logging.info("META → MÉTRIQUES ENVOYÉES AU SHEET (avec composition)")
        logging.info(f"  Clics Meta = clicks = {clicks}")
        logging.info(f"  Impressions Meta = impressions = {impressions}")
        logging.info(f"  CTR Meta = format({ctr}) depuis insights.ctr")
        logging.info(f"  CPC Meta = round({cpc}, 2) basé sur link_clicks={link_clicks}")
        logging.info(f"  Cout Facebook ADS = round({spend}, 2) depuis insights.spend")
        logging.info(f"  CPL Meta = {cpl} (pondéré si contacts_total fourni, sinon moyenne cost_per_result)")
        logging.info(f"  Contact Meta = {contact_conversions} (depuis contacts_total ou insights_data.conversions)")
        logging.info(f"  Recherche de lieux = {search_conversions} (extraction conversions/actions)")
        logging.info(f"🔗 CPC basé sur {link_clicks} link_clicks (vs {clicks} clics totaux)")
        logging.info(f"💰 CPL basé sur {spend_with_contacts}€ (dépenses campagnes avec contacts) vs {spend}€ total")
        return metrics 