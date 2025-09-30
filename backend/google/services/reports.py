"""
Service de rapports Google Ads - Gestion des métriques virtuelles et export
"""

import logging
from typing import Dict, List, Any, Tuple
from collections import defaultdict
from io import StringIO
import csv

from backend.google.services.authentication import GoogleAdsAuthService

class GoogleAdsReportsService:
    """Service pour gérer les rapports et métriques Google Ads"""
    
    def __init__(self):
        self.auth_service = GoogleAdsAuthService()
        
        # Mapping des noms de métriques pour l'affichage
        self.metric_names = {
            "metrics.impressions": "Impressions",
            "metrics.clicks": "Clics",
            "metrics.ctr": "CTR",
            "metrics.average_cpc": "CPC moyen (€)",
            "metrics.conversions": "Conversions",
            "metrics.cost_micros": "Coût (€)",
            "metrics.conversions_from_interactions_rate": "Taux de conversion",
            "metrics.cost_per_conversion": "Coût par conversion",
            "metrics.conversions_value": "Valeur de conversion",
            "metrics.video_views": "Vues de vidéo",
            "metrics.video_view_rate": "Taux de vue de vidéo",
            "metrics.phone_calls": "Appels téléphoniques"
        }
    
    def get_campaign_data(self, customer_id: str, start_date: str, end_date: str, 
                         channel_filter: List[str] = None) -> List:
        """
        Récupère les données de campagne pour un client donné
        
        Args:
            customer_id: ID du client Google Ads
            start_date: Date de début (YYYY-MM-DD)
            end_date: Date de fin (YYYY-MM-DD)
            channel_filter: Liste des canaux à inclure
            
        Returns:
            Liste des batches de résultats
        """
        if channel_filter is None:
            channel_filter = ["SEARCH", "PERFORMANCE_MAX", "DISPLAY"]
        
        # Métriques de base nécessaires pour les calculs
        base_metrics = [
            "metrics.impressions",
            "metrics.clicks", 
            "metrics.ctr",
            "metrics.average_cpc",
            "metrics.cost_micros",
            "metrics.conversions",
            "metrics.phone_calls"
        ]
        
        select_fields = [
            "campaign.advertising_channel_type",
            "campaign.name"
        ] + base_metrics

        query = f"""
        SELECT
            {', '.join(select_fields)}
        FROM campaign
        WHERE
            segments.date BETWEEN '{start_date}' AND '{end_date}'
            AND campaign.advertising_channel_type IN ({','.join([f"'{c}'" for c in channel_filter])})
        """

        logging.info(f"🔍 Récupération des données de campagne pour {customer_id}")
        logging.info(f"📅 Période: {start_date} à {end_date}")
        logging.info(f"📊 Canaux: {channel_filter}")
        
        try:
            response = self.auth_service.fetch_report_data(customer_id, query)
            response_list = list(response)  # Convertir en liste pour pouvoir la réutiliser
            
            # Avec search(), les données sont directement dans response_list, pas dans .results
            total_results = len(response_list) if response_list else 0
            logging.info(f"📈 {total_results} résultats récupérés")
            
            return response_list
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de la récupération des données de campagne: {e}")
            raise
    
    def calculate_channel_specific_metrics(self, response_data: List, selected_metrics: List[str]) -> Dict[str, Any]:
        """
        Calcule les métriques spécialisées par canal à partir des données brutes
        
        Args:
            response_data: Données de réponse de l'API Google Ads
            selected_metrics: Liste des métriques sélectionnées
            
        Returns:
            Dictionnaire des métriques virtuelles calculées
        """
        # Grouper les données par type de canal
        channel_data = {
            'PERFORMANCE_MAX': {'clicks': 0, 'impressions': 0, 'cost_micros': 0, 'cpc_sum': 0, 'cpc_count': 0, 'conversions': 0, 'phone_calls': 0},
            'SEARCH': {'clicks': 0, 'impressions': 0, 'cost_micros': 0, 'cpc_sum': 0, 'cpc_count': 0, 'conversions': 0, 'phone_calls': 0},
            'DISPLAY': {'clicks': 0, 'impressions': 0, 'cost_micros': 0, 'cpc_sum': 0, 'cpc_count': 0, 'conversions': 0, 'phone_calls': 0}
        }
        
        total_data = {'clicks': 0, 'impressions': 0, 'ctr_sum': 0, 'ctr_count': 0, 'cpc_sum': 0, 'cpc_count': 0}
        
        # Debug : compter le nombre de lignes traitées
        total_rows = 0
        channels_found = set()
        
        # Collecter les données par canal
        # Avec search(), les données sont directement dans response_data, pas dans .results
        for row in response_data:
            total_rows += 1
            channel = row.campaign.advertising_channel_type.name
            channels_found.add(channel)
            
            # Log des détails pour les premières lignes
            if total_rows <= 3:
                logging.info(f"📊 Ligne {total_rows}: Channel={channel}, Clicks={row.metrics.clicks}, Impressions={row.metrics.impressions}, Cost={row.metrics.cost_micros}")
            
            if channel in channel_data:
                channel_data[channel]['clicks'] += row.metrics.clicks or 0
                channel_data[channel]['impressions'] += row.metrics.impressions or 0
                channel_data[channel]['cost_micros'] += row.metrics.cost_micros or 0
                channel_data[channel]['conversions'] += row.metrics.conversions or 0
                channel_data[channel]['phone_calls'] += row.metrics.phone_calls or 0
                
                if row.metrics.average_cpc is not None:
                    channel_data[channel]['cpc_sum'] += row.metrics.average_cpc
                    channel_data[channel]['cpc_count'] += 1
            else:
                logging.warning(f"⚠️ Canal non reconnu: {channel}")
            
            # Totaux globaux
            total_data['clicks'] += row.metrics.clicks or 0
            total_data['impressions'] += row.metrics.impressions or 0
            
            if row.metrics.ctr is not None:
                total_data['ctr_sum'] += row.metrics.ctr
                total_data['ctr_count'] += 1
                
            if row.metrics.average_cpc is not None:
                total_data['cpc_sum'] += row.metrics.average_cpc
                total_data['cpc_count'] += 1
        
        # Log des résultats de debug
        logging.info(f"📊 Nombre total de lignes traitées: {total_rows}")
        logging.info(f"📈 Canaux trouvés: {channels_found}")
        logging.info(f"💰 Données par canal: {channel_data}")
        logging.info(f"🎯 Totaux globaux: {total_data}")
        
        # Calculer les métriques virtuelles
        virtual_metrics = {}
        
        # Métriques Perfmax
        perfmax = channel_data['PERFORMANCE_MAX']
        virtual_metrics['metrics.clicks_perfmax'] = perfmax['clicks']
        virtual_metrics['metrics.impressions_perfmax'] = perfmax['impressions']
        virtual_metrics['metrics.cost_perfmax'] = round(perfmax['cost_micros'] / 1e6, 2)
        virtual_metrics['metrics.average_cpc_perfmax'] = round(perfmax['cost_micros'] / 1e6 / perfmax['clicks'], 2) if perfmax['clicks'] > 0 else 0
        
        # Métriques Search
        search = channel_data['SEARCH']
        virtual_metrics['metrics.clicks_search'] = search['clicks']
        virtual_metrics['metrics.impressions_search'] = search['impressions']
        virtual_metrics['metrics.cost_search'] = round(search['cost_micros'] / 1e6, 2)
        virtual_metrics['metrics.average_cpc_search'] = round(search['cost_micros'] / 1e6 / search['clicks'], 2) if search['clicks'] > 0 else 0
        
        # Métriques Display
        display = channel_data['DISPLAY']
        virtual_metrics['metrics.clicks_display'] = display['clicks']
        virtual_metrics['metrics.impressions_display'] = display['impressions']
        virtual_metrics['metrics.cost_display'] = round(display['cost_micros'] / 1e6, 2)
        virtual_metrics['metrics.average_cpc_display'] = round(display['cost_micros'] / 1e6 / display['clicks'], 2) if display['clicks'] > 0 else 0
        
        # Métriques globales
        virtual_metrics['metrics.total_clicks'] = total_data['clicks']
        virtual_metrics['metrics.impressions'] = total_data['impressions']
        virtual_metrics['metrics.ctr'] = f"{(total_data['ctr_sum'] / total_data['ctr_count']):.2%}" if total_data['ctr_count'] > 0 else "0.00%"
        
        # CPC global = coût total / clics totaux
        total_cost = sum(channel_data[ch]['cost_micros'] for ch in channel_data)
        virtual_metrics['metrics.average_cpc'] = round(total_cost / 1e6 / total_data['clicks'], 2) if total_data['clicks'] > 0 else 0
        
        # Coût total en euros
        virtual_metrics['metrics.cost_micros'] = round(total_cost / 1e6, 2)
        
        # Conversions totales
        total_conversions = sum(channel_data[ch]['conversions'] for ch in channel_data)
        total_phone_calls = sum(channel_data[ch]['phone_calls'] for ch in channel_data)
        
        virtual_metrics['metrics.conversions'] = total_conversions
        virtual_metrics['metrics.phone_calls'] = total_phone_calls
        
        return virtual_metrics
    
    def process_virtual_metrics_data(self, response_data: List, selected_metrics: List[str]) -> Tuple[List[str], List[List], List[List]]:
        """
        Traite les données en calculant les métriques virtuelles pour le format vertical
        
        Args:
            response_data: Données de réponse de l'API
            selected_metrics: Liste des métriques sélectionnées
            
        Returns:
            Tuple (headers, data_rows, csv_data)
        """
        # Noms français des métriques
        metric_names = {
            "metrics.clicks_perfmax": "Clics Perfmax",
            "metrics.impressions_perfmax": "Impressions Perfmax", 
            "metrics.average_cpc_perfmax": "CPC Perfmax (€)",
            "metrics.cost_perfmax": "Coût Perfmax (€)",
            "metrics.clicks_search": "Clics Search",
            "metrics.impressions_search": "Impressions Search",
            "metrics.average_cpc_search": "CPC Search (€)", 
            "metrics.cost_search": "Coût Search (€)",
            "metrics.clicks_display": "Clics Display",
            "metrics.impressions_display": "Impressions Display",
            "metrics.average_cpc_display": "CPC Display (€)",
            "metrics.cost_display": "Coût Display (€)",
            "metrics.total_clicks": "Total Clics",
            "metrics.ctr": "CTR",
            "metrics.impressions": "Impressions",
            "metrics.average_cpc": "CPC moyen (€)",
            "metrics.cost_micros": "Coût Total (€)",
            "metrics.conversions": "Conversions",
            "metrics.phone_calls": "Appels téléphoniques"
        }
        
        # Calculer toutes les métriques virtuelles
        virtual_metrics = self.calculate_channel_specific_metrics(response_data, selected_metrics)
        
        # Créer une "campagne virtuelle" avec toutes les données
        campaign_name = "Données Globales"
        
        # Headers : ["Métrique", "Campagne"]  
        headers = ["Métrique", campaign_name]
        
        # Data rows : Une ligne par métrique sélectionnée
        data_rows = []
        csv_data = []
        
        for metric in selected_metrics:
            metric_label = metric_names.get(metric, metric)
            value = virtual_metrics.get(metric, "0")
            
            row_data = [metric_label, value]
            data_rows.append(row_data)
            csv_data.append(row_data)
        
        return headers, data_rows, csv_data
    
    def calculate_sheet_metrics_from_ads_data(self, virtual_metrics: Dict[str, Any], selected_metrics: List[str]) -> Dict[str, Any]:
        """
        Convertit les métriques calculées de Google Ads vers le format du Google Sheet
        
        Args:
            virtual_metrics: Données calculées depuis Google Ads
            selected_metrics: Liste des métriques sélectionnées par l'utilisateur
        
        Returns:
            Dictionnaire avec seulement les métriques sélectionnées
        """
        # Mapping complet des métriques virtuelles vers les noms du Google Sheet
        metrics_mapping = {
            "metrics.cost_micros": "Cout Google ADS",
            "metrics.clicks_search": "Clics search", 
            "metrics.impressions_search": "Impressions Search",
            "metrics.average_cpc_search": "CPC Search",
            "metrics.clicks_perfmax": "Clics Perf Max",
            "metrics.impressions_perfmax": "Impressions Perf Max", 
            "metrics.clicks_display": "Clics Display",
            "metrics.impressions_display": "Impressions Display",
            "metrics.average_cpc_display": "CPC Display",
            "metrics.cost_display": "Cout Display",
            "metrics.cost_search": "Cout Search",
            "metrics.cost_perfmax": "Cout PM",
            "metrics.total_clicks": "Total Clic",
            "metrics.impressions": "Total Impressions",
            "metrics.average_cpc": "Total CPC moyen",
            "metrics.ctr": "CTR Google"
        }
        
        # Ne retourner que les métriques sélectionnées par l'utilisateur
        result = {}
        
        for selected_metric in selected_metrics:
            if selected_metric in metrics_mapping:
                sheet_metric_name = metrics_mapping[selected_metric]
                metric_value = virtual_metrics.get(selected_metric, 0)
                result[sheet_metric_name] = metric_value
                logging.info(f"🎯 Métrique sélectionnée: {selected_metric} -> {sheet_metric_name} = {metric_value}")
            else:
                logging.warning(f"⚠️ Métrique non mappée: {selected_metric}")
        
        return result
    
    def write_csv_from_data(self, headers: List[str], csv_data: List[List]) -> StringIO:
        """
        Crée un CSV à partir de données déjà formatées
        
        Args:
            headers: En-têtes du CSV
            csv_data: Données à écrire
            
        Returns:
            StringIO contenant le CSV
        """
        output = StringIO()
        writer = csv.writer(output)
        
        # Écrire les headers
        writer.writerow(headers)
        
        # Écrire les données
        for row in csv_data:
            writer.writerow(row)
        
        output.seek(0)
        return output 