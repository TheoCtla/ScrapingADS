"""
Backend Flask pour le scraping de rapports publicitaires
"""

import sys
import os

# Ajouter le répertoire parent au sys.path pour permettre les imports backend.*
# Utiliser append() au lieu de insert(0) pour éviter les conflits avec les packages du venv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import gc
import calendar
from datetime import datetime, date
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Configuration
from backend.config.settings import Config

# Services communs
from backend.common.services.google_sheets import GoogleSheetsService
from backend.common.services.client_resolver import ClientResolverService
from backend.common.services.light_scraper import LightScraperService
from backend.common.utils.concurrency_manager import with_concurrency_limit, get_concurrency_status

# Services Google Ads
from backend.google_ads_wrapper.services.authentication import GoogleAdsAuthService
from backend.google_ads_wrapper.services.reports import GoogleAdsReportsService
from backend.google_ads_wrapper.services.conversions import GoogleAdsConversionsService
from backend.google_ads_wrapper.utils.mappings import GoogleAdsMappingService

# Services Meta Ads
from backend.meta.services.authentication import MetaAdsAuthService
from backend.meta.services.reports import MetaAdsReportsService
from backend.meta.utils.mappings import MetaAdsMappingService

# Services Google Analytics 4
from backend.google_analytics.services.reports import GoogleAnalyticsReportsService

# Configuration du logging optimisée
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler('backend.log'),
        logging.StreamHandler()
    ]
)

# Réduire les logs verbeux des bibliothèques externes
logging.getLogger('googleapiclient').setLevel(logging.WARNING)
logging.getLogger('google.auth').setLevel(logging.WARNING)
logging.getLogger('google.oauth2').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)

# Initialisation de l'application Flask
app = Flask(__name__)
CORS(app, supports_credentials=True, origins=Config.FLASK.CORS_ORIGINS)

# Assurer que les répertoires nécessaires existent
Config.ensure_directories()

# Valider que toutes les variables sensibles sont définies
try:
    Config.validate_required_vars()
except ValueError as e:
    logging.error(f"Erreur de configuration : {e}")
    raise

# Services globaux (initialisation paresseuse)
_services = {}

def get_service(service_name):
    """Initialise les services de manière paresseuse pour éviter les logs répétitifs"""
    if service_name not in _services:
        if service_name == 'google_auth':
            _services[service_name] = GoogleAdsAuthService()
        elif service_name == 'google_reports':
            _services[service_name] = GoogleAdsReportsService()
        elif service_name == 'google_conversions':
            _services[service_name] = GoogleAdsConversionsService()
        elif service_name == 'google_mappings':
            _services[service_name] = GoogleAdsMappingService()
        elif service_name == 'meta_auth':
            _services[service_name] = MetaAdsAuthService()
        elif service_name == 'meta_reports':
            _services[service_name] = MetaAdsReportsService()
        elif service_name == 'meta_mappings':
            _services[service_name] = MetaAdsMappingService()
        elif service_name == 'ga_reports':
            _services[service_name] = GoogleAnalyticsReportsService()
        elif service_name == 'sheets_service':
            _services[service_name] = GoogleSheetsService()
        elif service_name == 'client_resolver':
            _services[service_name] = ClientResolverService()
        elif service_name == 'light_scraper':
            _services[service_name] = LightScraperService()
        elif service_name == 'google_drive':
            from backend.common.services.google_drive import GoogleDriveService
            _services[service_name] = GoogleDriveService()
    return _services[service_name]

# ================================
# ROUTES UNIFIÉES - NOUVELLES
# ================================

@app.route("/list-authorized-clients", methods=["GET"])
def list_authorized_clients():
    """Liste les clients autorisés (liste blanche)"""
    try:
        client_resolver = get_service('client_resolver')
        allowlist = client_resolver.get_allowlist()
        return jsonify({
            "clients": allowlist,
            "count": len(allowlist)
        })
    except Exception as e:
        logging.error(f"Erreur lors de la récupération de la liste blanche: {str(e)}")
        return jsonify({"error": str(e)}), 500

def normalize_string(text: str) -> str:
    """Normalise une chaîne en supprimant accents, tirets et caractères spéciaux"""
    import unicodedata
    return unicodedata.normalize('NFD', text.lower()).encode('ascii', 'ignore').decode('ascii')

