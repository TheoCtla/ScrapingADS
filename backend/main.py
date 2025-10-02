"""
Point d'entrée principal de l'application de reporting publicitaire
"""

import logging
import os
from datetime import datetime
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

# Services Google Ads
from backend.google.services.authentication import GoogleAdsAuthService
from backend.google.services.reports import GoogleAdsReportsService
from backend.google.services.conversions import GoogleAdsConversionsService
from backend.google.utils.mappings import GoogleAdsMappingService

# Services Meta Ads
from backend.meta.services.authentication import MetaAdsAuthService
from backend.meta.services.reports import MetaAdsReportsService
from backend.meta.utils.mappings import MetaAdsMappingService

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
    logging.info("✅ Toutes les variables d'environnement sont configurées")
except ValueError as e:
    logging.error(f"❌ Erreur de configuration : {e}")
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
        elif service_name == 'sheets_service':
            _services[service_name] = GoogleSheetsService()
        elif service_name == 'client_resolver':
            _services[service_name] = ClientResolverService()
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
        logging.error(f"❌ Erreur lors de la récupération de la liste blanche: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/list-filtered-clients", methods=["POST"])
def list_filtered_clients():
    """Liste les clients autorisés filtrés (simule la searchbar)"""
    try:
        data = request.json
        search_term = data.get("search_term", "").lower()
        
        client_resolver = get_service('client_resolver')
        allowlist = client_resolver.get_allowlist()
        
        if search_term:
            filtered_clients = [client for client in allowlist if search_term in client.lower()]
        else:
            filtered_clients = allowlist
        
        return jsonify({
            "clients": filtered_clients,
            "count": len(filtered_clients),
            "total_count": len(allowlist)
        })
    except Exception as e:
        logging.error(f"❌ Erreur lors de la récupération des clients filtrés: {str(e)}")
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
        logging.error(f"❌ Erreur lors de la résolution du client: {str(e)}")
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
        logging.error(f"❌ Erreur lors de la récupération des clients Google: {str(e)}")
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
        logging.error("❌ Paramètres manquants dans /export-report")
        return jsonify({"error": "Paramètres manquants"}), 400

    try:
        # Récupérer les données de campagne
        google_reports = get_service('google_reports')
        response_data = google_reports.get_campaign_data(customer_id, start_date, end_date, channel_filter)
        
        if not response_data:
            logging.warning("⚠️ Aucune donnée retournée par la requête GAQL")
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
                logging.info(f"📊 Tentative de mise à jour du Google Sheet pour {customer_id}, mois: {sheet_month}")
                
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
                    logging.warning(f"⚠️ Pas de mapping trouvé pour le customer_id: {customer_id}")
                    logging.info(f"📋 Onglets disponibles: {available_sheets}")
                    logging.info(f"💡 Ajoutez le mapping dans client_mappings.json: \"{customer_id}\": \"Nom_Onglet\"")
                else:
                    logging.info(f"📋 Mapping manuel trouvé: {customer_id} -> {sheet_client_name}")
                
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
                            logging.info(f"✅ Google Sheet mis à jour avec succès: {len(updates)} cellules")
                        
                        # Scraping Contact si demandé
                        contact_enabled = data.get("contact", False)
                        if contact_enabled:
                            try:
                                google_conversions = get_service('google_conversions')
                                contact_result = google_conversions.scrape_contact_conversions_for_customer(
                                    customer_id, sheet_client_name, start_date, end_date, sheet_month
                                )
                                if contact_result.get('success'):
                                    logging.info(f"✅ Scraping Contact réussi: {contact_result.get('total_conversions')} conversions")
                            except Exception as e:
                                logging.error(f"❌ Erreur lors du scraping Contact: {e}")
                        
                        # Scraping Itinéraires si demandé
                        itineraire_enabled = data.get("itineraire", False)
                        if itineraire_enabled:
                            try:
                                google_conversions = get_service('google_conversions')
                                directions_result = google_conversions.scrape_directions_conversions_for_customer(
                                    customer_id, sheet_client_name, start_date, end_date, sheet_month
                                )
                                if directions_result.get('success'):
                                    logging.info(f"✅ Scraping Itinéraires réussi: {directions_result.get('total_conversions')} conversions")
                            except Exception as e:
                                logging.error(f"❌ Erreur lors du scraping Itinéraires: {e}")
                                
            except Exception as e:
                logging.error(f"❌ Erreur lors de la mise à jour du Google Sheet: {str(e)}")
        
        return send_file(filepath, as_attachment=True)
        
    except Exception as e:
        logging.error(f"❌ Erreur lors de l'export Google: {str(e)}")
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

        logging.info(f"📋 {len(accounts_info)} comptes Meta accessibles au total")
        return jsonify(accounts_info)

    except Exception as e:
        logging.error(f"❌ Erreur lors de la récupération des comptes Meta: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ================================
# ROUTES UNIFIÉES
# ================================

@app.route("/export-unified-report", methods=["POST"])
def export_unified_report():
    """Export unifié pour Google Ads + Meta Ads avec checkboxes"""
    logging.info("🚀 ROUTE /export-unified-report appelée")
    data = request.json
    logging.info(f"📥 Données reçues: {data}")

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
        logging.info("🔧 Ajout automatique de la métrique 'meta.spend' au rapport unifié")

    # Paramètres de scraping
    contact_enabled = data.get("contact", False)
    itineraire_enabled = data.get("itineraire", False)

    if not start_date or not end_date:
        return jsonify({"error": "Dates de début et fin requises"}), 400

    if not selected_client:
        return jsonify({"error": "Veuillez sélectionner un client"}), 400

    # NOUVEAU: Résolution du client sélectionné
    logging.info(f"🎯 Traitement du client sélectionné: {selected_client}")
    
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
    
    logging.info(f"🔍 IDs résolus pour '{selected_client}': Google={google_customer_id}, Meta={meta_account_id}")
    
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
        if google_customer_id and google_metrics:
            logging.info(f"📊 Traitement Google Ads pour '{selected_client}' (ID: {google_customer_id})")
            
            try:
                # Récupérer les données de campagne
                google_reports = get_service('google_reports')
                response_data = google_reports.get_campaign_data(google_customer_id, start_date, end_date)
                
                if response_data:
                    # Calculer les métriques virtuelles
                    virtual_metrics = google_reports.calculate_channel_specific_metrics(response_data, google_metrics)
                    
                    # Mettre à jour le Google Sheet si demandé
                    if sheet_month:
                        google_mappings = get_service('google_mappings')
                        sheet_client_name = google_mappings.get_sheet_name_for_customer(google_customer_id)
                        
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
                                    
                                    # Scraping additionnel si demandé
                                    if contact_enabled:
                                        try:
                                            google_conversions = get_service('google_conversions')
                                            google_conversions.scrape_contact_conversions_for_customer(
                                                google_customer_id, sheet_client_name, start_date, end_date, sheet_month
                                            )
                                        except Exception as e:
                                            logging.error(f"❌ Erreur scraping Contact Google {google_customer_id}: {e}")
                                    
                                    if itineraire_enabled:
                                        try:
                                            google_conversions = get_service('google_conversions')
                                            google_conversions.scrape_directions_conversions_for_customer(
                                                google_customer_id, sheet_client_name, start_date, end_date, sheet_month
                                            )
                                        except Exception as e:
                                            logging.error(f"❌ Erreur scraping Itinéraires Google {google_customer_id}: {e}")
                            else:
                                failed_updates.append(f"Google - {selected_client}: Mois '{sheet_month}' non trouvé")
                        else:
                            failed_updates.append(f"Google - {selected_client}: Pas de mapping vers un onglet Google Sheet")
                else:
                    failed_updates.append(f"Google - {selected_client}: Aucune donnée Google Ads")
                    
            except Exception as e:
                logging.error(f"❌ Erreur Google Ads pour {selected_client}: {e}")
                failed_updates.append(f"Google - {selected_client}: Erreur API")
        elif google_metrics and not google_customer_id:
            platform_warnings.append("Google Ads non configuré pour ce client")

        # ===== TRAITEMENT META ADS =====
        if meta_account_id and meta_metrics:
            logging.info(f"📊 Traitement Meta Ads pour '{selected_client}' (ID: {meta_account_id})")
            
            try:
                # Récupérer les données Meta
                meta_reports = get_service('meta_reports')
                insights = meta_reports.get_meta_insights(meta_account_id, start_date, end_date)
                
                if insights:
                    # Récupérer le CPL moyen des campagnes avec conversions > 0
                    cpl_average = meta_reports.get_meta_campaigns_cpl_average(meta_account_id, start_date, end_date)
                    
                    # Calculer les métriques avec le nouveau CPL
                    metrics = meta_reports.calculate_meta_metrics(insights, cpl_average)
                    
                    # Mettre à jour le Google Sheet si demandé
                    if sheet_month:
                        meta_mappings = get_service('meta_mappings')
                        sheet_name = meta_mappings.get_sheet_name_for_account(meta_account_id)
                        meta_metrics_mapping = meta_mappings.get_meta_metrics_mapping()
                        
                        if sheet_name and sheet_name in available_sheets:
                            month_row = sheets_service.get_row_for_month(sheet_name, sheet_month)
                            
                            if month_row:
                                updates = []
                                
                                # Ne traiter que les métriques sélectionnées par l'utilisateur
                                for selected_metric in meta_metrics:
                                    # Convertir la valeur frontend vers le nom de colonne
                                    column_name = meta_metrics_mapping.get(selected_metric)
                                    
                                    if column_name and column_name in metrics:
                                        # Récupérer la valeur directement depuis les métriques calculées
                                        metric_value = metrics[column_name]
                                        
                                        column_letter = sheets_service.get_column_for_metric(sheet_name, column_name)
                                        
                                        if column_letter:
                                            updates.append({
                                                'range': f"{column_letter}{month_row}",
                                                'value': metric_value
                                            })
                                            logging.info(f"📊 {column_name}: {metric_value} → {column_letter}{month_row}")
                                
                                if updates:
                                    sheets_service.update_sheet_data(sheet_name, updates)
                                    successful_updates.append(f"Meta - {sheet_name}: {len(updates)} cellules")
                                else:
                                    failed_updates.append(f"Meta - {selected_client}: Aucune colonne trouvée")
                            else:
                                failed_updates.append(f"Meta - {selected_client}: Mois '{sheet_month}' non trouvé")
                        else:
                            failed_updates.append(f"Meta - {selected_client}: Pas de mapping vers un onglet Google Sheet")
                else:
                    failed_updates.append(f"Meta - {selected_client}: Aucune donnée Meta Ads")
                    
            except Exception as e:
                logging.error(f"❌ Erreur Meta Ads pour {selected_client}: {e}")
                failed_updates.append(f"Meta - {selected_client}: Erreur API")
        elif meta_metrics and not meta_account_id:
            platform_warnings.append("Meta Ads non configuré pour ce client")

        # Log des résultats
        if successful_updates:
            logging.info(f"✅ Mises à jour réussies: {successful_updates}")
        if failed_updates:
            logging.warning(f"⚠️ Échecs: {failed_updates}")
        if platform_warnings:
            logging.info(f"ℹ️ Avertissements plateformes: {platform_warnings}")

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
        logging.error(f"❌ Erreur lors de l'export unifié: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ================================
# ROUTES UTILITAIRES
# ================================

@app.route("/healthz", methods=["GET"])
def health_check():
    """Endpoint de santé pour Render - optimisé pour éviter les logs répétitifs"""
    return jsonify({"status": "healthy", "service": "scrapping-rapport-backend"}), 200

@app.route("/", methods=["GET"])
def root():
    """Endpoint racine pour éviter les erreurs 404"""
    return jsonify({"message": "Scrapping Rapport API", "status": "running"}), 200

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
        
        logging.info(f"🔄 Début de mise à jour pour client '{client_name}', mois '{mois}'")
        
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
        logging.error(f"❌ Erreur lors de la mise à jour du sheet: {str(e)}")
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
        logging.error(f"❌ Erreur test auto-détection: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ================================
# POINT D'ENTRÉE PRINCIPAL
# ================================

if __name__ == "__main__":
    logging.info("🚀 Démarrage de l'application de reporting publicitaire")
    logging.info(f"📋 Configuration chargée:")
    logging.info(f"   - Port: {Config.FLASK.PORT}")
    logging.info(f"   - Debug: {Config.FLASK.DEBUG}")
    logging.info(f"   - CORS Origins: {Config.FLASK.CORS_ORIGINS}")
    
    app.run(debug=Config.FLASK.DEBUG, port=Config.FLASK.PORT) 