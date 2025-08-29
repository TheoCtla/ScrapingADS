"""
Service de rapports Meta Ads - Gestion des insights et métriques
"""

import logging
import requests
from typing import Dict, Any, Optional

from backend.config.settings import Config

class MetaAdsReportsService:
    """Service pour gérer les rapports et métriques Meta Ads"""
    
    def __init__(self):
        self.access_token = Config.API.META_ACCESS_TOKEN
        self.api_version = "v19.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
    
    def get_meta_insights(self, ad_account_id: str, start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
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
                "fields": "impressions,clicks,ctr,cpc,spend,actions,campaign_name",
                "level": "campaign",  # Récupérer par campagne au lieu de account
                "time_range": f'{{"since":"{start_date}","until":"{end_date}"}}',
                "limit": 100  # Limite pour pagination
            }
            
            logging.info(f"🔍 Appel API Meta pour {ad_account_id}: {start_date} à {end_date} (niveau campagne)")
            
            # Gérer la pagination pour récupérer toutes les campagnes
            all_data = []
            next_url = None
            
            while True:
                if next_url:
                    response = requests.get(next_url)
                else:
                    response = requests.get(url, params=params)
                    
                if response.status_code != 200:
                    logging.error(f"❌ Erreur API Meta: {response.status_code} - {response.text}")
                    return None
                
                response_data = response.json()
                page_data = response_data.get("data", [])
                all_data.extend(page_data)
                
                # Vérifier s'il y a une page suivante
                paging = response_data.get("paging", {})
                next_url = paging.get("next")
                
                if not next_url:
                    break
                    
                logging.info(f"📄 Page suivante trouvée, récupération de {len(page_data)} campagnes supplémentaires...")
            
            data = all_data
            logging.info(f"📊 Données Meta reçues: {len(data)} campagnes")
            
            if not data:
                logging.warning(f"⚠️ Aucune donnée de campagne trouvée pour {ad_account_id}")
                return None
                
            # Agréger manuellement toutes les métriques des campagnes
            aggregated_data = {
                "impressions": 0,
                "clicks": 0,
                "spend": 0.0,
                "actions": [],
                "link_clicks": 0,  # Pour le CPC correct
                "spend_with_contacts": 0.0  # Nouveau : pour le CPL correct
            }
            
            valid_campaigns = 0
            
            for campaign_data in data:
                campaign_name = campaign_data.get('campaign_name', 'Unknown')
                
                # Additionner les métriques simples
                impressions = int(campaign_data.get('impressions', 0))
                clicks = int(campaign_data.get('clicks', 0))
                spend = float(campaign_data.get('spend', 0))
                
                aggregated_data["impressions"] += impressions
                aggregated_data["clicks"] += clicks
                aggregated_data["spend"] += spend
                
                # Agréger les actions ET extraire les link_clicks + détecter contacts
                campaign_actions = campaign_data.get('actions', [])
                has_contacts = False
                
                if campaign_actions:
                    aggregated_data["actions"].extend(campaign_actions)
                    
                    # Extraire les link_clicks spécifiquement pour le CPC
                    for action in campaign_actions:
                        if action.get('action_type') == 'link_click':
                            link_click_value = int(action.get('value', 0))
                            aggregated_data["link_clicks"] += link_click_value
                            logging.info(f"  🔗 Link clicks dans {campaign_name}: {link_click_value}")
                        
                        # Détecter si cette campagne génère des contacts (add_to_cart)
                        elif action.get('action_type') == 'add_to_cart':
                            contact_value = int(action.get('value', 0))
                            if contact_value > 0:
                                has_contacts = True
                                logging.info(f"  👥 Contacts (add_to_cart) dans {campaign_name}: {contact_value}")
                
                # Si cette campagne génère des contacts, ajouter son spend au CPL
                if has_contacts:
                    aggregated_data["spend_with_contacts"] += spend
                    logging.info(f"  💰 Spend pour contacts: {spend}€ (campagne {campaign_name})")
                
                if impressions > 0 or clicks > 0:
                    valid_campaigns += 1
                    logging.info(f"  📈 {campaign_name}: {clicks} clics, {impressions} impressions, {spend}€")
                    
                    # Log des actions pour chaque campagne (pour diagnostic)
                    if campaign_actions:
                        campaign_action_types = [action.get('action_type', 'unknown') for action in campaign_actions]
                        logging.info(f"    🔹 Actions dans {campaign_name}: {campaign_action_types}")
            
            # Calculer les métriques dérivées après agrégation
            total_impressions = aggregated_data["impressions"]
            total_clicks = aggregated_data["clicks"]
            total_link_clicks = aggregated_data["link_clicks"]
            total_spend = aggregated_data["spend"]
            total_spend_with_contacts = aggregated_data["spend_with_contacts"]
            
            # CTR = (Total Clics / Total Impressions) * 100
            aggregated_data["ctr"] = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            
            # CPC = Total Spend / Total Link Clicks (CORRECT !)
            aggregated_data["cpc"] = (total_spend / total_link_clicks) if total_link_clicks > 0 else 0
            
            logging.info(f"🎯 Agrégation finale: {total_clicks} clics, {total_link_clicks} link_clicks, {total_impressions} impressions")
            logging.info(f"💰 Spend total: {total_spend}€, Spend avec contacts: {total_spend_with_contacts}€")
            logging.info(f"🎯 CTR calculé: {aggregated_data['ctr']:.2f}%, CPC calculé: {aggregated_data['cpc']:.2f}€ (basé sur link_clicks)")
            logging.info(f"📊 {valid_campaigns} campagnes avec données sur {len(data)} campagnes totales")
            
            return aggregated_data
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de la récupération des insights Meta: {e}")
            return None
    
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
            
            logging.info(f"🔍 DEBUG: Appel API Meta campagnes pour CPL moyen {ad_account_id}: {start_date} à {end_date}")
            
            response = requests.get(url, params=params)
            if response.status_code != 200:
                logging.error(f"❌ Erreur API Meta campagnes: {response.status_code} - {response.text}")
                return 0
            
            response_data = response.json()
            data = response_data.get("data", [])
            
            logging.info(f"📊 DEBUG: Données campagnes Meta reçues: {len(data)} campagnes")
            
            valid_cpls = []
            
            for i, campaign in enumerate(data):
                campaign_name = campaign.get('campaign_name', 'Unknown')
                cost_per_result = campaign.get('cost_per_result')
                spend = float(campaign.get('spend', 0))
                impressions = int(campaign.get('impressions', 0))
                actions = campaign.get('actions', [])
                
                logging.info(f"🔍 DEBUG Campagne {i+1}: '{campaign_name}'")
                logging.info(f"   - Spend: {spend}€")
                logging.info(f"   - Impressions: {impressions}")
                logging.info(f"   - Actions: {actions}")
                logging.info(f"   - Cost_per_result brut: {cost_per_result}")
                
                # Condition pour campagne active : spend > 0 ET impressions > 0
                is_active = spend > 0 and impressions > 0
                logging.info(f"   - Campagne active ? {is_active}")
                
                if not is_active:
                    logging.info(f"   ❌ Campagne '{campaign_name}' ignorée (inactive)")
                    continue
                
                # Analyser cost_per_result
                if cost_per_result:
                    logging.info(f"   - Cost_per_result existe, longueur: {len(cost_per_result) if isinstance(cost_per_result, list) else 'Not a list'}")
                    
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
                logging.info(f"📊 Détail des CPL: {[round(cpl, 2) for cpl in valid_cpls]}")
                logging.info(f"🎯 RÉSULTAT FINAL: {round(average_cpl, 2)}€")
                return round(average_cpl, 2)
            else:
                logging.warning(f"⚠️ AUCUNE campagne active avec cost_per_result trouvée pour {ad_account_id}")
                return 0
                
        except Exception as e:
            logging.error(f"❌ Erreur lors de la récupération du CPL moyen des campagnes: {e}")
            import traceback
            logging.error(f"❌ Traceback: {traceback.format_exc()}")
            return 0
    
    def process_meta_actions(self, actions: list) -> tuple:
        """
        Traite les actions Meta agrégées pour extraire Contact et Recherche de lieux
        
        Args:
            actions: Liste des actions Meta
            
        Returns:
            Tuple (contact_conversions, search_conversions)
        """
        contact_conversions = 0
        search_conversions = 0
        
        if not actions:
            return contact_conversions, search_conversions
        
        # Agréger les actions par type (car on a maintenant toutes les actions de toutes les campagnes)
        action_totals = {}
        
        for action in actions:
            action_type = action.get('action_type', '')
            value = int(action.get('value', 0))
            
            if action_type in action_totals:
                action_totals[action_type] += value
            else:
                action_totals[action_type] = value
        
        # Extraire les conversions selon les types qui nous intéressent
        for action_type, total_value in action_totals.items():
            action_lower = action_type.lower()
            
            # ✅ LOGIQUE CORRIGÉE - Basée sur les vraies actions Meta
            
            # CONTACTS : Actions de génération de leads
            if action_type in ['onsite_web_lead', 'lead', 'offsite_conversion.fb_pixel_lead']:
                contact_conversions += total_value
                logging.info(f"✅ CONTACT DÉTECTÉ: '{action_type}' = {total_value}")
                
            # RECHERCHES : Actions de recherche de lieux
            elif action_type == 'offsite_conversion.fb_pixel_custom':
                search_conversions += total_value
                logging.info(f"✅ RECHERCHE DÉTECTÉE: '{action_type}' = {total_value}")
                
            # Autres actions (debug seulement)
            else:
                logging.info(f"ℹ️ ACTION AUTRE: '{action_type}' = {total_value}")
        
        logging.info(f"🎯 Actions agrégées: Contact={contact_conversions}, Recherche={search_conversions}")
        if action_totals:
            logging.info(f"🔍 Détail actions par type: {action_totals}")
            logging.info("📋 ANALYSE DES ACTIONS META :")
            for action_type, value in action_totals.items():
                if 'contact' in action_type.lower() or 'lead' in action_type.lower() or 'form' in action_type.lower():
                    logging.info(f"  🎯 CONTACT POTENTIEL: '{action_type}' = {value}")
                elif 'search' in action_type.lower() or 'direction' in action_type.lower() or 'location' in action_type.lower():
                    logging.info(f"  📍 RECHERCHE POTENTIELLE: '{action_type}' = {value}")
                else:
                    logging.info(f"  ❓ AUTRE: '{action_type}' = {value}")
        else:
            logging.warning("⚠️ Aucune action trouvée dans les données Meta")
        
        return contact_conversions, search_conversions
    
    def calculate_meta_metrics(self, insights_data: Optional[Dict[str, Any]], cpl_average: float = 0) -> Dict[str, Any]:
        """
        Calcule les métriques Meta formatées pour le Google Sheet
        
        Args:
            insights_data: Données d'insights Meta
            cpl_average: CPL moyen calculé
            
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
        
        # Actions (conversions)
        actions = insights_data.get('actions', [])
        contact_conversions, search_conversions = self.process_meta_actions(actions)
        
        # CPL (Cost Per Lead) = Moyenne des CPL des campagnes avec conversions > 0
        cpl = cpl_average
        
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
        
        logging.info(f"📈 Métriques Meta calculées: {metrics}")
        logging.info(f"🔗 CPC basé sur {link_clicks} link_clicks (au lieu de {clicks} clics totaux)")
        logging.info(f"💰 CPL basé sur {spend_with_contacts}€ dépenses campagnes avec contacts (au lieu de {spend}€ total)")
        return metrics 