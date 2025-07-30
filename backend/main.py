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

# Services Google Ads
from backend.google.services.authentication import GoogleAdsAuthService
from backend.google.services.reports import GoogleAdsReportsService
from backend.google.services.conversions import GoogleAdsConversionsService
from backend.google.utils.mappings import GoogleAdsMappingService

# Services Meta Ads
from backend.meta.services.authentication import MetaAdsAuthService
from backend.meta.services.reports import MetaAdsReportsService
from backend.meta.utils.mappings import MetaAdsMappingService

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

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

# Initialisation des services
google_auth = GoogleAdsAuthService()
google_reports = GoogleAdsReportsService()
google_conversions = GoogleAdsConversionsService()
google_mappings = GoogleAdsMappingService()

meta_auth = MetaAdsAuthService()
meta_reports = MetaAdsReportsService()
meta_mappings = MetaAdsMappingService()

sheets_service = GoogleSheetsService()

# ================================
# ROUTES GOOGLE ADS
# ================================

@app.route("/list-customers", methods=["GET"])
def list_google_customers():
    """Liste les clients Google Ads accessibles"""
    try:
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
    data = request.json

    # Paramètres communs
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    sheet_month = data.get("sheet_month")

    # Paramètres Google Ads
    google_customers = data.get("google_customers", [])
    google_metrics = data.get("google_metrics", [])

    # Paramètres Meta Ads
    meta_accounts = data.get("meta_accounts", [])
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

    if not google_customers and not meta_accounts:
        return jsonify({"error": "Veuillez sélectionner au moins un client Google Ads ou Meta Ads"}), 400

    try:
        available_sheets = sheets_service.get_worksheet_names() if sheet_month else []
        successful_updates = []
        failed_updates = []

        # ===== TRAITEMENT GOOGLE ADS =====
        if google_customers:
            logging.info(f"📊 Traitement de {len(google_customers)} comptes Google Ads")
            
            for customer_id in google_customers:
                logging.info(f"🔄 Traitement du compte Google: {customer_id}")
                
                try:
                    # Récupérer les données de campagne
                    response_data = google_reports.get_campaign_data(customer_id, start_date, end_date)
                    
                    if response_data:
                        # Calculer les métriques virtuelles
                        virtual_metrics = google_reports.calculate_channel_specific_metrics(response_data, google_metrics)
                        
                        # Mettre à jour le Google Sheet si demandé
                        if sheet_month:
                            sheet_client_name = google_mappings.get_sheet_name_for_customer(customer_id)
                            
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
                                                google_conversions.scrape_contact_conversions_for_customer(
                                                    customer_id, sheet_client_name, start_date, end_date, sheet_month
                                                )
                                            except Exception as e:
                                                logging.error(f"❌ Erreur scraping Contact Google {customer_id}: {e}")
                                        
                                        if itineraire_enabled:
                                            try:
                                                google_conversions.scrape_directions_conversions_for_customer(
                                                    customer_id, sheet_client_name, start_date, end_date, sheet_month
                                                )
                                            except Exception as e:
                                                logging.error(f"❌ Erreur scraping Itinéraires Google {customer_id}: {e}")
                                    else:
                                        failed_updates.append(f"Google - {customer_id}: Aucune colonne trouvée")
                                else:
                                    failed_updates.append(f"Google - {customer_id}: Mois non trouvé")
                            else:
                                failed_updates.append(f"Google - {customer_id}: Pas de mapping")
                    else:
                        failed_updates.append(f"Google - {customer_id}: Aucune donnée")
                        
                except Exception as e:
                    logging.error(f"❌ Erreur Google Ads pour {customer_id}: {e}")
                    failed_updates.append(f"Google - {customer_id}: Erreur API")

        # ===== TRAITEMENT META ADS =====
        if meta_accounts:
            logging.info(f"📊 Traitement de {len(meta_accounts)} comptes Meta Ads")
            
            for ad_account_id in meta_accounts:
                logging.info(f"🔄 Traitement du compte Meta: {ad_account_id}")
                
                try:
                    # Récupérer les données Meta
                    insights = meta_reports.get_meta_insights(ad_account_id, start_date, end_date)
                    
                    if insights:
                        # Récupérer le CPL moyen des campagnes avec conversions > 0
                        cpl_average = meta_reports.get_meta_campaigns_cpl_average(ad_account_id, start_date, end_date)
                        
                        # Calculer les métriques avec le nouveau CPL
                        metrics = meta_reports.calculate_meta_metrics(insights, cpl_average)
                        
                        # Mettre à jour le Google Sheet si demandé
                        if sheet_month and meta_metrics:
                            sheet_name = meta_mappings.get_sheet_name_for_account(ad_account_id)
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
                                        failed_updates.append(f"Meta - {sheet_name}: Aucune colonne trouvée")
                                else:
                                    failed_updates.append(f"Meta - {sheet_name}: Mois '{sheet_month}' non trouvé")
                            else:
                                failed_updates.append(f"Meta - {ad_account_id}: Pas de mapping vers un onglet Google Sheet")
                    else:
                        failed_updates.append(f"Meta - {ad_account_id}: Aucune donnée")
                        
                except Exception as e:
                    logging.error(f"❌ Erreur Meta Ads pour {ad_account_id}: {e}")
                    failed_updates.append(f"Meta - {ad_account_id}: Erreur API")

        # Log des résultats
        if successful_updates:
            logging.info(f"✅ Mises à jour réussies: {successful_updates}")
        if failed_updates:
            logging.warning(f"⚠️ Échecs: {failed_updates}")

        # Retourner une réponse JSON
        return jsonify({
            "success": True,
            "message": "Données envoyées au Google Sheet avec succès",
            "successful_updates": successful_updates,
            "failed_updates": failed_updates
        })

    except Exception as e:
        logging.error(f"❌ Erreur lors de l'export unifié: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ================================
# ROUTES UTILITAIRES
# ================================

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