@app.route("/list-filtered-clients", methods=["POST"])
def list_filtered_clients():
    """Liste les clients autorisés filtrés (simule la searchbar)"""
    try:
        data = request.json
        search_term = data.get("search_term", "")
        
        client_resolver = get_service('client_resolver')
        allowlist = client_resolver.get_allowlist()
        
        if search_term:
            normalized_search = normalize_string(search_term)
            filtered_clients = [client for client in allowlist if normalized_search in normalize_string(client)]
        else:
            filtered_clients = allowlist
        
        return jsonify({
            "clients": filtered_clients,
            "count": len(filtered_clients),
            "total_count": len(allowlist)
        })
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des clients filtrés: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/resolve-client", methods=["POST"])
def resolve_client():
    """Résout un nom de client vers ses IDs Google Ads et Meta Ads"""
    try:
        data = request.json
        client_name = data.get("client_name")
        
        if not client_name:
            return jsonify({"error": "Nom de client requis"}), 400
        
        # Valider la sélection
        client_resolver = get_service('client_resolver')
        is_valid, error_message = client_resolver.validate_client_selection(client_name)
        if not is_valid:
            return jsonify({"error": error_message}), 400
        
        # Résoudre les comptes
        resolved_accounts = client_resolver.resolve_client_accounts(client_name)
        client_info = client_resolver.get_client_info(client_name)
        
        return jsonify({
            "client_info": client_info,
            "resolved_accounts": resolved_accounts
        })
        
    except Exception as e:
        logging.error(f"Erreur lors de la résolution du client: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ================================
# ROUTES GOOGLE ADS (LEGACY - À SUPPRIMER)
# ================================

@app.route("/list-customers", methods=["GET"])
def list_google_customers():
    """Liste les clients Google Ads accessibles (LEGACY)"""
    try:
        google_auth = get_service('google_auth')
        customers_info = google_auth.list_customers()
        return jsonify(customers_info)
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des clients Google: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/export-report", methods=["POST"])
def export_google_report():
    """Export des rapports Google Ads avec mise à jour automatique du Google Sheet"""
    data = request.json

    customer_id = data.get("customer_id")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    sheet_month = data.get("sheet_month")
    metrics = data.get("metrics", [
        "metrics.impressions",
        "metrics.clicks",
        "metrics.ctr",
        "metrics.average_cpc",
        "metrics.conversions",
        "metrics.cost_micros"
    ])
    channel_filter = data.get("channel_filter", ["SEARCH", "PERFORMANCE_MAX", "DISPLAY"])

    if not customer_id or not start_date or not end_date:
        logging.error("Paramètres manquants dans /export-report")
        return jsonify({"error": "Paramètres manquants"}), 400

    try:
        # Récupérer les données de campagne
        google_reports = get_service('google_reports')
        response_data = google_reports.get_campaign_data(customer_id, start_date, end_date, channel_filter)
        
        if not response_data:
            logging.warning("Aucune donnée retournée par la requête GAQL")
            return jsonify({"error": "Aucune donnée trouvée"}), 404
        
        # Traitement des données pour le CSV
        headers, data_rows, csv_data = google_reports.process_virtual_metrics_data(response_data, metrics)
        
        # Générer le CSV pour le téléchargement
        csv_output = google_reports.write_csv_from_data(headers, csv_data)
        
        # Sauvegarde du fichier CSV
        filename = f"rapport_google_ads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = Config.PATHS.EXPORTS_DIR / filename
        
        with open(filepath, "w", newline="", encoding='utf-8') as f:
            f.write(csv_output.getvalue())

        # Mise à jour automatique du Google Sheet
        if sheet_month and customer_id:
            try:
                logging.info(f" Tentative de mise à jour du Google Sheet pour {customer_id}, mois: {sheet_month}")
                
                # Calculer les métriques virtuelles
                virtual_metrics = google_reports.calculate_channel_specific_metrics(response_data, metrics)
                
                # Mapper vers les métriques du sheet
                sheet_data = google_reports.calculate_sheet_metrics_from_ads_data(virtual_metrics, metrics)
                
                # Logique d'auto-détection intelligente
                sheets_service = get_service('sheets_service')
                google_mappings = get_service('google_mappings')
                available_sheets = sheets_service.get_worksheet_names()
                sheet_client_name = google_mappings.get_sheet_name_for_customer(customer_id)
                
                if not sheet_client_name:
                    logging.warning(f"Pas de mapping trouvé pour le customer_id: {customer_id}")
                    logging.info(f"Onglets disponibles: {available_sheets}")
                    logging.info(f"Ajoutez le mapping dans client_mappings.json: \"{customer_id}\": \"Nom_Onglet\"")
                else:
                    logging.info(f"Mapping manuel trouvé: {customer_id} -> {sheet_client_name}")
                
                # Procéder à la mise à jour si un onglet a été trouvé
                if sheet_client_name and sheet_client_name in available_sheets:
                    month_row = sheets_service.get_row_for_month(sheet_client_name, sheet_month)
                    
                    if month_row:
                        updates = []
                        
                        for metric_name, metric_value in sheet_data.items():
                            column_letter = sheets_service.get_column_for_metric(sheet_client_name, metric_name)
                            
                            if column_letter:
                                updates.append({
                                    'range': f"{column_letter}{month_row}",
                                    'value': metric_value
                                })
                        
                        if updates:
                            sheets_service.update_sheet_data(sheet_client_name, updates)
                            logging.info(f"Google Sheet mis à jour avec succès: {len(updates)} cellules")
                        
                        # Scraping Contact si demandé
                        contact_enabled = data.get("contact", False)
                        if contact_enabled:
                            try:
                                google_conversions = get_service('google_conversions')
                                contact_result = google_conversions.scrape_contact_conversions_for_customer(
                                    customer_id, sheet_client_name, start_date, end_date, sheet_month
                                )
                                if contact_result.get('success'):
                                    logging.info(f"Scraping Contact réussi: {contact_result.get('total_conversions')} conversions")
                            except Exception as e:
                                logging.error(f"Erreur lors du scraping Contact: {e}")
                        
                        # Scraping Itinéraires si demandé
                        itineraire_enabled = data.get("itineraire", False)
                        if itineraire_enabled:
                            try:
                                google_conversions = get_service('google_conversions')
                                directions_result = google_conversions.scrape_directions_conversions_for_customer(
                                    customer_id, sheet_client_name, start_date, end_date, sheet_month
                                )
                                if directions_result.get('success'):
                                    logging.info(f"Scraping Itinéraires réussi: {directions_result.get('total_conversions')} conversions")
                            except Exception as e:
                                logging.error(f"Erreur lors du scraping Itinéraires: {e}")
                                
            except Exception as e:
                logging.error(f"Erreur lors de la mise à jour du Google Sheet: {str(e)}")
        
        return send_file(filepath, as_attachment=True)
        
    except Exception as e:
        logging.error(f"Erreur lors de l'export Google: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ================================
# ROUTES META ADS
# ================================

@app.route("/list-meta-accounts", methods=["GET"])
def list_meta_accounts():
    """Liste TOUS les comptes Meta Ads accessibles"""
    try:
        meta_auth = get_service('meta_auth')
        all_accounts = meta_auth.get_all_accessible_ad_accounts()
        
        # Formatter pour l'interface frontend
        accounts_info = []
        for account in all_accounts:
            accounts_info.append({
                "ad_account_id": account["account_id"],
                "name": account["name"],
                "status": account["account_status"]
            })

        logging.info(f" {len(accounts_info)} comptes Meta accessibles au total")
        return jsonify(accounts_info)

    except Exception as e:
        logging.error(f"Erreur lors de la récupération des comptes Meta: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ================================
# ROUTES UNIFIÉES
# ================================

@app.route("/export-unified-report", methods=["POST"])
@with_concurrency_limit("unified_report_export", timeout=120)
def export_unified_report():
    data = request.json

    # Paramètres communs
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    sheet_month = data.get("sheet_month")
    selected_client = data.get("selected_client")  # NOUVEAU: nom du client sélectionné

    # Paramètres Google Ads
    google_metrics = data.get("google_metrics", [])

    # Paramètres Meta Ads
    meta_metrics = data.get("meta_metrics", [])
    
    # Ajouter automatiquement la métrique de coût si elle n'est pas sélectionnée
    if meta_metrics and "meta.spend" not in meta_metrics:
        meta_metrics.append("meta.spend")

    # Paramètres de scraping
    contact_enabled = data.get("contact", False)
    itineraire_enabled = data.get("itineraire", False)

    # Paramètre Google Analytics
    include_analytics = data.get("include_analytics", False)

    if not start_date or not end_date:
        return jsonify({"error": "Dates de début et fin requises"}), 400

    if not selected_client:
        return jsonify({"error": "Veuillez sélectionner un client"}), 400

    
    # Valider et résoudre le client
    client_resolver = get_service('client_resolver')
    is_valid, error_message = client_resolver.validate_client_selection(selected_client)
    if not is_valid:
        return jsonify({"error": error_message}), 400
    
    resolved_accounts = client_resolver.resolve_client_accounts(selected_client)
    client_info = client_resolver.get_client_info(selected_client)
    
    # Extraire les IDs résolus
    google_customer_id = resolved_accounts["googleAds"]["customerId"] if resolved_accounts["googleAds"] else None
    meta_account_id = resolved_accounts["metaAds"]["adAccountId"] if resolved_accounts["metaAds"] else None
    meta_campaign_filter = resolved_accounts["metaAds"].get("campaignFilter") if resolved_accounts["metaAds"] else None
    google_campaign_filter = resolved_accounts["googleAds"].get("campaignFilter") if resolved_accounts["googleAds"] else None
    ga_config = resolved_accounts.get("googleAnalytics")

    # Détection Emma (par nom et/ou par IDs connus) — couvre Emma Merignac + Emma Toulouse
    is_emma = (
        selected_client in ("Emma Merignac", "Emma Toulouse")
        or google_customer_id in ("6090621431", "8788853042")
        or meta_account_id in ("2569730083369971", "1548241199574613")
    )
    
    # Détection Roche Bobois Lyon Centre (contacts et recherches forcés à 0)
    is_roche_lyon = selected_client == "Roche bobois Lyon Centre" or google_customer_id == "3938194507"
    
    # Détection Création contemporaine (contacts et recherches forcés à 0)
    is_creation_contemporaine = selected_client == "Création contemporaine" or google_customer_id == "2210445091"
    
    # Détection Roche Bobois Saint-Bonnet (contacts et recherches forcés à 0)
    is_roche_saint_bonnet = selected_client == "Roche bobois Saint-Bonnet" or google_customer_id == "6841136645"
    
    # Détection Riviera Grass (campagnes actives uniquement)
    is_riviera_grass = selected_client == "Riviera Grass" or google_customer_id == "5184726119" or meta_account_id == "1284256950286793"
    
    # Détection Univers Construction (campagnes actives uniquement)
    is_univers_construction = selected_client == "Univers Construction" or google_customer_id == "5509129108" or meta_account_id == "1968946783916182"
    
    # Détection Emma Nantes (campagnes actives uniquement)
    is_emma_nantes = selected_client == "Emma Nantes" or google_customer_id == "9686568792" or meta_account_id == "2281515502281464"

    # Détection Laserel Auxerre / Nantes :
    # - skip Contact/Itinéraires (Google + Meta)
    # - scraping additionnel : "engaged_10s" Meta + custom conversion Google "Temps passé 10sec"
    sel_low = (selected_client or "").lower()
    is_laserel_auxerre = "laserel auxerre" in sel_low
    is_laserel_nantes = "laserel nantes" in sel_low
    is_laserel_branch = is_laserel_auxerre or is_laserel_nantes
    # Conserve l'ancien nom pour compat des autres usages
    is_laserel = is_laserel_branch

    # Détection Alexander Sachs : pas de scraping Google Ads (rapport Meta uniquement)
    is_sachs = selected_client == "Alexander Sachs"

    # Détection Eco Système Durable : élargir le channel_filter Google Ads
    # (compte avec campagnes VIDEO/DEMAND_GEN, exclues par défaut → chiffres incomplets sinon)
    is_eco_systeme_durable = selected_client == "Eco Système Durable"

    # Détection LyleOO : scraping Meta dédié (Interest/Retarget Facebook/Insta + Budget)
    is_lyleoo = selected_client == "LyleOO" or meta_account_id == "2184991331836484"

    # Filtre nom campagne Meta par convention de nommage du client
    meta_campaign_name_filter = None
    if is_emma:
        meta_campaign_name_filter = "Emma"
    elif meta_campaign_filter:
        # Utiliser le filtre spécifique configuré pour le client
        meta_campaign_name_filter = meta_campaign_filter
    else:
        # Logique de fallback pour les anciens clients
        sel_lower = (selected_client or "").lower()
        if "orgeval" in sel_lower:
            meta_campaign_name_filter = "Orgeval"
        elif "melun" in sel_lower:
            meta_campaign_name_filter = "Melun"
    
    
    # Vérifier qu'au moins une plateforme est configurée
    if not google_customer_id and not meta_account_id:
        return jsonify({"error": f"Aucune plateforme configurée pour le client '{selected_client}'"}), 400

    try:
        sheets_service = get_service('sheets_service')
        available_sheets = sheets_service.get_worksheet_names() if sheet_month else []
        successful_updates = []
        failed_updates = []
        platform_warnings = []

        # ===== TRAITEMENT GOOGLE ADS =====
        # Sachs : on n'écrit aucune donnée Google dans le sheet (rapport Meta uniquement)
        if is_sachs and google_metrics:
            logging.info("Alexander Sachs détecté — skip total scraping Google Ads (rapport Meta uniquement)")
            platform_warnings.append("Google Ads skip pour Alexander Sachs")
        elif google_customer_id and google_metrics:
            logging.info(f" Traitement Google Ads pour '{selected_client}' (ID: {google_customer_id})")
            
            try:
                # Récupérer les données de campagne
                google_reports = get_service('google_reports')
                if is_emma:
                    logging.info("Emma détecté — filtrage campagnes Google: actives sur la période uniquement (impressions > 0)")
                if is_riviera_grass:
                    logging.info("Riviera Grass détecté — filtrage campagnes Google: actives sur la période uniquement (impressions > 0)")
                if is_univers_construction:
                    logging.info("Univers Construction détecté — filtrage campagnes Google: actives sur la période uniquement (impressions > 0)")
                if is_emma_nantes:
                    logging.info("Emma Nantes détecté — filtrage campagnes Google: actives sur la période uniquement (impressions > 0)")
                # Channel filter étendu pour les clients qui ont VIDEO/DEMAND_GEN
                google_channel_filter = ["SEARCH", "PERFORMANCE_MAX", "DISPLAY"]
                if is_eco_systeme_durable:
                    google_channel_filter = ["SEARCH", "PERFORMANCE_MAX", "DISPLAY", "VIDEO", "DEMAND_GEN"]
                    logging.info(f"Eco Système Durable détecté — channel_filter étendu: {google_channel_filter}")

                response_data = google_reports.get_campaign_data(
                    google_customer_id,
                    start_date,
                    end_date,
                    only_enabled=is_emma or is_riviera_grass or is_univers_construction or is_emma_nantes or bool(google_campaign_filter),
                    channel_filter=google_channel_filter,
                )
                if is_emma:
                    logging.info(f"Emma Google — campagnes (après filtre): {len(response_data) if response_data else 0}")

                # Filtrer par nom de campagne Google si configuré
                if google_campaign_filter and response_data:
                    filter_lower = google_campaign_filter.lower()
                    before_count = len(response_data)
                    response_data = [row for row in response_data if filter_lower in row.campaign.name.lower()]
                    logging.info(f"Google campaign filter '{google_campaign_filter}': {before_count} → {len(response_data)} campagnes")

                if response_data:
                    # Calculer les métriques virtuelles
                    virtual_metrics = google_reports.calculate_channel_specific_metrics(response_data, google_metrics)
                    
                    # Mettre à jour le Google Sheet si demandé
                    if sheet_month:
                        google_mappings = get_service('google_mappings')
                        sheet_client_name = google_mappings.get_sheet_name_for_customer(google_customer_id)
                        # Pour les comptes partagés avec campaignFilter, utiliser le nom du client sélectionné
                        if google_campaign_filter and selected_client in available_sheets:
                            sheet_client_name = selected_client

                        if sheet_client_name and sheet_client_name in available_sheets:
                            month_row = sheets_service.get_row_for_month(sheet_client_name, sheet_month)
                            
                            if month_row:
                                # Mapper vers les métriques du sheet
                                sheet_data = google_reports.calculate_sheet_metrics_from_ads_data(virtual_metrics, google_metrics)
                                
                                updates = []
                                for metric_name, metric_value in sheet_data.items():
                                    column_letter = sheets_service.get_column_for_metric(sheet_client_name, metric_name)
                                    
                                    if column_letter:
                                        updates.append({
                                            'range': f"{column_letter}{month_row}",
                                            'value': metric_value
                                        })
                                
                                if updates:
                                    sheets_service.update_sheet_data(sheet_client_name, updates)
                                    successful_updates.append(f"Google - {sheet_client_name}: {len(updates)} cellules")
                                    
                                    # Scraping additionnel si demandé (skip pour Laserel : géré manuellement)
                                    if contact_enabled and not is_laserel:
                                        try:
                                            google_conversions = get_service('google_conversions')
                                            google_conversions.scrape_contact_conversions_for_customer(
                                                google_customer_id, sheet_client_name, start_date, end_date, sheet_month
                                            )
                                        except Exception as e:
                                            logging.error(f"Erreur scraping Contact Google {google_customer_id}: {e}")

                                    if itineraire_enabled and not is_laserel:
                                        try:
                                            google_conversions = get_service('google_conversions')
                                            google_conversions.scrape_directions_conversions_for_customer(
                                                google_customer_id, sheet_client_name, start_date, end_date, sheet_month
                                            )
                                        except Exception as e:
                                            logging.error(f"Erreur scraping Itinéraires Google {google_customer_id}: {e}")
                                    if is_laserel and (contact_enabled or itineraire_enabled):
                                        logging.info(f"Laserel Auxerre/Nantes — skip scraping Contact/Itinéraires Google (gérés manuellement)")

                                    # Laserel Auxerre / Nantes : scraping conversion custom 'Temps passé 10sec' → colonne Temps passé Google
                                    if is_laserel_auxerre or is_laserel_nantes:
                                        action_substr = "auxerre temps passé 10sec" if is_laserel_auxerre else "nantes temps passé 10sec"
                                        try:
                                            google_conversions = get_service('google_conversions')
                                            tp_result = google_conversions.scrape_temps_passe_for_customer(
                                                google_customer_id, sheet_client_name, start_date, end_date, sheet_month,
                                                action_name_substring=action_substr,
                                                sheet_column="Temps passé Google",
                                            )
                                            if tp_result.get("success"):
                                                successful_updates.append(f"Google Temps passé - {sheet_client_name}: {tp_result.get('total_conversions')}")
                                            else:
                                                failed_updates.append(f"Google Temps passé - {selected_client}: échec écriture")
                                        except Exception as e:
                                            logging.error(f"❌ Erreur scrape Temps passé Google {google_customer_id}: {e}")
                                            failed_updates.append(f"Google Temps passé - {selected_client}: {e}")
                            else:
                                failed_updates.append(f"Google - {selected_client}: Mois '{sheet_month}' non trouvé")
                        else:
                            failed_updates.append(f"Google - {selected_client}: Pas de mapping vers un onglet Google Sheet")
                else:
                    failed_updates.append(f"Google - {selected_client}: Aucune donnée Google Ads")
                    
            except Exception as e:
                logging.error(f"Erreur Google Ads pour {selected_client}: {e}")
                failed_updates.append(f"Google - {selected_client}: Erreur API")
        elif google_metrics and not google_customer_id:
            platform_warnings.append("Google Ads non configuré pour ce client")

        # ===== TRAITEMENT META ADS (OPTIMISÉ) =====
        if meta_account_id and meta_metrics:
            logging.info(f" Traitement Meta Ads pour '{selected_client}' (ID: {meta_account_id})")
            
            try:
                # Récupérer les données Meta avec timeout strict
                meta_reports = get_service('meta_reports')
                logging.info(f"Début récupération Meta pour {meta_account_id}")
                
                # Utiliser un timeout global pour éviter les blocages
                import threading
                import time
                
                timeout_occurred = threading.Event()
                
                def timeout_handler():
                    timeout_occurred.set()
                
                # Définir un timeout de 60 secondes pour Meta
                timeout_timer = threading.Timer(60.0, timeout_handler)
                timeout_timer.start()
                
                try:
                    # Vérifier si la métrique "Contact Meta" est sélectionnée
                    use_new_contacts_method = "meta.contact" in meta_metrics
                    
                    if use_new_contacts_method:
                        logging.info(f"🔄 Utilisation de la nouvelle méthode getContactsResults() pour les contacts Meta")
                        
                        # Utiliser la nouvelle méthode pour récupérer les contacts via /insights avec results
                        if is_emma:
                            logging.info("Emma détecté — filtrage campagnes Meta: ACTIVE uniquement (effective_status) + nom contient 'Emma' (insensible à la casse)")
                        if is_riviera_grass:
                            logging.info("Riviera Grass détecté — filtrage campagnes Meta: ACTIVE uniquement (effective_status)")
                        if is_univers_construction:
                            logging.info("Univers Construction détecté — filtrage campagnes Meta: ACTIVE uniquement (effective_status)")
                        if is_emma_nantes:
                            logging.info("Emma Nantes détecté — filtrage campagnes Meta: ACTIVE uniquement (effective_status)")
                        if meta_campaign_name_filter:
                            logging.info(f"Filtre nom campagne Meta: contient '{meta_campaign_name_filter}' (insensible à la casse)")
                        contacts_campaigns = meta_reports.getContactsResults(
                            meta_account_id,
                            start_date,
                            end_date,
                            only_active=is_emma or is_riviera_grass or is_univers_construction or is_emma_nantes,
                            name_contains_ci=meta_campaign_name_filter
                        )
                        
                        if contacts_campaigns:
                            # Calculer le total des contacts via getContactsResults() (FALLBACK uniquement)
                            # ⚠️ Cette valeur peut inclure les recherches de lieux, donc on l'utilise seulement si insights_data ne fournit pas de contacts
                            total_contacts_fallback = sum(campaign['contacts_meta'] for campaign in contacts_campaigns)
                            if is_emma:
                                logging.info(f"Emma Meta — campagnes contacts (après filtre): {len(contacts_campaigns)}")
                            logging.info(f"📊 Total contacts Meta via results (fallback): {total_contacts_fallback}")
                            
                            # Initialiser metrics vide - sera rempli par calculate_meta_metrics()
                            metrics = {}
                            
                            # Récupérer les insights classiques pour TOUTES les métriques (y compris Contact Meta)
                            insights = meta_reports.get_meta_insights(
                                meta_account_id,
                                start_date,
                                end_date,
                                only_active=is_emma or is_riviera_grass or is_univers_construction or is_emma_nantes,
                                name_contains_ci=meta_campaign_name_filter
                            )
                            if insights:
                                cpl_average = meta_reports.get_meta_campaigns_cpl_average(meta_account_id, start_date, end_date)
                                # Passer total_contacts_fallback - calculate_meta_metrics() l'utilisera SEULEMENT si insights_data.conversions n'a pas de contacts
                                metrics = meta_reports.calculate_meta_metrics(insights, cpl_average, meta_account_id, start_date, end_date, contacts_total=total_contacts_fallback)
                                if is_emma and isinstance(insights, dict) and 'campaign_count' in insights:
                                    logging.info(f"Emma Meta — campagnes insights (après filtre): {insights['campaign_count']}")
                            
                            # Cas spécial pour Roche Bobois Lyon Centre, Création contemporaine et Roche Saint-Bonnet (contacts et recherches forcés à 0)
                            if is_roche_lyon:
                                logging.info("Roche Bobois Lyon Centre détecté — contacts et recherches forcés à 0")
                                metrics["Contact Meta"] = 0
                                metrics["Recherche de lieux"] = 0
                            elif is_creation_contemporaine:
                                logging.info("Création contemporaine détecté — contacts et recherches forcés à 0")
                                metrics["Contact Meta"] = 0
                                metrics["Recherche de lieux"] = 0
                            elif is_roche_saint_bonnet:
                                logging.info("Roche Bobois Saint-Bonnet détecté — contacts et recherches forcés à 0")
                                metrics["Contact Meta"] = 0
                                metrics["Recherche de lieux"] = 0
                        else:
                            logging.warning(f"⚠️ Aucune donnée de contacts via results trouvée")
                            metrics = {}
                    else:
                        # Utiliser l'ancienne méthode pour toutes les métriques
                        if is_emma:
                            logging.info("Emma détecté — filtrage campagnes Meta: ACTIVE uniquement (effective_status) + nom contient 'Emma' (insensible à la casse)")
                        if is_riviera_grass:
                            logging.info("Riviera Grass détecté — filtrage campagnes Meta: ACTIVE uniquement (effective_status)")
                        if is_univers_construction:
                            logging.info("Univers Construction détecté — filtrage campagnes Meta: ACTIVE uniquement (effective_status)")
                        if is_emma_nantes:
                            logging.info("Emma Nantes détecté — filtrage campagnes Meta: ACTIVE uniquement (effective_status)")
                        if meta_campaign_name_filter:
                            logging.info(f"Filtre nom campagne Meta: contient '{meta_campaign_name_filter}' (insensible à la casse)")
                        insights = meta_reports.get_meta_insights(
                            meta_account_id,
                            start_date,
                            end_date,
                            only_active=is_emma or is_riviera_grass or is_univers_construction or is_emma_nantes,
                            name_contains_ci=meta_campaign_name_filter
                        )
                        timeout_timer.cancel()  # Annuler le timeout
                        logging.info(f"Données Meta récupérées: {insights is not None}")
                        
                        if insights:
                            # Récupérer le CPL moyen des campagnes avec conversions > 0
                            cpl_average = meta_reports.get_meta_campaigns_cpl_average(meta_account_id, start_date, end_date)
                            
                            # Calculer les métriques; ici pas de total contacts consolidé → fallback moyenne
                            metrics = meta_reports.calculate_meta_metrics(insights, cpl_average, meta_account_id, start_date, end_date, contacts_total=None)
                            if is_emma and isinstance(insights, dict) and 'campaign_count' in insights:
                                logging.info(f"Emma Meta — campagnes insights (après filtre): {insights['campaign_count']}")
                            
                            # Cas spécial pour Roche Bobois Lyon Centre, Création contemporaine et Roche Saint-Bonnet (contacts et recherches forcés à 0)
                            if is_roche_lyon:
                                logging.info("Roche Bobois Lyon Centre détecté — contacts et recherches forcés à 0")
                                metrics["Contact Meta"] = 0
                                metrics["Recherche de lieux"] = 0
                            elif is_creation_contemporaine:
                                logging.info("Création contemporaine détecté — contacts et recherches forcés à 0")
                                metrics["Contact Meta"] = 0
                                metrics["Recherche de lieux"] = 0
                            elif is_roche_saint_bonnet:
                                logging.info("Roche Bobois Saint-Bonnet détecté — contacts et recherches forcés à 0")
                                metrics["Contact Meta"] = 0
                                metrics["Recherche de lieux"] = 0
                    
                    # Mettre à jour le Google Sheet si demandé (pour les deux méthodes)
                    if metrics and sheet_month:
                        meta_mappings = get_service('meta_mappings')
                        google_mappings = get_service('google_mappings')

                        # Si un filtre campagne Meta est actif, c'est que plusieurs clients
                        # partagent le même compte Meta (ex: AvivA Melun/Orgeval, Roche Bobois,
                        # Création contemporaine). On écrit alors directement dans l'onglet du
                        # client sélectionné, sans consulter les mappings.
                        if meta_campaign_filter or meta_campaign_name_filter:
                            sheet_name = selected_client
                            logging.info(f"Filtre campagne Meta actif → écriture dans l'onglet '{selected_client}'")
                        else:
                            # Comportement standard : mapping Google d'abord, puis Meta, puis fallback
                            sheet_name = google_mappings.get_sheet_name_for_customer(google_customer_id) if google_customer_id else None
                            if not sheet_name:
                                sheet_name = meta_mappings.get_sheet_name_for_account(meta_account_id)
                            if not sheet_name:
                                sheet_name = selected_client
                            
                        meta_metrics_mapping = meta_mappings.get_meta_metrics_mapping()
                        
                        if sheet_name and sheet_name in available_sheets:
                            month_row = sheets_service.get_row_for_month(sheet_name, sheet_month)
                            
                            if month_row:
                                updates = []

                                # Colonnes à ne pas écrire pour Laserel (gérées manuellement)
                                LASEREL_SKIP_COLUMNS = {"Contact Meta", "Recherche de lieux"}

                                # Ne traiter que les métriques sélectionnées par l'utilisateur
                                for selected_metric in meta_metrics:
                                    # Convertir la valeur frontend vers le nom de colonne
                                    column_name = meta_metrics_mapping.get(selected_metric)

                                    if column_name and column_name in metrics:
                                        # Skip Contact Meta + Recherche de lieux pour Laserel
                                        if is_laserel and column_name in LASEREL_SKIP_COLUMNS:
                                            logging.info(f"Laserel détecté — skip écriture '{column_name}' (gérée manuellement)")
                                            continue

                                        # Récupérer la valeur directement depuis les métriques calculées
                                        metric_value = metrics[column_name]

                                        column_letter = sheets_service.get_column_for_metric(sheet_name, column_name)

                                        if column_letter:
                                            updates.append({
                                                'range': f"{column_letter}{month_row}",
                                                'value': metric_value
                                            })
                                            logging.info(f" {column_name}: {metric_value} → {column_letter}{month_row}")
                                
                                if updates:
                                    sheets_service.update_sheet_data(sheet_name, updates)
                                    successful_updates.append(f"Meta - {sheet_name}: {len(updates)} cellules")
                                else:
                                    failed_updates.append(f"Meta - {selected_client}: Aucune colonne trouvée")

                                # Laserel Auxerre / Nantes : scraping action custom 'engaged_10s' → colonne Temps passé
                                if is_laserel_auxerre or is_laserel_nantes:
                                    action_type = "auxerre_engaged_10s" if is_laserel_auxerre else "nantes_engaged_10s"
                                    try:
                                        tp_total = meta_reports.get_action_total_for_account(
                                            meta_account_id, start_date, end_date, action_type
                                        )
                                        col_letter_tp = sheets_service.get_column_for_metric(sheet_name, "Temps passé")
                                        if col_letter_tp:
                                            sheets_service.update_single_cell(sheet_name, f"{col_letter_tp}{month_row}", tp_total)
                                            successful_updates.append(f"Meta Temps passé - {sheet_name}: {tp_total}")
                                            logging.info(f"⏱️  Meta Temps passé ({action_type}): {tp_total} → {col_letter_tp}{month_row}")
                                        else:
                                            logging.warning(f"⚠️ Colonne 'Temps passé' non trouvée dans '{sheet_name}'")
                                            failed_updates.append(f"Meta Temps passé - {selected_client}: colonne non trouvée")
                                    except Exception as e:
                                        logging.error(f"❌ Erreur scrape engaged_10s Meta {meta_account_id}: {e}")
                                        failed_updates.append(f"Meta Temps passé - {selected_client}: {e}")

                                # Scraping spécifique LyleOO : Interest/Retarget Facebook/Insta + Budget
                                if is_lyleoo and month_row:
                                    try:
                                        ly_data = meta_reports.get_lyleoo_interest_retarget_data(
                                            meta_account_id, start_date, end_date
                                        )
                                        ly_columns = [
                                            ("Interest Facebook", ly_data["interest_facebook"]),
                                            ("Interest Insta", ly_data["interest_insta"]),
                                            ("Interest Budget", ly_data["interest_budget"]),
                                            ("Retarget Facebook", ly_data["retarget_facebook"]),
                                            ("Retarget Insta", ly_data["retarget_insta"]),
                                            ("Retarget Budget", ly_data["retarget_budget"]),
                                        ]
                                        ly_updates = []
                                        for col_name, val in ly_columns:
                                            col_letter = sheets_service.get_column_for_metric(sheet_name, col_name)
                                            if col_letter:
                                                ly_updates.append({
                                                    'range': f"{col_letter}{month_row}",
                                                    'value': val,
                                                })
                                                logging.info(f"  🦄 {col_name}: {val} → {col_letter}{month_row}")
                                            else:
                                                logging.warning(f"  ⚠️ Colonne LyleOO '{col_name}' non trouvée dans '{sheet_name}'")
                                        if ly_updates:
                                            sheets_service.update_sheet_data(sheet_name, ly_updates)
                                            successful_updates.append(f"Meta LyleOO - {sheet_name}: {len(ly_updates)} cellules")
                                    except Exception as e:
                                        logging.error(f"❌ Erreur scraping LyleOO Interest/Retarget: {e}")
                                        failed_updates.append(f"Meta LyleOO - {selected_client}: {e}")

                                # Scraping par campagne spécifique (Sachs)
                                if is_sachs and month_row:
                                    try:
                                        # Lire les headers ligne 3 pour les colonnes campagnes
                                        row3_range = f"'{sheet_name}'!3:3"
                                        row3_result = sheets_service.service.spreadsheets().values().get(
                                            spreadsheetId=sheets_service.sheet_id,
                                            range=row3_range
                                        ).execute()
                                        row3_headers = row3_result.get("values", [[]])[0] if row3_result.get("values") else []

                                        def col_letter_from_row3(col_name):
                                            for idx, h in enumerate(row3_headers):
                                                if h and h.strip() == col_name.strip():
                                                    return sheets_service._index_to_column_letter(idx)
                                            return None

                                        sachs_campaigns = {
                                            "follower": {"Montant": "spend", "Ajout au panier": "add_to_cart", "CTR": "ctr"},
                                            "drive": {"Montant DTS": "spend", "Itinéraires": "search", "CTR DTS": "ctr"},
                                            "interaction": {"Montant SP": "spend", "CTR SP": "ctr"},
                                        }
                                        for camp_filter, col_mapping in sachs_campaigns.items():
                                            camp_data = meta_reports.get_campaign_specific_metrics(
                                                meta_account_id, start_date, end_date, camp_filter)
                                            for col_name, data_key in col_mapping.items():
                                                value = camp_data.get(data_key, 0)
                                                if data_key == "ctr":
                                                    value = f"{value}%"  # Le sheet stocke avec %, le PPTX affiche tel quel
                                                col_letter = col_letter_from_row3(col_name)
                                                if col_letter:
                                                    sheets_service.update_single_cell(sheet_name, f"{col_letter}{month_row}", value)
                                                    logging.info(f"  Sachs {camp_filter} — {col_name}: {value} → {col_letter}{month_row}")
                                                else:
                                                    logging.warning(f"  ⚠️ Colonne '{col_name}' non trouvée en ligne 3 pour Sachs")
                                        successful_updates.append(f"Meta Sachs campagnes - {sheet_name}")
                                    except Exception as e:
                                        logging.error(f"❌ Erreur scraping campagnes Sachs: {e}")
                                        failed_updates.append(f"Meta Sachs campagnes - {selected_client}: {e}")
                            else:
                                failed_updates.append(f"Meta - {selected_client}: Mois '{sheet_month}' non trouvé")
                        else:
                            failed_updates.append(f"Meta - {selected_client}: Pas de mapping vers un onglet Google Sheet")
                    else:
                        failed_updates.append(f"Meta - {selected_client}: Aucune donnée Meta Ads")
                        
                except Exception as timeout_error:
                    timeout_timer.cancel()  # Annuler le timeout
                    if timeout_occurred.is_set():
                        logging.error(f"Timeout Meta Ads pour {selected_client} (60s dépassé)")
                        failed_updates.append(f"Meta - {selected_client}: Timeout (60s)")
                    else:
                        raise timeout_error
                    
            except Exception as e:
                logging.error(f"Erreur Meta Ads pour {selected_client}: {e}")
                logging.error(f"Type d'erreur: {type(e).__name__}")
                failed_updates.append(f"Meta - {selected_client}: Erreur API - {str(e)[:100]}")
                
        elif meta_metrics and not meta_account_id:
            platform_warnings.append("Meta Ads non configuré pour ce client")

        # ========================================
        # GOOGLE ANALYTICS - Vues de pages
        # ========================================
        if include_analytics and ga_config and sheet_month:
            try:
                ga_property_id = ga_config.get("propertyId")
                ga_pages = ga_config.get("pages", [])

                if not ga_property_id or not ga_pages:
                    platform_warnings.append("Analytics: configuration incomplète pour ce client")
                else:
                    # Forcer la plage de dates GA au mois COMPLET dérivé de start_date,
                    # pour éviter les off-by-one (ex: 2026-03-30 au lieu de 2026-03-31)
                    # quand l'utilisateur ajuste manuellement les dates dans le frontend.
                    try:
                        sd = datetime.strptime(start_date, "%Y-%m-%d").date()
                        ga_start = date(sd.year, sd.month, 1).isoformat()
                        ga_end = date(sd.year, sd.month, calendar.monthrange(sd.year, sd.month)[1]).isoformat()
                    except (ValueError, TypeError):
                        ga_start, ga_end = start_date, end_date

                    if (ga_start, ga_end) != (start_date, end_date):
                        logging.info(
                            f"📊 GA4 — plage normalisée au mois complet : "
                            f"{start_date}→{end_date} ⇒ {ga_start}→{ga_end}"
                        )

                    logging.info(f"📊 Scraping GA4 pour {selected_client} (property={ga_property_id}, {len(ga_pages)} pages)")

                    ga_reports = get_service('ga_reports')
                    paths = [p["path"] for p in ga_pages]
                    page_views = ga_reports.get_page_views(ga_property_id, paths, ga_start, ga_end)

                    # Résoudre l'onglet de destination (mêmes règles que Meta)
                    google_mappings = get_service('google_mappings')
                    meta_mappings_svc = get_service('meta_mappings')
                    ga_sheet_name = google_mappings.get_sheet_name_for_customer(google_customer_id) if google_customer_id else None
                    if not ga_sheet_name and meta_account_id:
                        ga_sheet_name = meta_mappings_svc.get_sheet_name_for_account(meta_account_id)
                    if not ga_sheet_name:
                        ga_sheet_name = selected_client

                    if ga_sheet_name and ga_sheet_name in available_sheets:
                        month_row = sheets_service.get_row_for_month(ga_sheet_name, sheet_month)

                        if month_row:
                            updates = []
                            for page in ga_pages:
                                column_name = page["sheetColumn"]
                                value = page_views.get(page["path"], 0)
                                column_letter = sheets_service.get_column_for_metric(ga_sheet_name, column_name)

                                if column_letter:
                                    updates.append({
                                        'range': f"{column_letter}{month_row}",
                                        'value': value
                                    })
                                    logging.info(f"  GA {column_name}: {value} → {column_letter}{month_row}")
                                else:
                                    logging.warning(f"  ⚠️ Colonne GA '{column_name}' non trouvée dans l'onglet '{ga_sheet_name}'")

                            if updates:
                                sheets_service.update_sheet_data(ga_sheet_name, updates)
                                successful_updates.append(f"Analytics - {ga_sheet_name}: {len(updates)} cellules")
                            else:
                                failed_updates.append(f"Analytics - {selected_client}: Aucune colonne trouvée")
                        else:
                            failed_updates.append(f"Analytics - {selected_client}: Mois '{sheet_month}' non trouvé")
                    else:
                        failed_updates.append(f"Analytics - {selected_client}: Onglet '{ga_sheet_name}' introuvable")

            except Exception as e:
                logging.error(f"Erreur Google Analytics pour {selected_client}: {e}")
                failed_updates.append(f"Analytics - {selected_client}: Erreur API - {str(e)[:100]}")
        elif include_analytics and not ga_config:
            platform_warnings.append("Google Analytics non configuré pour ce client")

        # Log des résultats
        if successful_updates:
            logging.info(f"Mises à jour réussies: {successful_updates}")
        if failed_updates:
            logging.warning(f" Échecs: {failed_updates}")
        if platform_warnings:
            logging.info(f"ℹ️ Avertissements plateformes: {platform_warnings}")

        # Scraping leads automatique pour les clients leadgen
        LEADS_CLIENTS = {
            "kozeo": "kozeo",
            "riviera grass": "riviera_grass",
            "sud gazon": "sud_gazon",
            "univers construction": "univers_construction",
            "tairmic": "tairmic",
            "eco système durable": "eco_systeme_durable",
            "univers gazon": "univers_gazon",
        }
        sel_lower = (selected_client or "").lower()
        for keyword, client_key in LEADS_CLIENTS.items():
            if keyword in sel_lower:
                try:
                    from backend.common.services.leads_scraper import _scrape_leads_client
                    leads_result = _scrape_leads_client(sheets_service, client_key, reference_month=None)
                    successful_updates.append(f"Leads {selected_client}: {leads_result['updates_count']} cellules")
                    logging.info(f"✅ Leads scrapés automatiquement pour '{selected_client}'")
                except Exception as e:
                    logging.error(f"❌ Erreur scraping leads auto pour '{selected_client}': {e}")
                    failed_updates.append(f"Leads {selected_client}: {e}")
                break

        # Nettoyage mémoire après traitement
        gc.collect()
        logging.info("🧹 Nettoyage mémoire effectué")

        # Retourner une réponse JSON
        return jsonify({
            "success": True,
            "message": f"Export unifié terminé pour '{selected_client}'",
            "client_info": client_info,
            "successful_updates": successful_updates,
            "failed_updates": failed_updates,
            "platform_warnings": platform_warnings
        })

    except Exception as e:
        logging.error(f"Erreur lors de l'export unifié: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ================================
# ROUTES
# ================================

@app.route("/healthz", methods=["GET"])
def health_check():
    """Endpoint de santé pour Render - optimisé pour éviter les logs répétitifs"""
    return jsonify({"status": "healthy", "service": "scrapping-rapport-backend"}), 200

@app.route("/concurrency-status", methods=["GET"])
def concurrency_status():
    """Endpoint pour monitorer l'état de concurrence"""
    try:
        status = get_concurrency_status()
        return jsonify({
            "status": "success",
            "concurrency": status,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        logging.error(f"Erreur lors de la récupération du statut de concurrence: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def root():
    """Endpoint racine pour éviter les erreurs 404"""
    return jsonify({"message": "Scrapping Rapport API", "status": "running"}), 200

@app.route("/export-meta-only", methods=["POST"])
@with_concurrency_limit("meta_only_export", timeout=60)
def export_meta_only():
    """Endpoint séparé pour Meta Ads uniquement - évite les timeouts"""
    try:
        data = request.json
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        sheet_month = data.get("sheet_month")
        selected_client = data.get("selected_client")
        meta_metrics = data.get("meta_metrics", [])
        
        if not all([start_date, end_date, selected_client]):
            return jsonify({"error": "Paramètres manquants"}), 400
        
        # Résoudre le client
        client_resolver = get_service('client_resolver')
        is_valid, error_message = client_resolver.validate_client_selection(selected_client)
        if not is_valid:
            return jsonify({"error": error_message}), 400
        
        resolved_accounts = client_resolver.resolve_client_accounts(selected_client)
        meta_account_id = resolved_accounts["metaAds"]["adAccountId"] if resolved_accounts["metaAds"] else None
        
        if not meta_account_id:
            return jsonify({"error": "Aucun compte Meta configuré pour ce client"}), 400
        
        # Traitement Meta avec timeout strict
        logging.info(f"Traitement Meta séparé pour {selected_client}")
        
        # TODO: Implémenter le traitement Meta ici une fois les problèmes résolus
        return jsonify({
            "success": True,
            "message": f"Traitement Meta séparé pour '{selected_client}' - En cours de développement",
            "meta_account_id": meta_account_id
        })
        
    except Exception as e:
        logging.error(f"Erreur endpoint Meta séparé: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/update_sheet", methods=["POST"])
def update_sheet():
    """Route pour mettre à jour un Google Sheet avec des données"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Payload JSON requis"}), 400
        
        mois = data.get("mois")
        client_name = data.get("client")
        metrics_data = data.get("data", {})
        
        if not mois or not client_name or not metrics_data:
            return jsonify({
                "error": "Paramètres manquants. Requis: mois, client, data"
            }), 400
        
        logging.info("Début de mise à jour pour client '{client_name}', mois '{mois}'")
        
        # Vérifier que l'onglet du client existe
        sheets_service = get_service('sheets_service')
        sheet_names = sheets_service.get_worksheet_names()
        if client_name not in sheet_names:
            return jsonify({
                "error": f"Client '{client_name}' non trouvé. Onglets disponibles: {sheet_names}"
            }), 404
        
        # Trouver la ligne du mois
        month_row = sheets_service.get_row_for_month(client_name, mois)
        if month_row is None:
            return jsonify({
                "error": f"Mois '{mois}' non trouvé dans l'onglet '{client_name}'"
            }), 404
        
        # Préparer les mises à jour
        updates = []
        missing_metrics = []
        
        for metric_name, metric_value in metrics_data.items():
            column_letter = sheets_service.get_column_for_metric(client_name, metric_name)
            
            if column_letter is None:
                missing_metrics.append(metric_name)
                continue
            
            updates.append({
                'range': f"{column_letter}{month_row}",
                'value': metric_value
            })
        
        if missing_metrics:
            return jsonify({
                "error": f"Métriques non trouvées dans l'onglet '{client_name}': {missing_metrics}"
            }), 404
        
        # Effectuer les mises à jour
        if updates:
            updated_cells = sheets_service.update_sheet_data(client_name, updates)
            
            return jsonify({
                "success": True,
                "client": client_name,
                "mois": mois,
                "onglet": client_name,
                "ligne_mois": month_row,
                "cellules_modifiees": updated_cells,
                "nb_metriques": len(updates)
            }), 200
        else:
            return jsonify({
                "error": "Aucune mise à jour à effectuer"
            }), 400
    
    except Exception as e:
        logging.error(f"Erreur lors de la mise à jour du sheet: {str(e)}")
        return jsonify({
            "error": f"Erreur interne: {str(e)}"
        }), 500

@app.route("/test-auto-detection", methods=["POST"])
def test_auto_detection():
    """Endpoint pour tester l'auto-détection des onglets"""
    try:
        data = request.get_json()
        customer_id = data.get('customer_id')
        
        if not customer_id:
            return jsonify({'error': 'customer_id requis'}), 400
        
        # Test de la logique d'auto-détection
        sheets_service = get_service('sheets_service')
        google_mappings = get_service('google_mappings')
        available_sheets = sheets_service.get_worksheet_names()
        
        # Vérifier mapping manuel
        manual_mapping = google_mappings.get_sheet_name_for_customer(customer_id)
        
        # Auto-détection (simplifiée)
        auto_detected = None
        
        return jsonify({
            'customer_id': customer_id,
            'manual_mapping': manual_mapping,
            'auto_detected': auto_detected,
            'available_sheets': available_sheets,
            'final_choice': manual_mapping or auto_detected
        })
        
    except Exception as e:
        logging.error(f"Erreur test auto-détection: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ================================
# ROUTES SCRAPING LÉGER
# ================================

@app.route("/scrape-light-contact", methods=["POST"])
@with_concurrency_limit("light_contact_scraping", timeout=30)
def scrape_light_contact():
    """Endpoint pour le scraping Contact léger sans navigateur"""
    try:
        data = request.json
        client_name = data.get("client_name")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        
        if not all([client_name, start_date, end_date]):
            return jsonify({"error": "Paramètres manquants: client_name, start_date, end_date"}), 400
        
        light_scraper = get_service('light_scraper')
        result = light_scraper.scrape_contact_conversions_light(client_name, start_date, end_date)
        
        return jsonify(result), 200 if result.get("success") else 500
        
    except Exception as e:
        logging.error(f"Erreur scraping Contact léger: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/scrape-light-directions", methods=["POST"])
@with_concurrency_limit("light_directions_scraping", timeout=30)
def scrape_light_directions():
    """Endpoint pour le scraping Itinéraires léger sans navigateur"""
    try:
        data = request.json
        client_name = data.get("client_name")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        
        if not all([client_name, start_date, end_date]):
            return jsonify({"error": "Paramètres manquants: client_name, start_date, end_date"}), 400
        
        light_scraper = get_service('light_scraper')
        result = light_scraper.scrape_directions_conversions_light(client_name, start_date, end_date)
        
        return jsonify(result), 200 if result.get("success") else 500
        
    except Exception as e:
        logging.error(f"Erreur scraping Itinéraires léger: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/scrape-website-light", methods=["POST"])
@with_concurrency_limit("light_website_scraping", timeout=30)
def scrape_website_light():
    """Endpoint pour le scraping léger de sites web"""
    try:
        data = request.json
        url = data.get("url")
        selectors = data.get("selectors", {})
        
        if not url:
            return jsonify({"error": "URL requise"}), 400
        
        light_scraper = get_service('light_scraper')
        result = light_scraper.scrape_website_light(url, selectors)
        
        return jsonify(result), 200 if result.get("success") else 500
        
    except Exception as e:
        logging.error(f"Erreur scraping site léger: {e}")
        return jsonify({"error": str(e)}), 500

# ================================
# ROUTES EXPORT GOOGLE DRIVE
# ================================

@app.route("/export-to-drive", methods=["POST"])
@with_concurrency_limit("drive_export", timeout=600)  # Timeout plus long pour les téléchargements
def export_to_drive():
    """Export du contenu créatif des campagnes Google Ads et Meta Ads vers Google Drive"""
    try:
        data = request.json
        client_name = data.get("client_name")
        
        if not client_name:
            return jsonify({"error": "Paramètre manquant: client_name"}), 400
        
        logging.info(f"🚀 Début export créatif Drive pour '{client_name}'")
        
        # Résoudre le client
        client_resolver = get_service('client_resolver')
        is_valid, error_message = client_resolver.validate_client_selection(client_name)
        if not is_valid:
            return jsonify({"error": error_message}), 400
        
        resolved_accounts = client_resolver.resolve_client_accounts(client_name)
        google_customer_id = resolved_accounts["googleAds"]["customerId"] if resolved_accounts["googleAds"] else None
        meta_account_id = resolved_accounts["metaAds"]["adAccountId"] if resolved_accounts["metaAds"] else None
        
        if not google_customer_id and not meta_account_id:
            return jsonify({"error": f"Aucune plateforme configurée pour le client '{client_name}'"}), 400
        
        # Initialiser les services
        drive_service = get_service('google_drive')
        
        # Créer ou trouver le dossier client
        client_folder_id = drive_service.find_or_create_folder(
            client_name,
            Config.API.GOOGLE_DRIVE_FOLDER_ID
        )
        
        # Créer le dossier de date sous le client
        today = datetime.now().strftime("%d-%m-%Y")  # Format français: JJ-MM-AAAA
        date_folder_id = drive_service.find_or_create_folder(today, client_folder_id)
        
        # Créer les dossiers de plateforme sous la date
        google_folder_id = drive_service.find_or_create_folder("Google", date_folder_id)
        meta_folder_id = drive_service.find_or_create_folder("Meta", date_folder_id)
        
        exported_files = []
        
        # ===== EXPORT GOOGLE ADS =====
        if google_customer_id:
            try:
                logging.info(f"📊 Export Google Ads créatif pour {client_name} (ID: {google_customer_id})")
                
                # Importer le service créatif Google Ads
                from backend.google_ads_wrapper.services.google_ads_creative import GoogleAdsCreativeService
                google_creative = GoogleAdsCreativeService()
                
                # Récupérer les campagnes actives
                campaigns = google_creative.get_active_campaigns(google_customer_id)
                
                if campaigns:
                    logging.info(f"✅ {len(campaigns)} campagnes Google actives trouvées")
                    
                    # Pour chaque campagne
                    for campaign in campaigns:
                        campaign_id = campaign['id']
                        campaign_name = campaign['name']
                        safe_campaign_name = campaign_name.replace('/', '-').replace('\\', '-').replace("'", "")
                        
                        logging.info(f"📝 Traitement campagne Google: {campaign_name}")
                        
                        # Récupérer toutes les annonces de la campagne avec le type
                        campaign_type = campaign.get('type')
                        ads = google_creative.get_campaign_ads(google_customer_id, campaign_id, campaign_type)
                        
                        if ads:
                            logging.info(f"  📄 {len(ads)} annonces trouvées")
                            
                            # Créer le CSV avec toutes les annonces
                            # En-têtes CSV (avec YouTube Videos URLs)
                            csv_content = "Groupe d'annonces,Nom annonce,Type,URL finale,Headlines,Descriptions,YouTube Videos URLs\n"
                            
                            for ad in ads:
                                # Préparer les champs pour le CSV (échapper les guillemets)
                                ad_group = ad.get("ad_group_name", "").replace('"', '""')
                                ad_name = ad.get("ad_name", "").replace('"', '""')
                                ad_type = ad.get("ad_type", "")
                                
                                headlines = " | ".join(ad.get('headlines', [])).replace('"', '""')
                                descriptions = " | ".join(ad.get('descriptions', [])).replace('"', '""')
                                
                                final_urls = " | ".join(ad.get('final_urls', [])).replace('"', '""')
                                
                                # Extraire les URLs YouTube
                                youtube_urls = " | ".join([yt['url'] for yt in ad.get('youtube_videos', [])]).replace('"', '""')
                                
                                # Ajouter la ligne au CSV
                                csv_content += f'"{ad_group}","{ad_name}","{ad_type}","{final_urls}","{headlines}","{descriptions}","{youtube_urls}"\n'
                            
                            
                            # Créer un dossier pour cette campagne
                            campaign_folder_id = drive_service.find_or_create_folder(safe_campaign_name, google_folder_id)
                            
                            # Télécharger et uploader les médias dans le dossier de la campagne
                            # Télécharger uniquement les images (pas les vidéos YouTube)
                            media_count = 0
                            for ad in ads:
                                # Télécharger les images
                                for img_url in ad.get('images', []):
                                    try:
                                        media_data, media_ext = google_creative.download_media_file(img_url)
                                        if media_data and media_ext:
                                            filename = f"image_{media_count}{media_ext}"
                                            # Construire le mime_type (media_ext contient le point, ex: '.jpg')
                                            mime_type = f"image/{media_ext[1:]}" if media_ext[1:] != 'jpg' else "image/jpeg"
                                            drive_service.upload_media_file(media_data, filename, campaign_folder_id, mime_type)
                                            media_count += 1
                                    except Exception as e:
                                        logging.warning(f"⚠️ Erreur téléchargement image: {e}")
                            
                            logging.info(f"📥 {media_count} images téléchargées")
                            
                            # Uploader le CSV dans le dossier de la campagne
                            csv_filename = f"{safe_campaign_name}_{today}.csv"
                            csv_info = drive_service.upload_csv_to_drive(
                                csv_content,
                                csv_filename,
                                campaign_folder_id
                            )
                            
                            exported_files.append({
                                "platform": "Google Ads",
                                "campaign": campaign_name,
                                "type": "csv",
                                **csv_info
                            })
                            
                            logging.info(f"✅ CSV Google exporté: {csv_filename}")
                        else:
                            logging.warning(f"⚠️ Aucune annonce trouvée pour {campaign_name}")
                else:
                    logging.warning(f"⚠️ Aucune campagne Google active trouvée pour {client_name}")
                    
            except Exception as e:
                logging.error(f"❌ Erreur export Google Ads: {e}")
                import traceback
                logging.error(traceback.format_exc())
        
        # ===== EXPORT META ADS =====
        if meta_account_id:
            try:
                logging.info(f"📊 Export Meta Ads créatif pour {client_name} (ID: {meta_account_id})")
                
                # Importer le service créatif Meta Ads
                from backend.meta.services.meta_ads_creative import MetaAdsCreativeService
                meta_creative = MetaAdsCreativeService()
                
                # Récupérer les campagnes actives
                campaigns = meta_creative.get_active_campaigns(meta_account_id)
                
                if campaigns:
                    logging.info(f"✅ {len(campaigns)} campagnes Meta actives trouvées")
                    
                    # Pour chaque campagne
                    for campaign in campaigns:
                        campaign_id = campaign['id']
                        campaign_name = campaign['name']
                        safe_campaign_name = campaign_name.replace('/', '-').replace('\\', '-').replace("'", "")
                        
                        logging.info(f"📝 Traitement campagne Meta: {campaign_name}")
                        
                        # Récupérer toutes les créations de la campagne
                        creatives = meta_creative.get_campaign_creatives(meta_account_id, campaign_id)
                        
                        if creatives:
                            logging.info(f"  🎨 {len(creatives)} créations trouvées")
                            
                            # Créer le CSV avec toutes les créations (sans URLs de médias)
                            csv_content = "Nom annonce,Titre,Texte,Call to Action,Lien\n"
                            
                            for creative in creatives:
                                name = creative.get("ad_name", "").replace('"', '""')
                                title = creative.get("title", "").replace('"', '""')
                                body = creative.get("body", "").replace('"', '""')
                                cta = creative.get("call_to_action", "").replace('"', '""')
                                link = creative.get("link_url", "").replace('"', '""')
                                
                                csv_content += f'"{name}","{title}","{body}","{cta}","{link}"\n'
                            
                            
                            # Créer un dossier pour cette campagne
                            campaign_folder_id = drive_service.find_or_create_folder(safe_campaign_name, meta_folder_id)
                            
                            # Télécharger et uploader les médias dans le dossier de la campagne
                            media_count = 0
                            for creative in creatives:
                                # Télécharger les images
                                for img_url in creative.get('images', []):
                                    try:
                                        media_data, media_ext = meta_creative.download_media_file(img_url)
                                        if media_data and media_ext:
                                            filename = f"image_{media_count}{media_ext}"
                                            # Construire le mime_type (media_ext contient le point, ex: '.jpg')
                                            mime_type = f"image/{media_ext[1:]}" if media_ext[1:] != 'jpg' else "image/jpeg"
                                            drive_service.upload_media_file(media_data, filename, campaign_folder_id, mime_type)
                                            media_count += 1
                                    except Exception as e:
                                        logging.warning(f"⚠️ Erreur téléchargement image Meta: {e}")
                                
                                # Télécharger les vidéos
                                for vid_url in creative.get('videos', []):
                                    try:
                                        media_data, media_ext = meta_creative.download_media_file(vid_url)
                                        if media_data and media_ext:
                                            filename = f"video_{media_count}{media_ext}"
                                            # Construire le mime_type (media_ext contient le point, ex: '.mp4')
                                            mime_type = f"video/{media_ext[1:]}"
                                            drive_service.upload_media_file(media_data, filename, campaign_folder_id, mime_type)
                                            media_count += 1
                                    except Exception as e:
                                        logging.warning(f"⚠️ Erreur téléchargement vidéo Meta: {e}")
                            
                            logging.info(f"📥 {media_count} fichiers média Meta téléchargés")
                            
                            # Uploader le CSV dans le dossier de la campagne
                            csv_filename = f"{safe_campaign_name}_{today}.csv"
                            csv_info = drive_service.upload_csv_to_drive(
                                csv_content,
                                csv_filename,
                                campaign_folder_id
                            )
                            
                            exported_files.append({
                                "platform": "Meta Ads",
                                "campaign": campaign_name,
                                "type": "csv",
                                **csv_info
                            })
                            
                            logging.info(f"✅ CSV Meta exporté: {csv_filename}")
                        else:
                            logging.warning(f"⚠️ Aucune création trouvée pour {campaign_name}")
                else:
                    logging.warning(f"⚠️ Aucune campagne Meta active trouvée pour {client_name}")
                    
            except Exception as e:
                logging.error(f"❌ Erreur export Meta Ads: {e}")
                import traceback
                logging.error(traceback.format_exc())
        
        logging.info(f"🎉 Export terminé: {len(exported_files)} fichiers créés")
        
        return jsonify({
            "success": True,
            "message": f"Export terminé: {len(exported_files)} fichiers CSV créés dans les dossiers Google/Meta",
            "files": exported_files,
            "client_folder_id": client_folder_id
        }), 200
        
    except Exception as e:
        logging.error(f"❌ Erreur lors de l'export Drive: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


# ================================
# RAPPORTS PPTX
# ================================

@app.route("/generate-report", methods=["POST"])
def generate_report():
    """
    Génère les rapports PPTX pour tous les clients (onglets visibles du Sheet)
    et les uploade sur Google Drive dans le dossier du mois.
    """
    try:
        from backend.reports.generator import generate_all_reports

        data = request.get_json(silent=True) or {}
        filter_name = data.get("filter")
        filter_template = data.get("template")

        result = generate_all_reports(filter_name=filter_name, filter_template=filter_template)

        summary = result["summary"]
        status_code = 200 if summary["errors"] == 0 else 207

        return jsonify(result), status_code

    except Exception as e:
        logging.error(f"Erreur génération rapports: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/scrape-leads", methods=["POST"])
def scrape_leads():
    """
    Scrape les leads depuis les sheets leads clients et écrit les résultats
    dans le sheet principal.
    """
    try:
        from backend.common.services.google_sheets import GoogleSheetsService
        from backend.common.services.leads_scraper import (
            scrape_leads_kozeo, scrape_leads_riviera, scrape_leads_sud_gazon,
            scrape_leads_univers, scrape_leads_tairmic, scrape_leads_eco_systeme_durable,
            scrape_leads_univers_gazon,
        )

        sheets_service = GoogleSheetsService()

        data = request.get_json(silent=True) or {}
        month = data.get("month")  # Optionnel, ex: "February 2026"
        client = data.get("client")  # Optionnel, ex: "kozeo" ou "riviera"

        results = []
        if client == "kozeo":
            results.append(scrape_leads_kozeo(sheets_service, reference_month=month))
        elif client == "riviera":
            results.append(scrape_leads_riviera(sheets_service, reference_month=month))
        elif client == "sudgazon":
            results.append(scrape_leads_sud_gazon(sheets_service, reference_month=month))
        elif client == "univers":
            results.append(scrape_leads_univers(sheets_service, reference_month=month))
        elif client == "tairmic":
            results.append(scrape_leads_tairmic(sheets_service, reference_month=month))
        elif client == "ecosysteme":
            results.append(scrape_leads_eco_systeme_durable(sheets_service, reference_month=month))
        elif client == "universgazon":
            results.append(scrape_leads_univers_gazon(sheets_service, reference_month=month))
        else:
            # Tous les clients
            results.append(scrape_leads_kozeo(sheets_service, reference_month=month))
            results.append(scrape_leads_riviera(sheets_service, reference_month=month))
            results.append(scrape_leads_sud_gazon(sheets_service, reference_month=month))
            results.append(scrape_leads_univers(sheets_service, reference_month=month))
            results.append(scrape_leads_tairmic(sheets_service, reference_month=month))
            results.append(scrape_leads_eco_systeme_durable(sheets_service, reference_month=month))
            results.append(scrape_leads_univers_gazon(sheets_service, reference_month=month))

        return jsonify({"success": True, "results": results}), 200

    except Exception as e:
        logging.error(f"Erreur scraping leads: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# ================================
# POINT D'ENTRÉE PRINCIPAL
# ================================



if __name__ == "__main__":
    logging.info("🚀 Démarrage de l'application de scraping ads")
    logging.info(f" Configuration chargée:")
    logging.info(f"   - Port: {Config.FLASK.PORT}")
    logging.info(f"   - Debug: {Config.FLASK.DEBUG}")
    logging.info(f"   - CORS Origins: {Config.FLASK.CORS_ORIGINS}")
    
    app.run(debug=Config.FLASK.DEBUG, port=Config.FLASK.PORT) 