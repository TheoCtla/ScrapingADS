"""
Service de conversions Google Ads - Gestion des conversions Contact et Itinéraires
Version finale avec correction de l'itération
"""

import logging
from typing import Tuple, List, Dict, Any
from google.ads.googleads.errors import GoogleAdsException

from backend.google_ads_wrapper.services.authentication import GoogleAdsAuthService
from backend.common.services.google_sheets import GoogleSheetsService

class GoogleAdsConversionsService:
    """Service pour gérer les conversions Google Ads"""
    
    def __init__(self):
        self.auth_service = GoogleAdsAuthService()
        self.sheets_service = GoogleSheetsService()
        
        # Noms des conversions à chercher (insensible à la casse)
        # Étendus pour couvrir plus de cas
        self.TARGET_CONTACT_NAMES = [
            "appels",
            "cta", 
            "appel (cta)",
            "clicks to call",
            "contact",
            "call",
            "phone"
        ]
        
        self.TARGET_DIRECTIONS_NAMES = [
            "itinéraires",
            "local actions - directions", 
            "itinéraires magasin",
            "click map",
            "directions",
            "local actions",
            "store visits"
        ]
        
        self.CRYOLIPOLYSE_CONTACT_NAMES = [
            "appels",
            "cta"
        ]
        
        # Addario: uniquement "appels" et "cta" pour les contacts
        self.ADDARIO_CONTACT_NAMES = [
            "appels",
            "cta"
        ]
        
        self.ADDARIO_DIRECTIONS_NAMES = [
            "itinéraires",
            "local actions - directions"
        ]
        
        self.CROZATIER_CONTACT_NAMES = [
            "appels",
            "clicks to call"
        ]
        
        self.DENTEVA_CONTACT_NAMES = [
            "action de conversion",
            "appels"
        ]
        
        self.DENTEVA_DIRECTIONS_NAMES = [
            "itinéraires",
            "click map",
            "local actions - directions"
        ]
        
        self.EVOPRO_CONTACT_NAMES = [
            "action de conversion",
            "appel (cta)",
            "cta",
            "clicks to call",
            "appels",
            "appel (footer)"
        ]
        
        self.EVOPRO_DIRECTIONS_NAMES = [
            "itinéraires",
            "local actions - directions"
        ]
        
        self.FRANCE_LITERIE_AIX_CONTACT_NAMES = [
            "appels",
            "cta"
        ]
        
        self.FRANCE_LITERIE_AIX_DIRECTIONS_NAMES = [
            "itinéraires",
            "local actions - directions"
        ]
        
        self.FRANCE_LITERIE_ANNEMASSE_CONTACT_NAMES = [
            "appels",
            "clicks to call"
        ]
        
        self.FRANCE_LITERIE_ANNEMASSE_DIRECTIONS_NAMES = [
            "itinéraires",
            "local actions - directions"
        ]
        
        self.FRANCE_LITERIE_DIJON_CONTACT_NAMES = [
            "appels",
            "cta"
        ]
        
        self.FRANCE_LITERIE_DIJON_DIRECTIONS_NAMES = [
            "itinéraires magasin",
        ]
        
        self.FRANCE_LITERIE_NARBONNE_CONTACT_NAMES = [
            "appels",
            "clicks to call"
        ]
        
        self.FRANCE_LITERIE_NARBONNE_DIRECTIONS_NAMES = [
            "itinéraires",
            "local actions - directions",
            "itinéraires magasin"
        ]
        
        self.FRANCE_LITERIE_PERPIGNAN_CONTACT_NAMES = [
            "appels",
            "clicks to call"
        ]
        
        self.FRANCE_LITERIE_PERPIGNAN_DIRECTIONS_NAMES = [
            "itinéraires",
            "local actions - directions"
        ]
        
        self.KALTEA_AUBAGNE_CONTACT_NAMES = [
            "appels directs",
            "appels directs via google maps pour une campagne intelligente",
            "appels directs via l'annonce d'une campagne intelligente",
            "appels",
            "profil de l'établissement - appel"
        ]
        
        self.KALTEA_AUBAGNE_DIRECTIONS_NAMES = [
            "itinéraires",
            "itinéraires magasin",
            "itinéraires google maps d'une campagne intelligente"
        ]
        
        self.KALTEA_CHALON_CONTACT_NAMES = [
            "clicks to call",
            "appels"
        ]
        
        self.KALTEA_CHALON_DIRECTIONS_NAMES = [
            "local actions - directions",
            "itinéraires magasin"
        ]
        
        self.KALTEA_LYON_CONTACT_NAMES = [
            "clicks to call",
            "appels"
        ]
        
        self.KALTEA_LYON_DIRECTIONS_NAMES = [
            "local actions - directions",
            "itinéraire"
        ]
        
        self.LASEREL_CONTACT_NAMES = [
            "appels",
            "clicks to call",
            "appel (cta)",
            "cta"
        ]
        
        self.LASEREL_DIRECTIONS_NAMES = [
            "actions locales – itinéraire"
        ]
        
        self.LASEREL_AUXERRE_CONTACT_NAMES = [
            "whatsapp"
        ]
        
        self.BEDROOM_CONTACT_NAMES = [
            "call bouton",
            "clicks to call"
        ]

        self.EMMA_PERPIGNAN_CONTACT_NAMES = [
            "call bouton",
            "clicks to call",
            "email"
        ]

        self.EMMA_PERPIGNAN_DIRECTIONS_NAMES = [
            "itinéraires",
            "local actions - directions"
        ]

        self.EMMA_VENDENHEIM_CONTACT_NAMES = [
            "call bouton",
            "clicks to call"
        ]

        self.EMMA_VENDENHEIM_DIRECTIONS_NAMES = [
            "itinéraires",
            "local actions - directions"
        ]

        self.BEDROOM_DIRECTIONS_NAMES = [
            "itinéraires",
            "local actions - directions"
        ]
        
        self.CROZATIER_CONTACT_NAMES = [
            "appels",
            "clicks to call"
        ]
        
        self.CROZATIER_DIRECTIONS_NAMES = [
            "itinéraires",
            "local actions - directions"
        ]
        
        self.EMMA_MERIGNAC_CONTACT_NAMES = [
            "clicks to call",
            "call bouton"
        ]
        
        self.EMMA_MERIGNAC_DIRECTIONS_NAMES = [
            "actions locales – itinéraire",
            "itinéraires"
        ]

        self.EMMA_VENDENHEIM_DIRECTIONS_NAMES = [
            "itinéraires",
            "local actions - directions"
        ]
        
        self.STAR_LITERIE_CONTACT_NAMES = [
            "appels",
            "clicks to call",
            "cta"
        ]
        
        self.STAR_LITERIE_DIRECTIONS_NAMES = [
            "itinéraires",
            "local actions - directions",
            "itinéraires magasin"
        ]
        
        self.TOUSALON_PERPIGNAN_CONTACT_NAMES = [
            "appels"
        ]
        
        self.TOUSALON_PERPIGNAN_DIRECTIONS_NAMES = [
            "local actions - directions"
        ]
        
        self.TOUSALON_TOULOUSE_CONTACT_NAMES = [
            "appels",
            "clicks to call"
        ]
        
        self.TOUSALON_TOULOUSE_DIRECTIONS_NAMES = [
            "itinéraire",
            "local actions - directions"
        ]
        
        self.CUISINE_PLUS_PERPIGNAN_CONTACT_NAMES = [
            # Pas de conversions contact pour Cuisine Plus Perpignan
        ]
        
        self.CUISINE_PLUS_PERPIGNAN_DIRECTIONS_NAMES = [
            "itinéraires"
        ]
        
        self.FLAMME_CREATION_CONTACT_NAMES = [
            "appels",
            "clicks to call"
        ]
        
        self.FLAMME_CREATION_DIRECTIONS_NAMES = [
            "itinéraires",
            "local actions - directions"
        ]
        
        self.FL_CHAMPAGNE_CONTACT_NAMES = [
            "appels"
        ]
        
        self.FL_CHAMPAGNE_DIRECTIONS_NAMES = [
            "itinéraires"
        ]
        
        self.SAINT_PRIEST_GIVORS_CONTACT_NAMES = [
            "appel givors",
            "appel st priest",
            "appels",
            "clicks to call",
            "cta"
        ]
        
        self.SAINT_PRIEST_GIVORS_DIRECTIONS_NAMES = [
            "itinéraire saint priest",
            "itinéraire givors",
            "local actions - directions"
        ]
        
        self.FL_ANTIBES_CONTACT_NAMES = [
            "appels",
            "clicks to call",
            "cta"
        ]
        
        self.FL_ANTIBES_DIRECTIONS_NAMES = [
            "itinéraires",
            "local actions - directions"
        ]
        
        self.MEUBLE_RIGAUD_CONTACT_NAMES = [
            "appels",
            "clicks to call"
        ]
        
        self.MEUBLE_RIGAUD_DIRECTIONS_NAMES = [
            "itinéraires",
            "local actions - directions"
        ]
        
        self.MY_SALON_AUBIERE_CONTACT_NAMES = [
            "appels",
            "clicks to call"
        ]
        
        self.MY_SALON_AUBIERE_DIRECTIONS_NAMES = [
            "itinéraires",
            "local actions - directions"
        ]
        
        # Riviera Grass: uniquement Click Whatsapp, Click Tel, Click Email pour les contacts
        self.RIVIERA_GRASS_CONTACT_NAMES = [
            "click whatsapp",
            "click tel",
            "click email"
        ]
        
        # Emma Nantes: Clicks to call, Appels à partir des annonces (Calls from ads), Call bouton
        self.EMMA_NANTES_CONTACT_NAMES = [
            "clicks to call",
            "calls from ads",
            "call bouton"
        ]
        
        self.EMMA_NANTES_DIRECTIONS_NAMES = [
            "itinéraires",
            "local actions - directions"
        ]
        
        # Tairmic: Appels pour contacts, Itinéraires Magasin pour itinéraires
        self.TAIRMIC_CONTACT_NAMES = [
            "appels"
        ]
        
        self.TAIRMIC_DIRECTIONS_NAMES = [
            "itinéraires magasin"
        ]
        
        # Univers Construction: Appels Directs, Click Email, Click Tel / Actions locales – Itinéraire, Click Adresse
        self.UNIVERS_CONSTRUCTION_CONTACT_NAMES = [
            "appels directs",
            "click email",
            "click tel"
        ]
        
        self.UNIVERS_CONSTRUCTION_DIRECTIONS_NAMES = [
            "actions locales – itinéraire",
            "actions locales - itinéraire",
            "actions locales - itineraire",
            "click adresse"
        ]
        
        # Clients qui nécessitent une protection timeout
        self.TIMEOUT_PROTECTED_CLIENTS = [
            "5901565913",  # Laserel
            # Ajoutez d'autres client_ids ici si nécessaire
        ]
    
    def _apply_timeout_protection(self, customer_id: str, timeout_seconds: int = 60):
        """
        Applique une protection timeout pour les clients qui en ont besoin
        """
        if customer_id in self.TIMEOUT_PROTECTED_CLIENTS:
            import threading
            
            self.timeout_occurred = threading.Event()
            
            def timeout_handler():
                self.timeout_occurred.set()
            
            self.timeout_timer = threading.Timer(timeout_seconds, timeout_handler)
            self.timeout_timer.start()
            return True
        return False
    
    def _clear_timeout_protection(self):
        """
        Annule la protection timeout
        """
        if hasattr(self, 'timeout_timer'):
            self.timeout_timer.cancel()
    
    def get_all_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, int, List[Dict]]:
        """
        Récupère TOUTES les conversions et les sépare en Contact et Itinéraires
        
        Args:
            customer_id: ID du client Google Ads
            start_date: Date de début (YYYY-MM-DD)
            end_date: Date de fin (YYYY-MM-DD)
            
        Returns:
            Tuple (contact_total, directions_total, all_conversions)
        """
        contact_total = 0
        directions_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            # ✅ CORRECTION: response contient directement les GoogleAdsRow
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                # Logique pour gérer la différence entre les métriques
                # Si conversions a une valeur, l'utiliser
                # Sinon, utiliser all_conversions MAIS seulement si la différence n'est pas trop importante
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    # Utiliser all_conversions seulement si conversions est 0
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                
                # Vérifier si c'est A.G. Cryolipolyse (customer_id: 9321943301)
                is_cryolipolyse = customer_id == "9321943301"
                # Vérifier si c'est Addario (customer_id: 1513412386)
                is_addario = customer_id == "1513412386"
                # Vérifier si c'est Crozatier Dijon (customer_id: 3259500758)
                is_crozatier = customer_id == "3259500758"
                # Vérifier si c'est Denteva (customer_id: 1810240249)
                is_denteva = customer_id == "1810240249"
                # Vérifier si c'est EvoPro (customer_id: 5461114350)
                is_evopro = customer_id == "5461114350"
                # Vérifier si c'est France Literie Aix (customer_id: 5104651305)
                is_france_literie_aix = customer_id == "5104651305"
                # Vérifier si c'est France Literie Annemasse (customer_id: 2744128994)
                is_france_literie_annemasse = customer_id == "2744128994"
                # Vérifier si c'est FL Antibes Vallauris (customer_id: 2485486745)
                is_fl_antibes = customer_id == "2485486745"
                # Vérifier si c'est Cuisine Plus Perpignan (customer_id: 9360801546)
                is_cuisine_plus_perpignan = customer_id == "9360801546"
                # Vérifier si c'est Riviera Grass (customer_id: 5184726119)
                is_riviera_grass = customer_id == "5184726119"
                # Vérifier si c'est Emma Nantes (customer_id: 9686568792)
                is_emma_nantes = customer_id == "9686568792"
                # Vérifier si c'est Tairmic (customer_id: 2206388196)
                is_tairmic = customer_id == "2206388196"
                # Vérifier si c'est Univers Construction (customer_id: 5509129108)
                is_univers_construction = customer_id == "5509129108"
                
                # Normalisation spécifique pour gérer les espaces insécables
                # Normalisation spécifique pour gérer les espaces insécables et différents tirets
                normalized_conversion_name = conversion_name.replace('\xa0', ' ').replace('–', '-').replace('—', '-')
                                
                # Classifier par section basée sur le nom
                if is_cryolipolyse:
                    is_contact = any(target_name in conversion_name for target_name in self.CRYOLIPOLYSE_CONTACT_NAMES)
                    is_directions = any(target_name in conversion_name for target_name in self.TARGET_DIRECTIONS_NAMES)
                    if is_contact:
                        contact_total += conversions_value
                    if is_directions:
                        directions_total += conversions_value
                elif is_addario:
                    # Logique spécifique Addario: seulement "appels" et "cta"
                    is_contact = any(target_name in conversion_name for target_name in self.ADDARIO_CONTACT_NAMES)
                    is_directions = any(target_name in conversion_name for target_name in self.ADDARIO_DIRECTIONS_NAMES)
                    if is_contact:
                        contact_total += conversions_value
                        logging.info(f"✅ Conversion Contact: {row.segments.conversion_action_name} = {conversions_value}")
                    elif is_directions:
                        directions_total += conversions_value
                        logging.info(f"✅ Conversion Itinéraires: {row.segments.conversion_action_name} = {conversions_value}")
                    else:
                        logging.info(f"Conversion non classifiée: {row.segments.conversion_action_name} = {conversions_value}")
                    continue  # Éviter le double comptage
                elif is_crozatier:
                    is_contact = any(target_name in conversion_name for target_name in self.CROZATIER_CONTACT_NAMES)
                    is_directions = any(target_name in conversion_name for target_name in self.TARGET_DIRECTIONS_NAMES)
                    if is_contact:
                        contact_total += conversions_value
                    if is_directions:
                        directions_total += conversions_value
                elif is_denteva:
                    is_contact = any(target_name in conversion_name for target_name in self.DENTEVA_CONTACT_NAMES)
                    is_directions = any(target_name in conversion_name for target_name in self.DENTEVA_DIRECTIONS_NAMES)
                    if is_contact:
                        contact_total += conversions_value
                    if is_directions:
                        directions_total += conversions_value
                elif is_evopro:
                    is_contact = any(target_name in conversion_name for target_name in self.EVOPRO_CONTACT_NAMES)
                    is_directions = any(target_name in conversion_name for target_name in self.EVOPRO_DIRECTIONS_NAMES)
                    if is_contact:
                        contact_total += conversions_value
                    if is_directions:
                        directions_total += conversions_value
                elif is_france_literie_aix:
                    is_contact = any(target_name in conversion_name for target_name in self.FRANCE_LITERIE_AIX_CONTACT_NAMES)
                    is_directions = any(target_name in conversion_name for target_name in self.FRANCE_LITERIE_AIX_DIRECTIONS_NAMES)
                    if is_contact:
                        logging.info(f"🛏️ CONVERSION FRANCE LITERIE AIX CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                    if is_directions:
                        logging.info(f"🛏️ CONVERSION FRANCE LITERIE AIX ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                elif is_france_literie_annemasse:
                    is_contact = any(target_name in conversion_name for target_name in self.FRANCE_LITERIE_ANNEMASSE_CONTACT_NAMES)
                    is_directions = any(target_name in conversion_name for target_name in self.FRANCE_LITERIE_ANNEMASSE_DIRECTIONS_NAMES)
                    if is_contact:
                        logging.info(f"🏔️ CONVERSION FRANCE LITERIE ANNEMASSE CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                    if is_directions:
                        logging.info(f"🏔️ CONVERSION FRANCE LITERIE ANNEMASSE ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                elif is_fl_antibes:
                    is_contact = any(target_name in conversion_name for target_name in self.FL_ANTIBES_CONTACT_NAMES)
                    is_directions = any(target_name in conversion_name for target_name in self.FL_ANTIBES_DIRECTIONS_NAMES)
                    if is_contact:
                        logging.info(f"🏖️ CONVERSION FL ANTIBES CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                    if is_directions:
                        logging.info(f"🏖️ CONVERSION FL ANTIBES ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                elif is_cuisine_plus_perpignan:
                    # Logique spécifique Cuisine Plus Perpignan: rien en contact, seulement "itinéraires"
                    is_contact = any(target_name in conversion_name for target_name in self.CUISINE_PLUS_PERPIGNAN_CONTACT_NAMES)
                    is_directions = any(target_name in conversion_name for target_name in self.CUISINE_PLUS_PERPIGNAN_DIRECTIONS_NAMES)
                    if is_contact:
                        contact_total += conversions_value
                        logging.info(f"🍽️ Conversion Contact: {row.segments.conversion_action_name} = {conversions_value}")
                    elif is_directions:
                        directions_total += conversions_value
                        logging.info(f"🍽️ Conversion Itinéraires: {row.segments.conversion_action_name} = {conversions_value}")
                    else:
                        logging.info(f"Conversion non classifiée: {row.segments.conversion_action_name} = {conversions_value}")
                    continue  # Éviter le double comptage
                elif is_riviera_grass:
                    # Logique spécifique Riviera Grass: Click Whatsapp, Click Tel, Click Email avec correspondance exacte
                    is_contact = any(conversion_name == target_name for target_name in self.RIVIERA_GRASS_CONTACT_NAMES)
                    is_directions = False  # Pas d'itinéraires pour Riviera Grass
                    if is_contact:
                        contact_total += conversions_value
                        logging.info(f"🌱 CONVERSION RIVIERA GRASS CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                    else:
                        logging.info(f"Conversion non classifiée: {row.segments.conversion_action_name} = {conversions_value}")
                    continue  # Éviter le double comptage
                elif is_emma_nantes:
                    # Logique spécifique Emma Nantes: Clicks to call, Calls from ads, Call bouton / Itinéraires, Local actions - Directions
                    is_contact = any(conversion_name == target_name for target_name in self.EMMA_NANTES_CONTACT_NAMES)
                    is_directions = any(conversion_name == target_name for target_name in self.EMMA_NANTES_DIRECTIONS_NAMES)
                    if is_contact:
                        contact_total += conversions_value
                        logging.info(f"🛋️ CONVERSION EMMA NANTES CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                    elif is_directions:
                        directions_total += conversions_value
                        logging.info(f"🛋️ CONVERSION EMMA NANTES ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                    else:
                        logging.info(f"Conversion non classifiée: {row.segments.conversion_action_name} = {conversions_value}")
                    continue  # Éviter le double comptage
                elif is_tairmic:
                    # Logique spécifique Tairmic: Appels / Itinéraires Magasin
                    is_contact = any(conversion_name == target_name for target_name in self.TAIRMIC_CONTACT_NAMES)
                    is_directions = any(conversion_name == target_name for target_name in self.TAIRMIC_DIRECTIONS_NAMES)
                    if is_contact:
                        contact_total += conversions_value
                        logging.info(f"🏪 CONVERSION TAIRMIC CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                    elif is_directions:
                        directions_total += conversions_value
                        logging.info(f"🏪 CONVERSION TAIRMIC ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                    else:
                        logging.info(f"Conversion non classifiée: {row.segments.conversion_action_name} = {conversions_value}")
                    continue  # Éviter le double comptage
                elif is_univers_construction:
                    # Logique spécifique Univers Construction avec nom normalisé
                    # Utilisation de 'in' au lieu de '==' pour être plus permissif sur les noms normailsés
                    is_contact = any(target_name in normalized_conversion_name for target_name in self.UNIVERS_CONSTRUCTION_CONTACT_NAMES)
                    is_directions = any(target_name in normalized_conversion_name for target_name in self.UNIVERS_CONSTRUCTION_DIRECTIONS_NAMES)
                    if is_contact:
                        contact_total += conversions_value
                        logging.info(f"🏗️ CONVERSION UNIVERS CONSTRUCTION CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                    elif is_directions:
                        directions_total += conversions_value
                        logging.info(f"🏗️ CONVERSION UNIVERS CONSTRUCTION ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                    else:
                        logging.info(f"Conversion non classifiée: {row.segments.conversion_action_name} = {conversions_value}")
                    continue  # Éviter le double comptage
                else:
                    # Logique standard pour tous les autres clients
                    is_contact = any(target_name in conversion_name for target_name in self.TARGET_CONTACT_NAMES)
                    is_directions = any(target_name in conversion_name for target_name in self.TARGET_DIRECTIONS_NAMES)
                
                if is_contact:
                    contact_total += conversions_value
                    logging.info(f"✅ Conversion Contact: {row.segments.conversion_action_name} = {conversions_value}")
                elif is_directions:
                    directions_total += conversions_value
                    logging.info(f"✅ Conversion Itinéraires: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    # Si aucune section n'est identifiée, essayer de deviner basé sur le contexte
                    logging.info(f"Conversion non classifiée: {row.segments.conversion_action_name} = {conversions_value}")
                    # Pour l'instant, on ignore les conversions non classifiées
                    pass
            
            logging.info(f"📊 Total Contact: {contact_total}, Total Itinéraires: {directions_total}")
            return contact_total, directions_total, all_conversions
            
        except GoogleAdsException as ex:
            logging.error(f" GoogleAds API error pour {customer_id}: {ex.error.code().name}")
            for error in ex.failure.errors:
                logging.error(f"   - {error.message}")
            return contact_total, directions_total, all_conversions
        except Exception as e:
            logging.error(f"Erreur conversions {customer_id}: {e}")
            return contact_total, directions_total, all_conversions
    
    def get_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact (utilise la nouvelle méthode)
        """
        contact_total, directions_total, all_conversions = self.get_all_conversions_data(
            customer_id, start_date, end_date
        )
        
        # Filtrer seulement les conversions Contact
        contact_conversions = [conv for conv in all_conversions 
                              if any(target_name in conv['name'].lower() for target_name in self.TARGET_CONTACT_NAMES)]
        
        return contact_total, contact_conversions
    
    def get_cryolipolyse_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour A.G. Cryolipolyse
        Uniquement les conversions contenant "Appels" et "CTA"
        """
        contact_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🧊 Recherche des conversions CRYOLIPOLYSE pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Contact pour Cryolipolyse (uniquement "Appels" et "CTA")
                is_cryolipolyse_contact = any(target_name in conversion_name for target_name in self.CRYOLIPOLYSE_CONTACT_NAMES)
                
                if is_cryolipolyse_contact:
                    contact_total += conversions_value
                    logging.info(f"🧊 CONVERSION CRYOLIPOLYSE CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Cryolipolyse ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Contact Cryolipolyse
            contact_conversions = [conv for conv in all_conversions 
                                  if any(target_name in conv['name'].lower() for target_name in self.CRYOLIPOLYSE_CONTACT_NAMES)]
            
            return contact_total, contact_conversions
            
        except Exception as e:
            logging.error(f"Erreur conversions Cryolipolyse {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_crozatier_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour Crozatier Dijon
        Uniquement les conversions contenant "Appels" et "Clicks to call"
        """
        contact_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🏪 Recherche des conversions CROZATIER CONTACT pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Contact pour Crozatier (uniquement "Appels" et "Clicks to call")
                is_crozatier_contact = any(target_name in conversion_name for target_name in self.CROZATIER_CONTACT_NAMES)
                
                if is_crozatier_contact:
                    contact_total += conversions_value
                    logging.info(f"🏪 CONVERSION CROZATIER CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Crozatier ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Contact Crozatier
            contact_conversions = [conv for conv in all_conversions 
                                  if any(target_name in conv['name'].lower() for target_name in self.CROZATIER_CONTACT_NAMES)]
            
            return contact_total, contact_conversions
            
        except Exception as e:
            logging.error(f"Erreur conversions Crozatier {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_denteva_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour Denteva
        Uniquement les conversions contenant "Action de conversion" et "Appels"
        """
        contact_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🦷 Recherche des conversions DENTEVA CONTACT pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Contact pour Denteva (uniquement "Action de conversion" et "Appels")
                is_denteva_contact = any(target_name in conversion_name for target_name in self.DENTEVA_CONTACT_NAMES)
                
                if is_denteva_contact:
                    contact_total += conversions_value
                    logging.info(f"🦷 CONVERSION DENTEVA CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Denteva Contact ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Contact Denteva
            contact_conversions = [conv for conv in all_conversions 
                                  if any(target_name in conv['name'].lower() for target_name in self.DENTEVA_CONTACT_NAMES)]
            
            return contact_total, contact_conversions
            
        except Exception as e:
            logging.error(f"Erreur conversions Denteva Contact {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_denteva_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour Denteva
        Uniquement les conversions contenant "Itinéraires", "Click Map" et "Local actions - Directions"
        """
        directions_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🦷 Recherche des conversions DENTEVA ITINÉRAIRES pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Itinéraires pour Denteva (uniquement "Itinéraires", "Click Map" et "Local actions - Directions")
                is_denteva_directions = any(target_name in conversion_name for target_name in self.DENTEVA_DIRECTIONS_NAMES)
                
                if is_denteva_directions:
                    directions_total += conversions_value
                    logging.info(f"🦷 CONVERSION DENTEVA ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Denteva Itinéraires ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Itinéraires Denteva
            directions_conversions = [conv for conv in all_conversions 
                                     if any(target_name in conv['name'].lower() for target_name in self.DENTEVA_DIRECTIONS_NAMES)]
            
            return directions_total, directions_conversions
            
        except Exception as e:
            logging.error(f"Erreur conversions Denteva Itinéraires {customer_id}: {e}")
            return directions_total, all_conversions
    
    def get_evopro_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour EvoPro
        Toutes les conversions Contact : "Action de conversion", "Appel (CTA)", "CTA", "Clicks to call", "Appels", "Appel (footer)"
        """
        contact_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"💻 Recherche des conversions EVOPRO CONTACT pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Contact pour EvoPro (toutes les conversions Contact)
                is_evopro_contact = any(target_name in conversion_name for target_name in self.EVOPRO_CONTACT_NAMES)
                
                if is_evopro_contact:
                    contact_total += conversions_value
                    logging.info(f"💻 CONVERSION EVOPRO CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion EvoPro Contact ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Contact EvoPro
            contact_conversions = [conv for conv in all_conversions 
                                  if any(target_name in conv['name'].lower() for target_name in self.EVOPRO_CONTACT_NAMES)]
            
            return contact_total, contact_conversions
            
        except Exception as e:
            logging.error(f"Erreur conversions EvoPro Contact {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_evopro_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour EvoPro
        Uniquement les conversions contenant "Itinéraires" et "Local actions - Directions"
        """
        directions_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"💻 Recherche des conversions EVOPRO ITINÉRAIRES pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Itinéraires pour EvoPro (uniquement "Itinéraires" et "Local actions - Directions")
                is_evopro_directions = any(target_name in conversion_name for target_name in self.EVOPRO_DIRECTIONS_NAMES)
                
                if is_evopro_directions:
                    directions_total += conversions_value
                    logging.info(f"💻 CONVERSION EVOPRO ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion EvoPro Itinéraires ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Itinéraires EvoPro
            directions_conversions = [conv for conv in all_conversions 
                                     if any(target_name in conv['name'].lower() for target_name in self.EVOPRO_DIRECTIONS_NAMES)]
            
            return directions_total, directions_conversions
            
        except Exception as e:
            logging.error(f"Erreur conversions EvoPro Itinéraires {customer_id}: {e}")
            return directions_total, all_conversions
    
    def get_france_literie_aix_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour France Literie Aix
        Uniquement les conversions contenant "Appels" et "CTA" (même logique que Cryolipolyse)
        """
        contact_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🛏️ Recherche des conversions FRANCE LITERIE AIX CONTACT pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Contact pour France Literie Aix (uniquement "Appels" et "CTA")
                is_france_literie_aix_contact = any(target_name in conversion_name for target_name in self.FRANCE_LITERIE_AIX_CONTACT_NAMES)
                
                if is_france_literie_aix_contact:
                    contact_total += conversions_value
                    logging.info(f"🛏️ CONVERSION FRANCE LITERIE AIX CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion France Literie Aix Contact ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Contact France Literie Aix
            contact_conversions = [conv for conv in all_conversions 
                                  if any(target_name in conv['name'].lower() for target_name in self.FRANCE_LITERIE_AIX_CONTACT_NAMES)]
            
            logging.info(f"🛏️ Total Contact France Literie Aix: {contact_total}")
            return contact_total, contact_conversions
            
        except Exception as e:
            logging.error(f"Erreur conversions France Literie Aix Contact {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_france_literie_aix_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour France Literie Aix
        Uniquement les conversions contenant "Itinéraires" et "Local actions - Directions"
        """
        directions_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🛏️ Recherche des conversions FRANCE LITERIE AIX ITINÉRAIRES pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Itinéraires pour France Literie Aix (uniquement "Itinéraires" et "Local actions - Directions")
                is_france_literie_aix_directions = any(target_name in conversion_name for target_name in self.FRANCE_LITERIE_AIX_DIRECTIONS_NAMES)
                
                if is_france_literie_aix_directions:
                    directions_total += conversions_value
                    logging.info(f"🛏️ CONVERSION FRANCE LITERIE AIX ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion France Literie Aix Itinéraires ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Itinéraires France Literie Aix
            directions_conversions = [conv for conv in all_conversions 
                                   if any(target_name in conv['name'].lower() for target_name in self.FRANCE_LITERIE_AIX_DIRECTIONS_NAMES)]
            
            logging.info(f"🛏️ Total Itinéraires France Literie Aix: {directions_total}")
            return directions_total, directions_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions France Literie Aix Itinéraires pour {customer_id}: {e}")
            return directions_total, all_conversions
    
    def get_france_literie_dijon_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour France Literie Dijon
        Uniquement les conversions contenant "Appels" et "CTA"
        """
        contact_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🏰 Recherche des conversions FRANCE LITERIE DIJON CONTACT pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Contact pour France Literie Dijon (uniquement "Appels" et "CTA")
                is_france_literie_dijon_contact = any(target_name in conversion_name for target_name in self.FRANCE_LITERIE_DIJON_CONTACT_NAMES)
                
                if is_france_literie_dijon_contact:
                    contact_total += conversions_value
                    logging.info(f"🏰 CONVERSION FRANCE LITERIE DIJON CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion France Literie Dijon Contact ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Contact France Literie Dijon
            contact_conversions = [conv for conv in all_conversions 
                                  if any(target_name in conv['name'].lower() for target_name in self.FRANCE_LITERIE_DIJON_CONTACT_NAMES)]
            
            logging.info(f"🏰 Total Contact France Literie Dijon: {contact_total}")
            return contact_total, contact_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions France Literie Dijon Contact pour {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_france_literie_dijon_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour France Literie Dijon
        Uniquement les conversions contenant "Itinéraires" et "Magasin"
        """
        directions_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🏰 Recherche des conversions FRANCE LITERIE DIJON ITINÉRAIRES pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Itinéraires pour France Literie Dijon (uniquement "Itinéraires" et "Magasin")
                is_france_literie_dijon_directions = any(target_name in conversion_name for target_name in self.FRANCE_LITERIE_DIJON_DIRECTIONS_NAMES)
                
                if is_france_literie_dijon_directions:
                    directions_total += conversions_value
                    logging.info(f"🏰 CONVERSION FRANCE LITERIE DIJON ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion France Literie Dijon Itinéraires ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Itinéraires France Literie Dijon
            directions_conversions = [conv for conv in all_conversions 
                                   if any(target_name in conv['name'].lower() for target_name in self.FRANCE_LITERIE_DIJON_DIRECTIONS_NAMES)]
            
            logging.info(f"🏰 Total Itinéraires France Literie Dijon: {directions_total}")
            return directions_total, directions_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions France Literie Dijon Itinéraires pour {customer_id}: {e}")
            return directions_total, all_conversions
    
    def get_france_literie_narbonne_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour France Literie Narbonne
        Uniquement les conversions contenant "Appels" et "CTA"
        """
        contact_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🏛️ Recherche des conversions FRANCE LITERIE NARBONNE CONTACT pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # 🏛️ LOGS DÉTAILLÉS FRANCE LITERIE NARBONNE - Debug complet (client qui fonctionne)
                logging.info(f"🏛️ FL NARBONNE DEBUG - Conversion trouvée: '{row.segments.conversion_action_name}'")
                logging.info(f"🏛️ FL NARBONNE DEBUG - metrics.conversions: {row.metrics.conversions}")
                logging.info(f"🏛️ FL NARBONNE DEBUG - metrics.all_conversions: {row.metrics.all_conversions}")
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                    logging.info(f"🏛️ FL NARBONNE DEBUG - Utilisation de metrics.conversions: {conversions_value}")
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                    logging.info(f"🏛️ FL NARBONNE DEBUG - Utilisation de metrics.all_conversions: {conversions_value}")
                else:
                    conversions_value = 0
                    logging.info(f"🏛️ FL NARBONNE DEBUG - Aucune conversion, valeur = 0")
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Contact pour France Literie Narbonne (uniquement "Appels" et "CTA")
                is_france_literie_narbonne_contact = any(target_name in conversion_name for target_name in self.FRANCE_LITERIE_NARBONNE_CONTACT_NAMES)
                
                # 🏛️ LOGS DÉTAILLÉS FRANCE LITERIE NARBONNE - Vérification des noms de conversions
                logging.info(f"🏛️ FL NARBONNE DEBUG - Noms recherchés: {self.FRANCE_LITERIE_NARBONNE_CONTACT_NAMES}")
                logging.info(f"🏛️ FL NARBONNE DEBUG - Nom de conversion: '{conversion_name}'")
                logging.info(f"🏛️ FL NARBONNE DEBUG - Match trouvé: {is_france_literie_narbonne_contact}")
                
                if is_france_literie_narbonne_contact:
                    contact_total += conversions_value
                    logging.info(f"🏛️ CONVERSION FRANCE LITERIE NARBONNE CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion France Literie Narbonne Contact ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Contact France Literie Narbonne
            contact_conversions = [conv for conv in all_conversions 
                                  if any(target_name in conv['name'].lower() for target_name in self.FRANCE_LITERIE_NARBONNE_CONTACT_NAMES)]
            
            logging.info(f"🏛️ Total Contact France Literie Narbonne: {contact_total}")
            logging.info(f"🏛️ FL NARBONNE RÉSUMÉ - Total final: {contact_total}")
            logging.info(f"🏛️ FL NARBONNE RÉSUMÉ - Conversions trouvées: {len(contact_conversions)}")
            for conv in contact_conversions:
                logging.info(f"🏛️ FL NARBONNE RÉSUMÉ - {conv['name']}: {conv['conversions']}")
            return contact_total, contact_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions France Literie Narbonne Contact pour {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_france_literie_narbonne_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour France Literie Narbonne
        Uniquement les conversions contenant "Itinéraires" et "Local actions - Directions"
        """
        directions_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🏛️ Recherche des conversions FRANCE LITERIE NARBONNE ITINÉRAIRES pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Itinéraires pour France Literie Narbonne (uniquement "Itinéraires" et "Local actions - Directions")
                is_france_literie_narbonne_directions = any(target_name in conversion_name for target_name in self.FRANCE_LITERIE_NARBONNE_DIRECTIONS_NAMES)
                
                if is_france_literie_narbonne_directions:
                    directions_total += conversions_value
                    logging.info(f"🏛️ CONVERSION FRANCE LITERIE NARBONNE ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion France Literie Narbonne Itinéraires ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Itinéraires France Literie Narbonne
            directions_conversions = [conv for conv in all_conversions 
                                   if any(target_name in conv['name'].lower() for target_name in self.FRANCE_LITERIE_NARBONNE_DIRECTIONS_NAMES)]
            
            logging.info(f"🏛️ Total Itinéraires France Literie Narbonne: {directions_total}")
            return directions_total, directions_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions France Literie Narbonne Itinéraires pour {customer_id}: {e}")
            return directions_total, all_conversions
    
    def get_france_literie_perpignan_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour France Literie Perpignan
        Uniquement les conversions contenant "Appels" et "Clicks to call"
        """
        contact_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🏰 Recherche des conversions FRANCE LITERIE PERPIGNAN CONTACT pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Contact pour France Literie Perpignan (uniquement "Appels" et "Clicks to call")
                is_france_literie_perpignan_contact = any(target_name in conversion_name for target_name in self.FRANCE_LITERIE_PERPIGNAN_CONTACT_NAMES)
                
                if is_france_literie_perpignan_contact:
                    contact_total += conversions_value
                    logging.info(f"🏰 CONVERSION FRANCE LITERIE PERPIGNAN CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion France Literie Perpignan Contact ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Contact France Literie Perpignan
            contact_conversions = [conv for conv in all_conversions 
                                  if any(target_name in conv['name'].lower() for target_name in self.FRANCE_LITERIE_PERPIGNAN_CONTACT_NAMES)]
            
            logging.info(f"🏰 Total Contact France Literie Perpignan: {contact_total}")
            return contact_total, contact_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions France Literie Perpignan Contact pour {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_france_literie_perpignan_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour France Literie Perpignan
        Uniquement les conversions contenant "Itinéraires" et "Local actions - Directions"
        """
        directions_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🏰 Recherche des conversions FRANCE LITERIE PERPIGNAN ITINÉRAIRES pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Itinéraires pour France Literie Perpignan (uniquement "Itinéraires" et "Local actions - Directions")
                is_france_literie_perpignan_directions = any(target_name in conversion_name for target_name in self.FRANCE_LITERIE_PERPIGNAN_DIRECTIONS_NAMES)
                
                if is_france_literie_perpignan_directions:
                    directions_total += conversions_value
                    logging.info(f"🏰 CONVERSION FRANCE LITERIE PERPIGNAN ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion France Literie Perpignan Itinéraires ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Itinéraires France Literie Perpignan
            directions_conversions = [conv for conv in all_conversions 
                                   if any(target_name in conv['name'].lower() for target_name in self.FRANCE_LITERIE_PERPIGNAN_DIRECTIONS_NAMES)]
            
            logging.info(f"🏰 Total Itinéraires France Literie Perpignan: {directions_total}")
            return directions_total, directions_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions France Literie Perpignan Itinéraires pour {customer_id}: {e}")
            return directions_total, all_conversions
    
    def get_kaltea_aubagne_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour Kaltea Aubagne
        Uniquement les conversions contenant les différents types d'appels
        """
        contact_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🌡️ Recherche des conversions KALTEA AUBAGNE CONTACT pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Contact pour Kaltea Aubagne
                is_kaltea_aubagne_contact = any(target_name in conversion_name for target_name in self.KALTEA_AUBAGNE_CONTACT_NAMES)
                
                if is_kaltea_aubagne_contact:
                    contact_total += conversions_value
                    logging.info(f"🌡️ CONVERSION KALTEA AUBAGNE CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Kaltea Aubagne Contact ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Contact Kaltea Aubagne
            contact_conversions = [conv for conv in all_conversions 
                                  if any(target_name in conv['name'].lower() for target_name in self.KALTEA_AUBAGNE_CONTACT_NAMES)]
            
            logging.info(f"🌡️ Total Contact Kaltea Aubagne: {contact_total}")
            return contact_total, contact_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Kaltea Aubagne Contact pour {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_kaltea_aubagne_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour Kaltea Aubagne
        Uniquement les conversions contenant les différents types d'itinéraires
        """
        directions_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🌡️ Recherche des conversions KALTEA AUBAGNE ITINÉRAIRES pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Itinéraires pour Kaltea Aubagne
                is_kaltea_aubagne_directions = any(target_name in conversion_name for target_name in self.KALTEA_AUBAGNE_DIRECTIONS_NAMES)
                
                if is_kaltea_aubagne_directions:
                    directions_total += conversions_value
                    logging.info(f"🌡️ CONVERSION KALTEA AUBAGNE ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Kaltea Aubagne Itinéraires ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Itinéraires Kaltea Aubagne
            directions_conversions = [conv for conv in all_conversions 
                                   if any(target_name in conv['name'].lower() for target_name in self.KALTEA_AUBAGNE_DIRECTIONS_NAMES)]
            
            logging.info(f"🌡️ Total Itinéraires Kaltea Aubagne: {directions_total}")
            return directions_total, directions_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Kaltea Aubagne Itinéraires pour {customer_id}: {e}")
            return directions_total, all_conversions
    
    def get_kaltea_chalon_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour Kaltea Chalon
        Uniquement les conversions contenant "Clicks to call" et "Appels"
        """
        contact_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🌡️ Recherche des conversions KALTEA CHALON CONTACT pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Contact pour Kaltea Chalon
                is_kaltea_chalon_contact = any(target_name in conversion_name for target_name in self.KALTEA_CHALON_CONTACT_NAMES)
                
                if is_kaltea_chalon_contact:
                    contact_total += conversions_value
                    logging.info(f"🌡️ CONVERSION KALTEA CHALON CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Kaltea Chalon Contact ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Contact Kaltea Chalon
            contact_conversions = [conv for conv in all_conversions 
                                  if any(target_name in conv['name'].lower() for target_name in self.KALTEA_CHALON_CONTACT_NAMES)]
            
            logging.info(f"🌡️ Total Contact Kaltea Chalon: {contact_total}")
            return contact_total, contact_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Kaltea Chalon Contact pour {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_kaltea_chalon_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour Kaltea Chalon
        Uniquement les conversions contenant "Local actions - Directions" et "Itinéraires Magasin"
        """
        directions_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🌡️ Recherche des conversions KALTEA CHALON ITINÉRAIRES pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Itinéraires pour Kaltea Chalon
                is_kaltea_chalon_directions = any(target_name in conversion_name for target_name in self.KALTEA_CHALON_DIRECTIONS_NAMES)
                
                if is_kaltea_chalon_directions:
                    directions_total += conversions_value
                    logging.info(f"🌡️ CONVERSION KALTEA CHALON ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Kaltea Chalon Itinéraires ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Itinéraires Kaltea Chalon
            directions_conversions = [conv for conv in all_conversions 
                                   if any(target_name in conv['name'].lower() for target_name in self.KALTEA_CHALON_DIRECTIONS_NAMES)]
            
            logging.info(f"🌡️ Total Itinéraires Kaltea Chalon: {directions_total}")
            return directions_total, directions_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Kaltea Chalon Itinéraires pour {customer_id}: {e}")
            return directions_total, all_conversions
    
    def get_kaltea_lyon_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour Kaltea Lyon
        Uniquement les conversions contenant "Clicks to call" et "Appels"
        """
        contact_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🌡️ Recherche des conversions KALTEA LYON CONTACT pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Contact pour Kaltea Lyon
                is_kaltea_lyon_contact = any(target_name in conversion_name for target_name in self.KALTEA_LYON_CONTACT_NAMES)
                
                if is_kaltea_lyon_contact:
                    contact_total += conversions_value
                    logging.info(f"🌡️ CONVERSION KALTEA LYON CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Kaltea Lyon Contact ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Contact Kaltea Lyon
            contact_conversions = [conv for conv in all_conversions 
                                  if any(target_name in conv['name'].lower() for target_name in self.KALTEA_LYON_CONTACT_NAMES)]
            
            logging.info(f"🌡️ Total Contact Kaltea Lyon: {contact_total}")
            return contact_total, contact_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Kaltea Lyon Contact pour {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_kaltea_lyon_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour Kaltea Lyon
        Uniquement les conversions contenant "Local actions - Directions" et "Itinéraire"
        """
        directions_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🌡️ Recherche des conversions KALTEA LYON ITINÉRAIRES pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Itinéraires pour Kaltea Lyon
                is_kaltea_lyon_directions = any(target_name in conversion_name for target_name in self.KALTEA_LYON_DIRECTIONS_NAMES)
                
                if is_kaltea_lyon_directions:
                    directions_total += conversions_value
                    logging.info(f"🌡️ CONVERSION KALTEA LYON ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Kaltea Lyon Itinéraires ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Itinéraires Kaltea Lyon
            directions_conversions = [conv for conv in all_conversions 
                                   if any(target_name in conv['name'].lower() for target_name in self.KALTEA_LYON_DIRECTIONS_NAMES)]
            
            logging.info(f"🌡️ Total Itinéraires Kaltea Lyon: {directions_total}")
            return directions_total, directions_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Kaltea Lyon Itinéraires pour {customer_id}: {e}")
            return directions_total, all_conversions
    
    def get_laserel_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour Laserel
        Uniquement les conversions contenant "Appels", "Clicks to call", "Appel (CTA)", "CTA"
        """
        contact_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🔬 Recherche des conversions LASEREL CONTACT pour le client {customer_id}")
            
            # Ajouter un timeout pour éviter les problèmes de mémoire
            import threading
            
            timeout_occurred = threading.Event()
            
            def timeout_handler():
                timeout_occurred.set()
            
            # Timeout de 30 secondes
            timeout_timer = threading.Timer(30.0, timeout_handler)
            timeout_timer.start()
            
            try:
                response = self.auth_service.fetch_report_data(customer_id, query)
                timeout_timer.cancel()  # Annuler le timeout
            except Exception as e:
                timeout_timer.cancel()  # Annuler le timeout
                if timeout_occurred.is_set():
                    logging.error(f"⏰ Timeout lors de la requête Laserel Contact pour {customer_id}")
                    return 0, []
                else:
                    raise e
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Contact pour Laserel
                # Utiliser une correspondance EXACTE pour éviter de matcher [TARMAAC] Click CTA
                is_laserel_contact = any(conversion_name == target_name for target_name in self.LASEREL_CONTACT_NAMES)
                
                if is_laserel_contact:
                    contact_total += conversions_value
                    logging.info(f"🔬 CONVERSION LASEREL CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Laserel Contact ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Contact Laserel
            contact_conversions = [conv for conv in all_conversions 
                                   if any(conv['name'].lower() == target_name for target_name in self.LASEREL_CONTACT_NAMES)]
            
            logging.info(f"🔬 Total Contact Laserel: {contact_total}")
            return contact_total, contact_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Laserel Contact pour {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_laserel_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour Laserel
        Uniquement les conversions contenant "Actions locales – Itinéraire"
        """
        directions_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🔬 Recherche des conversions LASEREL ITINÉRAIRES pour le client {customer_id}")
            
            # Ajouter un timeout pour éviter les problèmes de mémoire
            import threading
            
            timeout_occurred = threading.Event()
            
            def timeout_handler():
                timeout_occurred.set()
            
            # Timeout de 30 secondes
            timeout_timer = threading.Timer(30.0, timeout_handler)
            timeout_timer.start()
            
            try:
                response = self.auth_service.fetch_report_data(customer_id, query)
                timeout_timer.cancel()  # Annuler le timeout
            except Exception as e:
                timeout_timer.cancel()  # Annuler le timeout
                if timeout_occurred.is_set():
                    logging.error(f"⏰ Timeout lors de la requête Laserel Itinéraires pour {customer_id}")
                    return 0, []
                else:
                    raise e
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Itinéraires pour Laserel
                is_laserel_directions = any(target_name in conversion_name for target_name in self.LASEREL_DIRECTIONS_NAMES)
                
                if is_laserel_directions:
                    directions_total += conversions_value
                else:
                    logging.info(f"Conversion Laserel Itinéraires ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Itinéraires Laserel
            directions_conversions = [conv for conv in all_conversions 
                                   if any(target_name in conv['name'].lower() for target_name in self.LASEREL_DIRECTIONS_NAMES)]
            
            return directions_total, directions_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Laserel Itinéraires pour {customer_id}: {e}")
            return directions_total, all_conversions
    
    def get_laserel_auxerre_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère TOUTES les données de conversions Contact pour Laserel Auxerre
        """
        contact_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🔬 Recherche de TOUTES les conversions LASEREL AUXERRE CONTACT pour le client {customer_id}")
            
            # Ajouter un timeout pour éviter les problèmes de mémoire
            import threading
            
            timeout_occurred = threading.Event()
            
            def timeout_handler():
                timeout_occurred.set()
            
            # Timeout de 30 secondes
            timeout_timer = threading.Timer(30.0, timeout_handler)
            timeout_timer.start()
            
            try:
                response = self.auth_service.fetch_report_data(customer_id, query)
                timeout_timer.cancel()  # Annuler le timeout
            except Exception as e:
                timeout_timer.cancel()  # Annuler le timeout
                if timeout_occurred.is_set():
                    logging.error(f"⏰ Timeout lors de la requête Laserel Auxerre Contact pour {customer_id}")
                    return 0, []
                else:
                    raise e
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Log détaillé pour diagnostic
                logging.info(f"🔍 Conversion trouvée: '{row.segments.conversion_action_name}'")
                logging.info(f"🔍 - conversions: {row.metrics.conversions}")
                logging.info(f"🔍 - all_conversions: {row.metrics.all_conversions}")
                logging.info(f"🔍 - valeur utilisée: {conversions_value}")
                
                # Enregistrer toutes les conversions
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Whatsapp pour Laserel Auxerre
                is_whatsapp_conversion = "whatsapp" in conversion_name
                
                if is_whatsapp_conversion:
                    # Ajouter seulement les conversions Whatsapp au total
                    contact_total += conversions_value
                    logging.info(f"✅ Conversion Laserel Auxerre Contact ajoutée: {row.segments.conversion_action_name} = {conversions_value} (Total: {contact_total})")
                else:
                    logging.info(f"❌ Conversion Laserel Auxerre Contact ignorée (pas Whatsapp): {row.segments.conversion_action_name} = {conversions_value}")
            
            return contact_total, all_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Laserel Auxerre Contact pour {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_laserel_auxerre_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour Laserel Auxerre
        Retourne 0 car pas d'itinéraires pour Google
        """
        logging.info(f"🔬 LASEREL AUXERRE ITINÉRAIRES - Pas d'itinéraires pour Google : retourne 0")
        
        # Retourner 0 car pas d'itinéraires pour Google
        return 0, []
    
    def get_star_literie_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour Star Literie
        Uniquement les conversions contenant "Appels" et "Clicks to call"
        """
        contact_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"⭐ Recherche des conversions STAR LITERIE CONTACT pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Contact pour Star Literie
                is_star_literie_contact = any(target_name in conversion_name for target_name in self.STAR_LITERIE_CONTACT_NAMES)
                
                if is_star_literie_contact:
                    contact_total += conversions_value
                    logging.info(f"⭐ CONVERSION STAR LITERIE CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Star Literie Contact ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Contact Star Literie
            contact_conversions = [conv for conv in all_conversions 
                                  if any(target_name in conv['name'].lower() for target_name in self.STAR_LITERIE_CONTACT_NAMES)]
            
            logging.info(f"⭐ Total Contact Star Literie: {contact_total}")
            return contact_total, contact_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Star Literie Contact pour {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_star_literie_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour Star Literie
        Uniquement les conversions contenant "Itinéraires", "Local actions - Directions" et "Itinéraires Magasin"
        """
        directions_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"⭐ Recherche des conversions STAR LITERIE ITINÉRAIRES pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Itinéraires pour Star Literie
                is_star_literie_directions = any(target_name in conversion_name for target_name in self.STAR_LITERIE_DIRECTIONS_NAMES)
                
                if is_star_literie_directions:
                    directions_total += conversions_value
                    logging.info(f"⭐ CONVERSION STAR LITERIE ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Star Literie Itinéraires ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Itinéraires Star Literie
            directions_conversions = [conv for conv in all_conversions 
                                   if any(target_name in conv['name'].lower() for target_name in self.STAR_LITERIE_DIRECTIONS_NAMES)]
            
            logging.info(f"⭐ Total Itinéraires Star Literie: {directions_total}")
            return directions_total, directions_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Star Literie Itinéraires pour {customer_id}: {e}")
            return directions_total, all_conversions
    
    def get_tousalon_perpignan_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour Tousalon Perpignan
        Uniquement les conversions contenant "Appels"
        """
        contact_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"💇 Recherche des conversions TOUSALON PERPIGNAN CONTACT pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Contact pour Tousalon Perpignan
                is_tousalon_perpignan_contact = any(target_name in conversion_name for target_name in self.TOUSALON_PERPIGNAN_CONTACT_NAMES)
                
                if is_tousalon_perpignan_contact:
                    contact_total += conversions_value
                    logging.info(f"💇 CONVERSION TOUSALON PERPIGNAN CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Tousalon Perpignan Contact ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Contact Tousalon Perpignan
            contact_conversions = [conv for conv in all_conversions 
                                  if any(target_name in conv['name'].lower() for target_name in self.TOUSALON_PERPIGNAN_CONTACT_NAMES)]
            
            logging.info(f"💇 Total Contact Tousalon Perpignan: {contact_total}")
            return contact_total, contact_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Tousalon Perpignan Contact pour {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_tousalon_perpignan_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour Tousalon Perpignan
        Uniquement les conversions contenant "Local actions - Directions"
        """
        directions_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"💇 Recherche des conversions TOUSALON PERPIGNAN ITINÉRAIRES pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Itinéraires pour Tousalon Perpignan
                is_tousalon_perpignan_directions = any(target_name in conversion_name for target_name in self.TOUSALON_PERPIGNAN_DIRECTIONS_NAMES)
                
                if is_tousalon_perpignan_directions:
                    directions_total += conversions_value
                    logging.info(f"💇 CONVERSION TOUSALON PERPIGNAN ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Tousalon Perpignan Itinéraires ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Itinéraires Tousalon Perpignan
            directions_conversions = [conv for conv in all_conversions 
                                   if any(target_name in conv['name'].lower() for target_name in self.TOUSALON_PERPIGNAN_DIRECTIONS_NAMES)]
            
            logging.info(f"💇 Total Itinéraires Tousalon Perpignan: {directions_total}")
            return directions_total, directions_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Tousalon Perpignan Itinéraires pour {customer_id}: {e}")
            return directions_total, all_conversions
    
    def get_tousalon_toulouse_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour Tousalon Toulouse
        Uniquement les conversions contenant "Appels" et "Clicks to call"
        """
        contact_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🏛️ Recherche des conversions TOUSALON TOULOUSE CONTACT pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Contact pour Tousalon Toulouse
                is_tousalon_toulouse_contact = any(target_name in conversion_name for target_name in self.TOUSALON_TOULOUSE_CONTACT_NAMES)
                
                if is_tousalon_toulouse_contact:
                    contact_total += conversions_value
                    logging.info(f"🏛️ CONVERSION TOUSALON TOULOUSE CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Tousalon Toulouse Contact ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Contact Tousalon Toulouse
            contact_conversions = [conv for conv in all_conversions 
                                  if any(target_name in conv['name'].lower() for target_name in self.TOUSALON_TOULOUSE_CONTACT_NAMES)]
            
            logging.info(f"🏛️ Total Contact Tousalon Toulouse: {contact_total}")
            return contact_total, contact_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Tousalon Toulouse Contact pour {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_tousalon_toulouse_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour Tousalon Toulouse
        Uniquement les conversions contenant "Itinéraire" et "Local actions - Directions"
        """
        directions_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🏛️ Recherche des conversions TOUSALON TOULOUSE ITINÉRAIRES pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Itinéraires pour Tousalon Toulouse
                is_tousalon_toulouse_directions = any(target_name in conversion_name for target_name in self.TOUSALON_TOULOUSE_DIRECTIONS_NAMES)
                
                if is_tousalon_toulouse_directions:
                    directions_total += conversions_value
                    logging.info(f"🏛️ CONVERSION TOUSALON TOULOUSE ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Tousalon Toulouse Itinéraires ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Itinéraires Tousalon Toulouse
            directions_conversions = [conv for conv in all_conversions 
                                   if any(target_name in conv['name'].lower() for target_name in self.TOUSALON_TOULOUSE_DIRECTIONS_NAMES)]
            
            logging.info(f"🏛️ Total Itinéraires Tousalon Toulouse: {directions_total}")
            return directions_total, directions_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Tousalon Toulouse Itinéraires pour {customer_id}: {e}")
            return directions_total, all_conversions
    
    def get_bedroom_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour Bedroom
        Uniquement les conversions contenant "Call bouton" et "Clicks to call"
        """
        contact_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🛏️ Recherche des conversions BEDROOM CONTACT pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Contact pour Bedroom
                is_bedroom_contact = any(target_name in conversion_name for target_name in self.BEDROOM_CONTACT_NAMES)
                
                if is_bedroom_contact:
                    contact_total += conversions_value
                    logging.info(f"🛏️ CONVERSION BEDROOM CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Bedroom Contact ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Contact Bedroom
            contact_conversions = [conv for conv in all_conversions 
                                  if any(target_name in conv['name'].lower() for target_name in self.BEDROOM_CONTACT_NAMES)]
            
            logging.info(f"🛏️ Total Contact Bedroom: {contact_total}")
            return contact_total, contact_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Bedroom Contact pour {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_bedroom_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour Bedroom
        Uniquement les conversions contenant "Itinéraires" et "Local actions - Directions"
        """
        directions_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🛏️ Recherche des conversions BEDROOM ITINÉRAIRES pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Itinéraires pour Bedroom
                is_bedroom_directions = any(target_name in conversion_name for target_name in self.BEDROOM_DIRECTIONS_NAMES)
                
                if is_bedroom_directions:
                    directions_total += conversions_value
                    logging.info(f"🛏️ CONVERSION BEDROOM ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Bedroom Itinéraires ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Itinéraires Bedroom
            directions_conversions = [conv for conv in all_conversions 
                                   if any(target_name in conv['name'].lower() for target_name in self.BEDROOM_DIRECTIONS_NAMES)]
            
            logging.info(f"🛏️ Total Itinéraires Bedroom: {directions_total}")
            return directions_total, directions_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Bedroom Itinéraires pour {customer_id}: {e}")
            return directions_total, all_conversions

    def get_emma_perpignan_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour Emma Perpignan.
        Uniquement: 'Call bouton', 'Clicks to call', 'email' (substring match).
        """
        contact_total = 0
        all_conversions = []

        try:
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """

            logging.info(f"🌸 Recherche des conversions EMMA PERPIGNAN CONTACT pour {customer_id}")
            response = self.auth_service.fetch_report_data(customer_id, query)

            for row in response:
                conversion_name = (row.segments.conversion_action_name or "").lower().strip()

                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0

                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })

                is_match = any(target_name in conversion_name for target_name in self.EMMA_PERPIGNAN_CONTACT_NAMES)
                if is_match:
                    contact_total += conversions_value
                    logging.info(f"🌸 CONVERSION EMMA PERPIGNAN CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Emma Perpignan Contact ignorée: {row.segments.conversion_action_name} = {conversions_value}")

            contact_conversions = [conv for conv in all_conversions
                                   if any(target_name in conv['name'].lower() for target_name in self.EMMA_PERPIGNAN_CONTACT_NAMES)]
            logging.info(f"🌸 Total Contact Emma Perpignan: {contact_total}")
            return contact_total, contact_conversions

        except Exception as e:
            logging.error(f"Erreur Emma Perpignan Contact pour {customer_id}: {e}")
            return contact_total, all_conversions

    def get_emma_perpignan_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour Emma Perpignan.
        Uniquement: 'Itinéraires', 'Local actions - Directions'.
        """
        directions_total = 0
        all_conversions = []

        try:
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """

            logging.info(f"🌸 Recherche des conversions EMMA PERPIGNAN ITINÉRAIRES pour {customer_id}")
            response = self.auth_service.fetch_report_data(customer_id, query)

            for row in response:
                conversion_name = (row.segments.conversion_action_name or "").lower().strip()

                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0

                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })

                is_match = any(target_name in conversion_name for target_name in self.EMMA_PERPIGNAN_DIRECTIONS_NAMES)
                if is_match:
                    directions_total += conversions_value
                    logging.info(f"🌸 CONVERSION EMMA PERPIGNAN ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Emma Perpignan Itinéraires ignorée: {row.segments.conversion_action_name} = {conversions_value}")

            directions_conversions = [conv for conv in all_conversions
                                      if any(target_name in conv['name'].lower() for target_name in self.EMMA_PERPIGNAN_DIRECTIONS_NAMES)]
            logging.info(f"🌸 Total Itinéraires Emma Perpignan: {directions_total}")
            return directions_total, directions_conversions

        except Exception as e:
            logging.error(f"Erreur Emma Perpignan Itinéraires pour {customer_id}: {e}")
            return directions_total, all_conversions

    def get_emma_vendenheim_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour Emma Vendenheim.
        Uniquement: 'Call bouton', 'Clicks to call' (substring match).
        """
        contact_total = 0
        all_conversions = []

        try:
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """

            logging.info(f"🌷 Recherche des conversions EMMA VENDENHEIM CONTACT pour {customer_id}")
            response = self.auth_service.fetch_report_data(customer_id, query)

            for row in response:
                conversion_name = (row.segments.conversion_action_name or "").lower().strip()

                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0

                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })

                is_match = any(target_name in conversion_name for target_name in self.EMMA_VENDENHEIM_CONTACT_NAMES)
                if is_match:
                    contact_total += conversions_value
                    logging.info(f"🌷 CONVERSION EMMA VENDENHEIM CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Emma Vendenheim Contact ignorée: {row.segments.conversion_action_name} = {conversions_value}")

            contact_conversions = [conv for conv in all_conversions
                                   if any(target_name in conv['name'].lower() for target_name in self.EMMA_VENDENHEIM_CONTACT_NAMES)]
            logging.info(f"🌷 Total Contact Emma Vendenheim: {contact_total}")
            return contact_total, contact_conversions

        except Exception as e:
            logging.error(f"Erreur Emma Vendenheim Contact pour {customer_id}: {e}")
            return contact_total, all_conversions

    def get_emma_vendenheim_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour Emma Vendenheim.
        Uniquement: 'Itinéraires', 'Local actions - Directions'.
        """
        directions_total = 0
        all_conversions = []

        try:
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """

            logging.info(f"🌷 Recherche des conversions EMMA VENDENHEIM ITINÉRAIRES pour {customer_id}")
            response = self.auth_service.fetch_report_data(customer_id, query)

            for row in response:
                conversion_name = (row.segments.conversion_action_name or "").lower().strip()

                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0

                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })

                is_match = any(target_name in conversion_name for target_name in self.EMMA_VENDENHEIM_DIRECTIONS_NAMES)
                if is_match:
                    directions_total += conversions_value
                    logging.info(f"🌷 CONVERSION EMMA VENDENHEIM ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Emma Vendenheim Itinéraires ignorée: {row.segments.conversion_action_name} = {conversions_value}")

            directions_conversions = [conv for conv in all_conversions
                                      if any(target_name in conv['name'].lower() for target_name in self.EMMA_VENDENHEIM_DIRECTIONS_NAMES)]
            logging.info(f"🌷 Total Itinéraires Emma Vendenheim: {directions_total}")
            return directions_total, directions_conversions

        except Exception as e:
            logging.error(f"Erreur Emma Vendenheim Itinéraires pour {customer_id}: {e}")
            return directions_total, all_conversions

    def get_crozatier_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour Crozatier Dijon
        Uniquement les conversions contenant "Appels" et "Clicks to call"
        """
        contact_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🏪 Recherche des conversions CROZATIER CONTACT pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Contact pour Crozatier
                is_crozatier_contact = any(target_name in conversion_name for target_name in self.CROZATIER_CONTACT_NAMES)
                
                if is_crozatier_contact:
                    contact_total += conversions_value
                    logging.info(f"🏪 CONVERSION CROZATIER CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Crozatier Contact ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Contact Crozatier
            contact_conversions = [conv for conv in all_conversions 
                                  if any(target_name in conv['name'].lower() for target_name in self.CROZATIER_CONTACT_NAMES)]
            
            logging.info(f"🏪 Total Contact Crozatier: {contact_total}")
            return contact_total, contact_conversions
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de la récupération des conversions Crozatier Contact pour {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_crozatier_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour Crozatier Dijon
        Uniquement les conversions contenant "Itinéraires" et "Local actions - Directions"
        """
        directions_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🏪 Recherche des conversions CROZATIER ITINÉRAIRES pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Itinéraires pour Crozatier
                is_crozatier_directions = any(target_name in conversion_name for target_name in self.CROZATIER_DIRECTIONS_NAMES)
                
                if is_crozatier_directions:
                    directions_total += conversions_value
                    logging.info(f"🏪 CONVERSION CROZATIER ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Crozatier Itinéraires ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Itinéraires Crozatier
            directions_conversions = [conv for conv in all_conversions 
                                   if any(target_name in conv['name'].lower() for target_name in self.CROZATIER_DIRECTIONS_NAMES)]
            
            logging.info(f"🏪 Total Itinéraires Crozatier: {directions_total}")
            return directions_total, directions_conversions
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de la récupération des conversions Crozatier Itinéraires pour {customer_id}: {e}")
            return directions_total, all_conversions
    
    def get_cuisine_plus_perpignan_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour Cuisine Plus Perpignan
        PAS DE CONVERSIONS CONTACT pour ce client
        """
        contact_total = 0
        all_conversions = []
        
        try:
            logging.info(f"🍽️ Cuisine Plus Perpignan - PAS DE CONVERSIONS CONTACT pour le client {customer_id}")
            
            # Pas de conversions contact pour Cuisine Plus Perpignan
            logging.info(f"🍽️ Total Contact Cuisine Plus Perpignan: {contact_total} (aucune conversion contact)")
            return contact_total, all_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Cuisine Plus Perpignan Contact pour {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_cuisine_plus_perpignan_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour Cuisine Plus Perpignan
        Uniquement les conversions contenant "Itinéraires"
        """
        directions_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🍽️ Recherche des conversions CUISINE PLUS PERPIGNAN ITINÉRAIRES pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Itinéraires pour Cuisine Plus Perpignan
                is_cuisine_plus_perpignan_directions = any(target_name in conversion_name for target_name in self.CUISINE_PLUS_PERPIGNAN_DIRECTIONS_NAMES)
                
                if is_cuisine_plus_perpignan_directions:
                    directions_total += conversions_value
                    logging.info(f"🍽️ CONVERSION CUISINE PLUS PERPIGNAN ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Cuisine Plus Perpignan Itinéraires ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Itinéraires Cuisine Plus Perpignan
            directions_conversions = [conv for conv in all_conversions 
                                   if any(target_name in conv['name'].lower() for target_name in self.CUISINE_PLUS_PERPIGNAN_DIRECTIONS_NAMES)]
            
            logging.info(f"🍽️ Total Itinéraires Cuisine Plus Perpignan: {directions_total}")
            return directions_total, directions_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Cuisine Plus Perpignan Itinéraires pour {customer_id}: {e}")
            return directions_total, all_conversions
    
    def get_flamme_creation_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour Flamme&Creation
        Uniquement les conversions contenant "Appels" et "Clicks to call"
        """
        contact_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🔥 Recherche des conversions FLAMME&CREATION CONTACT pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Contact pour Flamme&Creation
                is_flamme_creation_contact = any(target_name in conversion_name for target_name in self.FLAMME_CREATION_CONTACT_NAMES)
                
                if is_flamme_creation_contact:
                    contact_total += conversions_value
                    logging.info(f"🔥 CONVERSION FLAMME&CREATION CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Flamme&Creation Contact ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Contact Flamme&Creation
            contact_conversions = [conv for conv in all_conversions 
                                  if any(target_name in conv['name'].lower() for target_name in self.FLAMME_CREATION_CONTACT_NAMES)]
            
            logging.info(f"🔥 Total Contact Flamme&Creation: {contact_total}")
            return contact_total, contact_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Flamme&Creation Contact pour {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_flamme_creation_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour Flamme&Creation
        Uniquement les conversions contenant "Itinéraires" et "Local actions - Directions"
        """
        directions_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🔥 Recherche des conversions FLAMME&CREATION ITINÉRAIRES pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Itinéraires pour Flamme&Creation
                is_flamme_creation_directions = any(target_name in conversion_name for target_name in self.FLAMME_CREATION_DIRECTIONS_NAMES)
                
                if is_flamme_creation_directions:
                    directions_total += conversions_value
                    logging.info(f"🔥 CONVERSION FLAMME&CREATION ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Flamme&Creation Itinéraires ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Itinéraires Flamme&Creation
            directions_conversions = [conv for conv in all_conversions 
                                   if any(target_name in conv['name'].lower() for target_name in self.FLAMME_CREATION_DIRECTIONS_NAMES)]
            
            logging.info(f"🔥 Total Itinéraires Flamme&Creation: {directions_total}")
            return directions_total, directions_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Flamme&Creation Itinéraires pour {customer_id}: {e}")
            return directions_total, all_conversions
    
    def get_fl_champagne_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour FL Champagne
        Uniquement les conversions contenant "Appels"
        """
        contact_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🍾 Recherche des conversions FL CHAMPAGNE CONTACT pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Contact pour FL Champagne
                is_fl_champagne_contact = any(target_name in conversion_name for target_name in self.FL_CHAMPAGNE_CONTACT_NAMES)
                
                if is_fl_champagne_contact:
                    contact_total += conversions_value
                    logging.info(f"🍾 CONVERSION FL CHAMPAGNE CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion FL Champagne Contact ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Contact FL Champagne
            contact_conversions = [conv for conv in all_conversions 
                                  if any(target_name in conv['name'].lower() for target_name in self.FL_CHAMPAGNE_CONTACT_NAMES)]
            
            logging.info(f"🍾 Total Contact FL Champagne: {contact_total}")
            return contact_total, contact_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions FL Champagne Contact pour {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_fl_champagne_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour FL Champagne
        Uniquement les conversions contenant "Itinéraires"
        """
        directions_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🍾 Recherche des conversions FL CHAMPAGNE ITINÉRAIRES pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Itinéraires pour FL Champagne
                is_fl_champagne_directions = any(target_name in conversion_name for target_name in self.FL_CHAMPAGNE_DIRECTIONS_NAMES)
                
                if is_fl_champagne_directions:
                    directions_total += conversions_value
                    logging.info(f"🍾 CONVERSION FL CHAMPAGNE ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion FL Champagne Itinéraires ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Itinéraires FL Champagne
            directions_conversions = [conv for conv in all_conversions 
                                   if any(target_name in conv['name'].lower() for target_name in self.FL_CHAMPAGNE_DIRECTIONS_NAMES)]
            
            logging.info(f"🍾 Total Itinéraires FL Champagne: {directions_total}")
            return directions_total, directions_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions FL Champagne Itinéraires pour {customer_id}: {e}")
            return directions_total, all_conversions
    
    def get_saint_priest_givors_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour Saint Priest Givors
        Uniquement les conversions contenant "Appel Givors", "Appel St Priest", "Appels", "Clicks to call" et "CTA"
        """
        contact_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🏰 Recherche des conversions SAINT PRIEST GIVORS CONTACT pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Contact pour Saint Priest Givors
                is_saint_priest_givors_contact = any(target_name in conversion_name for target_name in self.SAINT_PRIEST_GIVORS_CONTACT_NAMES)
                
                if is_saint_priest_givors_contact:
                    contact_total += conversions_value
                    logging.info(f"🏰 CONVERSION SAINT PRIEST GIVORS CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Saint Priest Givors Contact ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Contact Saint Priest Givors
            contact_conversions = [conv for conv in all_conversions 
                                  if any(target_name in conv['name'].lower() for target_name in self.SAINT_PRIEST_GIVORS_CONTACT_NAMES)]
            
            logging.info(f"🏰 Total Contact Saint Priest Givors: {contact_total}")
            return contact_total, contact_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Saint Priest Givors Contact pour {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_saint_priest_givors_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour Saint Priest Givors
        Uniquement les conversions contenant "Itinéraire Saint Priest", "Itinéraire Givors" et "Local actions - Directions"
        """
        directions_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🏰 Recherche des conversions SAINT PRIEST GIVORS ITINÉRAIRES pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Itinéraires pour Saint Priest Givors
                is_saint_priest_givors_directions = any(target_name in conversion_name for target_name in self.SAINT_PRIEST_GIVORS_DIRECTIONS_NAMES)
                
                if is_saint_priest_givors_directions:
                    directions_total += conversions_value
                    logging.info(f"🏰 CONVERSION SAINT PRIEST GIVORS ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Saint Priest Givors Itinéraires ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Itinéraires Saint Priest Givors
            directions_conversions = [conv for conv in all_conversions 
                                   if any(target_name in conv['name'].lower() for target_name in self.SAINT_PRIEST_GIVORS_DIRECTIONS_NAMES)]
            
            logging.info(f"🏰 Total Itinéraires Saint Priest Givors: {directions_total}")
            return directions_total, directions_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Saint Priest Givors Itinéraires pour {customer_id}: {e}")
            return directions_total, all_conversions
    
    def get_france_literie_annemasse_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour France Literie Annemasse
        Uniquement les conversions contenant "Appels" et "Clicks to call"
        """
        contact_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🏔️ Recherche des conversions FRANCE LITERIE ANNEMASSE CONTACT pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Contact pour France Literie Annemasse (uniquement "Appels" et "Clicks to call")
                is_france_literie_annemasse_contact = any(target_name in conversion_name for target_name in self.FRANCE_LITERIE_ANNEMASSE_CONTACT_NAMES)
                
                if is_france_literie_annemasse_contact:
                    contact_total += conversions_value
                    logging.info(f"🏔️ CONVERSION FRANCE LITERIE ANNEMASSE CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion France Literie Annemasse Contact ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Contact France Literie Annemasse
            contact_conversions = [conv for conv in all_conversions 
                                  if any(target_name in conv['name'].lower() for target_name in self.FRANCE_LITERIE_ANNEMASSE_CONTACT_NAMES)]
            
            logging.info(f"🏔️ Total Contact France Literie Annemasse: {contact_total}")
            return contact_total, contact_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions France Literie Annemasse Contact pour {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_france_literie_annemasse_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour France Literie Annemasse
        Uniquement les conversions contenant "Itinéraires" et "Local actions - Directions"
        """
        directions_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🏔️ Recherche des conversions FRANCE LITERIE ANNEMASSE ITINÉRAIRES pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Itinéraires pour France Literie Annemasse (uniquement "Itinéraires" et "Local actions - Directions")
                is_france_literie_annemasse_directions = any(target_name in conversion_name for target_name in self.FRANCE_LITERIE_ANNEMASSE_DIRECTIONS_NAMES)
                
                if is_france_literie_annemasse_directions:
                    directions_total += conversions_value
                    logging.info(f"🏔️ CONVERSION FRANCE LITERIE ANNEMASSE ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion France Literie Annemasse Itinéraires ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Itinéraires France Literie Annemasse
            directions_conversions = [conv for conv in all_conversions 
                                   if any(target_name in conv['name'].lower() for target_name in self.FRANCE_LITERIE_ANNEMASSE_DIRECTIONS_NAMES)]
            
            logging.info(f"🏔️ Total Itinéraires France Literie Annemasse: {directions_total}")
            return directions_total, directions_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions France Literie Annemasse Itinéraires pour {customer_id}: {e}")
            return directions_total, all_conversions
    
    def get_fl_antibes_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour FL Antibes Vallauris
        """
        contact_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🏖️ Recherche des conversions FL ANTIBES CONTACT pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # 🏖️ LOGS DÉTAILLÉS FL ANTIBES - Debug complet
                logging.info(f"🏖️ FL ANTIBES DEBUG - Conversion trouvée: '{row.segments.conversion_action_name}'")
                logging.info(f"🏖️ FL ANTIBES DEBUG - metrics.conversions: {row.metrics.conversions}")
                logging.info(f"🏖️ FL ANTIBES DEBUG - metrics.all_conversions: {row.metrics.all_conversions}")
                
                # Logique spécifique FL Antibes : utiliser UNIQUEMENT les conversions entières
                # Ignorer all_conversions pour éviter les conversions fractionnaires
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                    logging.info(f"🏖️ FL ANTIBES DEBUG - Utilisation de metrics.conversions: {conversions_value}")
                else:
                    conversions_value = 0
                    logging.info(f"🏖️ FL ANTIBES DEBUG - Aucune conversion entière, valeur = 0")
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Utiliser la logique spécifique FL Antibes avec correspondance précise pour "cta"
                is_fl_antibes_contact = False
                for target_name in self.FL_ANTIBES_CONTACT_NAMES:
                    if target_name == "cta":
                        # Pour "cta", correspondance exacte ou avec espaces uniquement
                        if conversion_name == "cta" or conversion_name.strip() == "cta":
                            is_fl_antibes_contact = True
                            break
                    else:
                        # Pour les autres, correspondance partielle
                        if target_name in conversion_name:
                            is_fl_antibes_contact = True
                            break
                
                # 🏖️ LOGS DÉTAILLÉS FL ANTIBES - Vérification des noms de conversions
                logging.info(f"🏖️ FL ANTIBES DEBUG - Noms recherchés: {self.FL_ANTIBES_CONTACT_NAMES}")
                logging.info(f"🏖️ FL ANTIBES DEBUG - Nom de conversion: '{conversion_name}'")
                logging.info(f"🏖️ FL ANTIBES DEBUG - Match trouvé: {is_fl_antibes_contact}")
                
                # Log spécial pour les conversions "cta"
                if "cta" in conversion_name.lower():
                    logging.info(f"🏖️ FL ANTIBES DEBUG - Conversion CTA détectée: '{conversion_name}' (valeur: {conversions_value})")
                    if conversion_name == "cta" or conversion_name.strip() == "cta":
                        logging.info(f"🏖️ FL ANTIBES DEBUG - ✅ CTA exacte acceptée")
                    else:
                        logging.info(f"🏖️ FL ANTIBES DEBUG -  CTA partielle rejetée (contient CTA mais n'est pas exacte)")
                
                if is_fl_antibes_contact:
                    contact_total += conversions_value
                    logging.info(f"🏖️ CONVERSION FL ANTIBES CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion FL Antibes Contact ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Contact FL Antibes (Appels, CTA, Clicks to call)
            contact_conversions = [conv for conv in all_conversions 
                                 if any(target_name in conv['name'].lower() for target_name in self.FL_ANTIBES_CONTACT_NAMES)]
            
            logging.info(f"🏖️ Total Contact FL Antibes: {contact_total}")
            logging.info(f"🏖️ FL ANTIBES RÉSUMÉ - Total final: {contact_total}")
            logging.info(f"🏖️ FL ANTIBES RÉSUMÉ - Conversions trouvées: {len(contact_conversions)}")
            for conv in contact_conversions:
                logging.info(f"🏖️ FL ANTIBES RÉSUMÉ - {conv['name']}: {conv['conversions']}")
            return contact_total, contact_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions FL Antibes Contact pour {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_fl_antibes_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour FL Antibes Vallauris
        Uniquement "Itinéraires" et "Local actions - Directions"
        """
        directions_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🏖️ Recherche des conversions FL ANTIBES ITINÉRAIRES pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Itinéraires pour FL Antibes (uniquement "Itinéraires" et "Local actions - Directions")
                is_fl_antibes_directions = any(target_name in conversion_name for target_name in self.FL_ANTIBES_DIRECTIONS_NAMES)
                
                if is_fl_antibes_directions:
                    directions_total += conversions_value
                    logging.info(f"🏖️ CONVERSION FL ANTIBES ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion FL Antibes Itinéraires ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Itinéraires FL Antibes
            directions_conversions = [conv for conv in all_conversions 
                                    if any(target_name in conv['name'].lower() for target_name in self.FL_ANTIBES_DIRECTIONS_NAMES)]
            
            logging.info(f"🏖️ Total Itinéraires FL Antibes: {directions_total}")
            return directions_total, directions_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions FL Antibes Itinéraires pour {customer_id}: {e}")
            return directions_total, all_conversions
    
    def get_emma_merignac_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour Emma Merignac
        Uniquement les conversions contenant "Clicks to call" et "Call bouton"
        """
        contact_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f" Recherche des conversions EMMA MERIGNAC CONTACT pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Contact pour Emma Merignac
                is_emma_merignac_contact = any(target_name in conversion_name for target_name in self.EMMA_MERIGNAC_CONTACT_NAMES)
                
                if is_emma_merignac_contact:
                    contact_total += conversions_value
                    logging.info(f" CONVERSION EMMA MERIGNAC CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Emma Merignac Contact ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Contact Emma Merignac
            contact_conversions = [conv for conv in all_conversions 
                                  if any(target_name in conv['name'].lower() for target_name in self.EMMA_MERIGNAC_CONTACT_NAMES)]
            
            logging.info(f" Total Contact Emma Merignac: {contact_total}")
            return contact_total, contact_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Emma Merignac Contact pour {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_meuble_rigaud_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour Meuble Rigaud
        Uniquement les conversions contenant "Appels" et "Clicks to call"
        """
        contact_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🪑 Recherche des conversions MEUBLE RIGAUD CONTACT pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Contact pour Meuble Rigaud (uniquement "Appels" et "Clicks to call")
                is_meuble_rigaud_contact = any(target_name in conversion_name for target_name in self.MEUBLE_RIGAUD_CONTACT_NAMES)
                
                if is_meuble_rigaud_contact:
                    contact_total += conversions_value
                    logging.info(f"🪑 CONVERSION MEUBLE RIGAUD CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Meuble Rigaud ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Contact Meuble Rigaud
            contact_conversions = [conv for conv in all_conversions 
                                  if any(target_name in conv['name'].lower() for target_name in self.MEUBLE_RIGAUD_CONTACT_NAMES)]
            
            logging.info(f" Total Contact Meuble Rigaud: {contact_total}")
            return contact_total, contact_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Meuble Rigaud Contact pour {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_meuble_rigaud_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour Meuble Rigaud
        Uniquement les conversions contenant "Itinéraires"
        """
        directions_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"🪑 Recherche des conversions MEUBLE RIGAUD ITINÉRAIRES pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Itinéraires pour Meuble Rigaud
                is_meuble_rigaud_directions = any(target_name in conversion_name for target_name in self.MEUBLE_RIGAUD_DIRECTIONS_NAMES)
                
                if is_meuble_rigaud_directions:
                    directions_total += conversions_value
                    logging.info(f"🪑 CONVERSION MEUBLE RIGAUD ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Meuble Rigaud Itinéraires ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Itinéraires Meuble Rigaud
            directions_conversions = [conv for conv in all_conversions 
                                  if any(target_name in conv['name'].lower() for target_name in self.MEUBLE_RIGAUD_DIRECTIONS_NAMES)]
            
            logging.info(f"🪑 Total Itinéraires Meuble Rigaud: {directions_total}")
            return directions_total, directions_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Meuble Rigaud Itinéraires pour {customer_id}: {e}")
            return directions_total, all_conversions
    
    def get_my_salon_aubiere_contact_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Contact spécifiquement pour My Salon Aubière
        Uniquement les conversions contenant "Appels" et "Clicks to call"
        """
        contact_total = 0
        all_conversions = []
        
        try:
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"💇 Recherche des conversions MY SALON AUBIÈRE CONTACT pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                is_my_salon_contact = any(target_name in conversion_name for target_name in self.MY_SALON_AUBIERE_CONTACT_NAMES)
                
                if is_my_salon_contact:
                    contact_total += conversions_value
                    logging.info(f"💇 CONVERSION MY SALON AUBIÈRE CONTACT: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion My Salon Aubière ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            contact_conversions = [conv for conv in all_conversions 
                                  if any(target_name in conv['name'].lower() for target_name in self.MY_SALON_AUBIERE_CONTACT_NAMES)]
            
            logging.info(f"💇 Total Contact My Salon Aubière: {contact_total}")
            return contact_total, contact_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions My Salon Aubière Contact pour {customer_id}: {e}")
            return contact_total, all_conversions
    
    def get_my_salon_aubiere_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour My Salon Aubière
        Uniquement les conversions contenant "Itinéraires" et "Local actions - Directions"
        """
        directions_total = 0
        all_conversions = []
        
        try:
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f"💇 Recherche des conversions MY SALON AUBIÈRE ITINÉRAIRES pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                is_my_salon_directions = any(target_name in conversion_name for target_name in self.MY_SALON_AUBIERE_DIRECTIONS_NAMES)
                
                if is_my_salon_directions:
                    directions_total += conversions_value
                    logging.info(f"💇 CONVERSION MY SALON AUBIÈRE ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion My Salon Aubière Itinéraires ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            directions_conversions = [conv for conv in all_conversions 
                                  if any(target_name in conv['name'].lower() for target_name in self.MY_SALON_AUBIERE_DIRECTIONS_NAMES)]
            
            logging.info(f"💇 Total Itinéraires My Salon Aubière: {directions_total}")
            return directions_total, directions_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions My Salon Aubière Itinéraires pour {customer_id}: {e}")
            return directions_total, all_conversions
    
    def get_emma_merignac_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour Emma Merignac
        Uniquement les conversions contenant "Actions locales – Itinéraire" et "Itinéraires"
        """
        directions_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
            """
            
            logging.info(f" Recherche des conversions EMMA MERIGNAC ITINÉRAIRES pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            # Log de debug pour voir TOUTES les conversions disponibles
            logging.info(f"🔍 DEBUG: Toutes les conversions disponibles pour Emma Merignac:")
            for row in response:
                logging.info(f"🔍 DEBUG: '{row.segments.conversion_action_name}' = {row.metrics.all_conversions if row.metrics.all_conversions else 0}")
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Log de debug pour voir toutes les conversions trouvées
                logging.info(f"🔍 DEBUG: Conversion trouvée: '{row.segments.conversion_action_name}' = {row.metrics.all_conversions if row.metrics.all_conversions else 0}")
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Itinéraires pour Emma Merignac
                is_emma_merignac_directions = any(target_name in conversion_name for target_name in self.EMMA_MERIGNAC_DIRECTIONS_NAMES)
                
                # Test spécifique pour "Actions locales – Itinéraire"
                if "actions locales" in conversion_name and "itinéraire" in conversion_name:
                    is_emma_merignac_directions = True
                    logging.info(f"🎯 FORCE MATCH: 'Actions locales – Itinéraire' détecté!")
                
                if is_emma_merignac_directions:
                    directions_total += conversions_value
                    logging.info(f"✅ CONVERSION EMMA MERIGNAC ITINÉRAIRES: '{row.segments.conversion_action_name}' = {conversions_value}")
                else:
                    logging.info(f"❌ Conversion Emma Merignac Itinéraires ignorée: '{row.segments.conversion_action_name}' = {conversions_value}")
            
            # Filtrer seulement les conversions Itinéraires Emma Merignac
            directions_conversions = [conv for conv in all_conversions 
                                     if any(target_name in conv['name'].lower() for target_name in self.EMMA_MERIGNAC_DIRECTIONS_NAMES)]
            
            logging.info(f" Total Itinéraires Emma Merignac: {directions_total}")
            return directions_total, directions_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Emma Merignac Itinéraires pour {customer_id}: {e}")
            return directions_total, all_conversions

    def get_emma_vendenheim_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires pour Emma Vendenheim.
        Conversions: "Itinéraires" + "Local actions - Directions"
        """
        directions_total = 0
        all_conversions = []

        try:
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
            """

            logging.info(f" Recherche des conversions EMMA VENDENHEIM ITINÉRAIRES pour le client {customer_id}")

            response = self.auth_service.fetch_report_data(customer_id, query)

            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()

                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0

                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })

                is_match = any(target_name in conversion_name for target_name in self.EMMA_VENDENHEIM_DIRECTIONS_NAMES)

                if is_match:
                    directions_total += conversions_value
                    logging.info(f"✅ CONVERSION EMMA VENDENHEIM ITINÉRAIRES: '{row.segments.conversion_action_name}' = {conversions_value}")

            logging.info(f" Total Itinéraires Emma Vendenheim: {directions_total}")
            return directions_total, [conv for conv in all_conversions
                                      if any(t in conv['name'].lower() for t in self.EMMA_VENDENHEIM_DIRECTIONS_NAMES)]

        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Emma Vendenheim Itinéraires pour {customer_id}: {e}")
            return directions_total, all_conversions
    
    def get_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires (utilise la nouvelle méthode)
        """
        contact_total, directions_total, all_conversions = self.get_all_conversions_data(
            customer_id, start_date, end_date
        )
        
        # Filtrer seulement les conversions Itinéraires
        directions_conversions = [conv for conv in all_conversions 
                                 if any(target_name in conv['name'].lower() for target_name in self.TARGET_DIRECTIONS_NAMES)]
        
        return directions_total, directions_conversions
    
    def get_addario_directions_conversions_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[int, List[Dict]]:
        """
        Récupère les données de conversions Itinéraires spécifiquement pour Addario
        Uniquement les conversions contenant "Itinéraires" et "Local actions - Directions"
        """
        directions_total = 0
        all_conversions = []
        
        try:
            # Requête pour récupérer TOUTES les conversion actions
            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """
            
            logging.info(f" Recherche des conversions ADDARIO ITINÉRAIRES pour le client {customer_id}")
            
            response = self.auth_service.fetch_report_data(customer_id, query)
            
            for row in response:
                conversion_name = row.segments.conversion_action_name.lower().strip()
                
                # Logique pour gérer la différence entre les métriques
                if row.metrics.conversions and row.metrics.conversions > 0:
                    conversions_value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    conversions_value = row.metrics.all_conversions
                else:
                    conversions_value = 0
                
                # Enregistrer toutes les conversions pour debug
                all_conversions.append({
                    'name': row.segments.conversion_action_name,
                    'id': row.segments.conversion_action,
                    'conversions': conversions_value
                })
                
                # Vérifier si c'est une conversion Itinéraires pour Addario (uniquement "Itinéraires" et "Local actions - Directions")
                is_addario_directions = any(target_name in conversion_name for target_name in self.ADDARIO_DIRECTIONS_NAMES)
                
                if is_addario_directions:
                    directions_total += conversions_value
                    logging.info(f" CONVERSION ADDARIO ITINÉRAIRES: {row.segments.conversion_action_name} = {conversions_value}")
                else:
                    logging.info(f"Conversion Addario ignorée: {row.segments.conversion_action_name} = {conversions_value}")
            
            # Filtrer seulement les conversions Itinéraires Addario
            directions_conversions = [conv for conv in all_conversions 
                                     if any(target_name in conv['name'].lower() for target_name in self.ADDARIO_DIRECTIONS_NAMES)]
            
            logging.info(f" Total Itinéraires Addario: {directions_total}")
            return directions_total, directions_conversions
            
        except Exception as e:
            logging.error(f" Erreur lors de la récupération des conversions Addario pour {customer_id}: {e}")
            return directions_total, all_conversions
    
    def update_contact_conversions_in_sheet(self, client_name: str, month: str, conversions_total: int) -> bool:
        """
        Met à jour les conversions Contact dans le Google Sheet
        
        Args:
            client_name: Nom du client (onglet)
            month: Mois à mettre à jour
            conversions_total: Nombre total de conversions
            
        Returns:
            True si succès, False sinon
        """
        try:
            # Vérifier que l'onglet existe
            available_sheets = self.sheets_service.get_worksheet_names()
            if client_name not in available_sheets:
                logging.error(f" Onglet '{client_name}' non trouvé dans le Google Sheet")
                return False
            
            # Trouver la ligne du mois
            row_number = self.sheets_service.get_row_for_month(client_name, month)
            if row_number is None:
                logging.error(f" Mois '{month}' non trouvé dans l'onglet '{client_name}'")
                return False
            
            # Trouver la colonne "Contact" (essayer différentes variantes)
            column_letter = self.sheets_service.get_column_for_metric(client_name, "Contact")
            if column_letter is None:
                column_letter = self.sheets_service.get_column_for_metric(client_name, "contact")
            if column_letter is None:
                logging.error(f" Colonne 'Contact' non trouvée dans l'onglet '{client_name}'")
                return False
            
            # Mettre à jour la cellule
            cell_range = f"{column_letter}{row_number}"
            success = self.sheets_service.update_single_cell(client_name, cell_range, conversions_total)
            
            if success:
                logging.info(f"✅ Conversions Contact mises à jour: {conversions_total} dans {client_name}")
            
            return success
            
        except Exception as e:
            logging.error(f" Erreur lors de la mise à jour Contact dans le Google Sheet: {e}")
            return False
    
    def update_directions_conversions_in_sheet(self, client_name: str, month: str, conversions_total: int) -> bool:
        """
        Met à jour les conversions Itinéraires dans le Google Sheet
        
        Args:
            client_name: Nom du client (onglet)
            month: Mois à mettre à jour
            conversions_total: Nombre total de conversions
            
        Returns:
            True si succès, False sinon
        """
        try:
            # Vérifier que l'onglet existe
            available_sheets = self.sheets_service.get_worksheet_names()
            if client_name not in available_sheets:
                logging.error(f" Onglet '{client_name}' non trouvé dans le Google Sheet")
                return False
            
            # Trouver la ligne du mois
            row_number = self.sheets_service.get_row_for_month(client_name, month)
            if row_number is None:
                logging.error(f" Mois '{month}' non trouvé dans l'onglet '{client_name}'")
                return False
            
            # Trouver la colonne "Itinéraires" (essayer différentes variantes)
            column_letter = self.sheets_service.get_column_for_metric(client_name, "Itinéraires")
            if column_letter is None:
                column_letter = self.sheets_service.get_column_for_metric(client_name, "itinéraires")
            if column_letter is None:
                # Essayer avec "Demande d'itineraires" 
                column_letter = self.sheets_service.get_column_for_metric(client_name, "Demande d'itineraires")
            if column_letter is None:
                # Essayer avec "demande d'itineraires" 
                column_letter = self.sheets_service.get_column_for_metric(client_name, "demande d'itineraires")
            
            if column_letter is None:
                logging.error(f" Colonne 'Itinéraires' non trouvée dans l'onglet '{client_name}'")
                return False
            
            # Mettre à jour la cellule
            cell_range = f"{column_letter}{row_number}"
            success = self.sheets_service.update_single_cell(client_name, cell_range, conversions_total)
            
            if success:
                logging.info(f"✅ Conversions Itinéraires mises à jour: {conversions_total} dans {client_name}")
            
            return success
            
        except Exception as e:
            logging.error(f" Erreur lors de la mise à jour Itinéraires dans le Google Sheet: {e}")
            return False
    
    def scrape_contact_conversions_for_customer(self, customer_id: str, client_name: str, 
                                               start_date: str, end_date: str, month: str) -> Dict[str, Any]:
        """
        Fonction principale pour scraper les conversions Contact d'un client et les ajouter au Google Sheet
        
        Args:
            customer_id: ID du client Google Ads
            client_name: Nom du client (onglet)
            start_date: Date de début
            end_date: Date de fin
            month: Mois à mettre à jour
            
        Returns:
            Dictionnaire avec le résultat de l'opération
        """
        try:
            logging.info(f" Début du scraping Contact pour {client_name} (ID: {customer_id})")
            
            # Vérifier si c'est A.G. Cryolipolyse pour utiliser la logique spécifique
            if customer_id == "9321943301" or client_name == "A.G. Cryolipolyse":
                logging.info(f"🧊 Utilisation de la logique spécifique Cryolipolyse pour {client_name}")
                # Récupérer les données de conversions Contact avec la logique Cryolipolyse
                total_conversions, found_conversions = self.get_cryolipolyse_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "3259500758" or client_name == "Crozatier Dijon":
                logging.info(f"🏪 Utilisation de la logique spécifique Crozatier pour {client_name}")
                # Récupérer les données de conversions Contact avec la logique Crozatier
                total_conversions, found_conversions = self.get_crozatier_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "1810240249" or client_name == "Denteva":
                logging.info(f"🦷 Utilisation de la logique spécifique Denteva pour {client_name}")
                # Récupérer les données de conversions Contact avec la logique Denteva
                total_conversions, found_conversions = self.get_denteva_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "5461114350" or client_name == "EvoPro Informatique":
                logging.info(f"💻 Utilisation de la logique spécifique EvoPro pour {client_name}")
                # Récupérer les données de conversions Contact avec la logique EvoPro
                total_conversions, found_conversions = self.get_evopro_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "5104651305" or client_name == "France Literie Aix":
                logging.info(f"🛏️ Utilisation de la logique spécifique France Literie Aix pour {client_name}")
                # Récupérer les données de conversions Contact avec la logique France Literie Aix
                total_conversions, found_conversions = self.get_france_literie_aix_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "7349999845" or client_name == "France Literie Dijon":
                logging.info(f"🏰 Utilisation de la logique spécifique France Literie Dijon pour {client_name}")
                # Récupérer les données de conversions Contact avec la logique France Literie Dijon
                total_conversions, found_conversions = self.get_france_literie_dijon_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "7807237268" or client_name == "France Literie Narbonne":
                logging.info(f"🏛️ Utilisation de la logique spécifique France Literie Narbonne pour {client_name}")
                # Récupérer les données de conversions Contact avec la logique France Literie Narbonne
                total_conversions, found_conversions = self.get_france_literie_narbonne_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "1226105597" or client_name == "France Literie Perpignan":
                logging.info(f"🏰 Utilisation de la logique spécifique France Literie Perpignan pour {client_name}")
                # Récupérer les données de conversions Contact avec la logique France Literie Perpignan
                total_conversions, found_conversions = self.get_france_literie_perpignan_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "4854280249" or client_name == "Kaltea Aubagne":
                logging.info(f"🌡️ Utilisation de la logique spécifique Kaltea Aubagne pour {client_name}")
                # Récupérer les données de conversions Contact avec la logique Kaltea Aubagne
                total_conversions, found_conversions = self.get_kaltea_aubagne_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "1189918252" or client_name == "Kaltea Chalon sur Saône":
                logging.info(f"🌡️ Utilisation de la logique spécifique Kaltea Chalon pour {client_name}")
                # Récupérer les données de conversions Contact avec la logique Kaltea Chalon
                total_conversions, found_conversions = self.get_kaltea_chalon_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "5074336650" or client_name == "Kaltea Lyon Sud":
                logging.info(f"🌡️ Utilisation de la logique spécifique Kaltea Lyon pour {client_name}")
                # Récupérer les données de conversions Contact avec la logique Kaltea Lyon
                total_conversions, found_conversions = self.get_kaltea_lyon_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "5901565913" or client_name == "Laserel":
                logging.info(f"🔬 Utilisation de la logique spécifique Laserel pour {client_name}")
                # Récupérer les données de conversions Contact avec la logique Laserel
                total_conversions, found_conversions = self.get_laserel_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "3345723560" or client_name == "Laserel Auxerre":
                logging.info(f"🔬 Utilisation de la logique spécifique Laserel Auxerre pour {client_name}")
                # Récupérer les données de conversions Contact avec la logique Laserel Auxerre
                total_conversions, found_conversions = self.get_laserel_auxerre_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "4865583978" or client_name == "Star Literie":
                logging.info(f"⭐ Utilisation de la logique spécifique Star Literie pour {client_name}")
                # Récupérer les données de conversions Contact avec la logique Star Literie
                total_conversions, found_conversions = self.get_star_literie_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "3245028529" or client_name == "Tousalon Perpignan":
                logging.info(f"💇 Utilisation de la logique spécifique Tousalon Perpignan pour {client_name}")
                # Récupérer les données de conversions Contact avec la logique Tousalon Perpignan
                total_conversions, found_conversions = self.get_tousalon_perpignan_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "4913925892" or client_name == "Tousalon Toulouse":
                logging.info(f"🏛️ Utilisation de la logique spécifique Tousalon Toulouse pour {client_name}")
                # Récupérer les données de conversions Contact avec la logique Tousalon Toulouse
                total_conversions, found_conversions = self.get_tousalon_toulouse_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "2620320258" or client_name == "Bedroom Perpignan":
                logging.info(f"🛏️ Utilisation de la logique spécifique Bedroom pour {client_name}")
                # Récupérer les données de conversions Contact avec la logique Bedroom
                total_conversions, found_conversions = self.get_bedroom_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "2288773609" or client_name == "Emma Perpignan":
                logging.info(f"🌸 Utilisation de la logique spécifique Emma Perpignan pour {client_name}")
                total_conversions, found_conversions = self.get_emma_perpignan_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "6470486244" or client_name == "Emma Vendenheim":
                logging.info(f"🌷 Utilisation de la logique spécifique Emma Vendenheim pour {client_name}")
                total_conversions, found_conversions = self.get_emma_vendenheim_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "9360801546" or client_name == "Cuisine Plus Perpignan":
                logging.info(f"🍽️ Utilisation de la logique spécifique Cuisine Plus Perpignan pour {client_name}")
                # Récupérer les données de conversions Contact avec la logique Cuisine Plus Perpignan (pas de contact)
                total_conversions, found_conversions = self.get_cuisine_plus_perpignan_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "9576529976" or client_name == "Flamme&Creation":
                logging.info(f"🔥 Utilisation de la logique spécifique Flamme&Creation pour {client_name}")
                # Récupérer les données de conversions Contact avec la logique Flamme&Creation
                total_conversions, found_conversions = self.get_flamme_creation_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "1842495793" or client_name == "France Literie Champagne":
                logging.info(f"🍾 Utilisation de la logique spécifique FL Champagne pour {client_name}")
                # Récupérer les données de conversions Contact avec la logique FL Champagne
                total_conversions, found_conversions = self.get_fl_champagne_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "3511211392" or client_name == "France Literie Saint-Priest & Givors":
                logging.info(f"🏰 Utilisation de la logique spécifique Saint Priest Givors pour {client_name}")
                # Récupérer les données de conversions Contact avec la logique Saint Priest Givors
                total_conversions, found_conversions = self.get_saint_priest_givors_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "2744128994" or client_name == "France Literie Annemasse":
                logging.info(f"🏔️ Utilisation de la logique spécifique France Literie Annemasse pour {client_name}")
                # Récupérer les données de conversions Contact avec la logique France Literie Annemasse
                total_conversions, found_conversions = self.get_france_literie_annemasse_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "2485486745" or client_name == "France Literie Antibes Vallauris":
                logging.info(f"🏖️ Utilisation de la logique spécifique FL Antibes Vallauris pour {client_name}")
                # Récupérer les données de conversions Contact avec la logique FL Antibes Vallauris
                total_conversions, found_conversions = self.get_fl_antibes_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "6090621431" or client_name == "Emma Merignac":
                logging.info(f" Utilisation de la logique spécifique Emma Merignac pour {client_name}")
                total_conversions, found_conversions = self.get_emma_merignac_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "6470486244" or client_name == "Emma Vendenheim":
                logging.info(f" Utilisation de la logique Emma Merignac pour {client_name}")
                total_conversions, found_conversions = self.get_emma_merignac_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "7836791446" or client_name == "Meuble Rigaud" or client_name == "Meubles Rigaud":
                logging.info(f"🪑 Utilisation de la logique spécifique Meuble Rigaud pour {client_name}")
                # Récupérer les données de conversions Contact avec la logique Meuble Rigaud
                total_conversions, found_conversions = self.get_meuble_rigaud_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "2041308129" or client_name == "My Salon Aubière":
                logging.info(f"💇 Utilisation de la logique spécifique My Salon Aubière pour {client_name}")
                # Récupérer les données de conversions Contact avec la logique My Salon Aubière
                total_conversions, found_conversions = self.get_my_salon_aubiere_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            else:
                # Récupérer les données de conversions Contact avec la logique standard
                total_conversions, found_conversions = self.get_contact_conversions_data(
                    customer_id, start_date, end_date
                )
            
            # Mettre à jour le Google Sheet
            success = self.update_contact_conversions_in_sheet(client_name, month, total_conversions)
            
            if success:
                logging.info(f"🎉 Scraping Contact terminé avec succès pour {client_name}")
                return {
                    'success': True,
                    'total_conversions': total_conversions,
                    'found_conversions': found_conversions
                }
            else:
                logging.error(f" Échec de la mise à jour du Google Sheet pour {client_name}")
                return {
                    'success': False,
                    'total_conversions': total_conversions,
                    'found_conversions': found_conversions
                }
        
        except Exception as e:
            logging.error(f" Erreur lors du scraping Contact pour {client_name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def scrape_directions_conversions_for_customer(self, customer_id: str, client_name: str,
                                                  start_date: str, end_date: str, month: str) -> Dict[str, Any]:
        """
        Fonction principale pour scraper les conversions Itinéraires d'un client et les ajouter au Google Sheet
        
        Args:
            customer_id: ID du client Google Ads
            client_name: Nom du client (onglet)
            start_date: Date de début
            end_date: Date de fin
            month: Mois à mettre à jour
            
        Returns:
            Dictionnaire avec le résultat de l'opération
        """
        try:
            logging.info(f" Début du scraping Itinéraires pour {client_name} (ID: {customer_id})")
            
            # Vérifier si c'est Addario pour utiliser la logique spécifique
            if customer_id == "1513412386" or client_name == "Addario":
                logging.info(f" Utilisation de la logique spécifique Addario pour {client_name}")
                # Récupérer les données de conversions Itinéraires avec la logique Addario
                total_conversions, found_conversions = self.get_addario_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "1810240249" or client_name == "Denteva":
                logging.info(f"🦷 Utilisation de la logique spécifique Denteva pour {client_name}")
                # Récupérer les données de conversions Itinéraires avec la logique Denteva
                total_conversions, found_conversions = self.get_denteva_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "5461114350" or client_name == "EvoPro Informatique":
                logging.info(f"💻 Utilisation de la logique spécifique EvoPro pour {client_name}")
                # Récupérer les données de conversions Itinéraires avec la logique EvoPro
                total_conversions, found_conversions = self.get_evopro_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "5104651305" or client_name == "France Literie Aix":
                logging.info(f"🛏️ Utilisation de la logique spécifique France Literie Aix pour {client_name}")
                # Récupérer les données de conversions Itinéraires avec la logique France Literie Aix
                total_conversions, found_conversions = self.get_france_literie_aix_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "7349999845" or client_name == "France Literie Dijon":
                logging.info(f"🏰 Utilisation de la logique spécifique France Literie Dijon pour {client_name}")
                # Récupérer les données de conversions Itinéraires avec la logique France Literie Dijon
                total_conversions, found_conversions = self.get_france_literie_dijon_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "7807237268" or client_name == "France Literie Narbonne":
                logging.info(f"🏛️ Utilisation de la logique spécifique France Literie Narbonne pour {client_name}")
                # Récupérer les données de conversions Itinéraires avec la logique France Literie Narbonne
                total_conversions, found_conversions = self.get_france_literie_narbonne_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "1226105597" or client_name == "France Literie Perpignan":
                logging.info(f"🏰 Utilisation de la logique spécifique France Literie Perpignan pour {client_name}")
                # Récupérer les données de conversions Itinéraires avec la logique France Literie Perpignan
                total_conversions, found_conversions = self.get_france_literie_perpignan_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "4854280249" or client_name == "Kaltea Aubagne":
                logging.info(f"🌡️ Utilisation de la logique spécifique Kaltea Aubagne pour {client_name}")
                # Récupérer les données de conversions Itinéraires avec la logique Kaltea Aubagne
                total_conversions, found_conversions = self.get_kaltea_aubagne_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "1189918252" or client_name == "Kaltea Chalon sur Saône":
                logging.info(f"🌡️ Utilisation de la logique spécifique Kaltea Chalon pour {client_name}")
                # Récupérer les données de conversions Itinéraires avec la logique Kaltea Chalon
                total_conversions, found_conversions = self.get_kaltea_chalon_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "5074336650" or client_name == "Kaltea Lyon Sud":
                logging.info(f"🌡️ Utilisation de la logique spécifique Kaltea Lyon pour {client_name}")
                # Récupérer les données de conversions Itinéraires avec la logique Kaltea Lyon
                total_conversions, found_conversions = self.get_kaltea_lyon_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "5901565913" or client_name == "Laserel":
                logging.info(f"🔬 Utilisation de la logique spécifique Laserel pour {client_name}")
                # Récupérer les données de conversions Itinéraires avec la logique Laserel
                total_conversions, found_conversions = self.get_laserel_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "3345723560" or client_name == "Laserel Auxerre":
                logging.info(f"🔬 Utilisation de la logique spécifique Laserel Auxerre pour {client_name}")
                # Récupérer les données de conversions Itinéraires avec la logique Laserel Auxerre
                total_conversions, found_conversions = self.get_laserel_auxerre_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "4865583978" or client_name == "Star Literie":
                logging.info(f"⭐ Utilisation de la logique spécifique Star Literie pour {client_name}")
                # Récupérer les données de conversions Itinéraires avec la logique Star Literie
                total_conversions, found_conversions = self.get_star_literie_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "3245028529" or client_name == "Tousalon Perpignan":
                logging.info(f"💇 Utilisation de la logique spécifique Tousalon Perpignan pour {client_name}")
                # Récupérer les données de conversions Itinéraires avec la logique Tousalon Perpignan
                total_conversions, found_conversions = self.get_tousalon_perpignan_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "4913925892" or client_name == "Tousalon Toulouse":
                logging.info(f"🏛️ Utilisation de la logique spécifique Tousalon Toulouse pour {client_name}")
                # Récupérer les données de conversions Itinéraires avec la logique Tousalon Toulouse
                total_conversions, found_conversions = self.get_tousalon_toulouse_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "2620320258" or client_name == "Bedroom Perpignan":
                logging.info(f"🛏️ Utilisation de la logique spécifique Bedroom pour {client_name}")
                # Récupérer les données de conversions Itinéraires avec la logique Bedroom
                total_conversions, found_conversions = self.get_bedroom_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "2288773609" or client_name == "Emma Perpignan":
                logging.info(f"🌸 Utilisation de la logique spécifique Emma Perpignan pour {client_name}")
                total_conversions, found_conversions = self.get_emma_perpignan_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "6470486244" or client_name == "Emma Vendenheim":
                logging.info(f"🌷 Utilisation de la logique spécifique Emma Vendenheim pour {client_name}")
                total_conversions, found_conversions = self.get_emma_vendenheim_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "3259500758" or client_name == "Crozatier Dijon":
                logging.info(f"🏪 Utilisation de la logique spécifique Crozatier pour {client_name}")
                # Récupérer les données de conversions Itinéraires avec la logique Crozatier
                total_conversions, found_conversions = self.get_crozatier_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "9360801546" or client_name == "Cuisine Plus Perpignan":
                logging.info(f"🍽️ Utilisation de la logique spécifique Cuisine Plus Perpignan pour {client_name}")
                # Récupérer les données de conversions Itinéraires avec la logique Cuisine Plus Perpignan
                total_conversions, found_conversions = self.get_cuisine_plus_perpignan_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "9576529976" or client_name == "Flamme&Creation":
                logging.info(f"🔥 Utilisation de la logique spécifique Flamme&Creation pour {client_name}")
                # Récupérer les données de conversions Itinéraires avec la logique Flamme&Creation
                total_conversions, found_conversions = self.get_flamme_creation_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "1842495793" or client_name == "France Literie Champagne":
                logging.info(f"🍾 Utilisation de la logique spécifique FL Champagne pour {client_name}")
                # Récupérer les données de conversions Itinéraires avec la logique FL Champagne
                total_conversions, found_conversions = self.get_fl_champagne_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "3511211392" or client_name == "France Literie Saint-Priest & Givors":
                logging.info(f"🏰 Utilisation de la logique spécifique Saint Priest Givors pour {client_name}")
                # Récupérer les données de conversions Itinéraires avec la logique Saint Priest Givors
                total_conversions, found_conversions = self.get_saint_priest_givors_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "2744128994" or client_name == "France Literie Annemasse":
                logging.info(f"🏔️ Utilisation de la logique spécifique France Literie Annemasse pour {client_name}")
                # Récupérer les données de conversions Itinéraires avec la logique France Literie Annemasse
                total_conversions, found_conversions = self.get_france_literie_annemasse_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "2485486745" or client_name == "France Literie Antibes Vallauris":
                logging.info(f"🏖️ Utilisation de la logique spécifique FL Antibes Vallauris pour {client_name}")
                # Récupérer les données de conversions Itinéraires avec la logique FL Antibes Vallauris
                total_conversions, found_conversions = self.get_fl_antibes_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "6090621431" or client_name == "Emma Merignac":
                logging.info(f" Utilisation de la logique spécifique Emma Merignac pour {client_name}")
                total_conversions, found_conversions = self.get_emma_merignac_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "6470486244" or client_name == "Emma Vendenheim":
                logging.info(f" Utilisation de la logique Emma Vendenheim pour {client_name}")
                total_conversions, found_conversions = self.get_emma_vendenheim_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "7836791446" or client_name == "Meuble Rigaud" or client_name == "Meubles Rigaud":
                logging.info(f"🪑 Utilisation de la logique spécifique Meuble Rigaud pour {client_name}")
                # Récupérer les données de conversions Itinéraires avec la logique Meuble Rigaud
                total_conversions, found_conversions = self.get_meuble_rigaud_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            elif customer_id == "2041308129" or client_name == "My Salon Aubière":
                logging.info(f"💇 Utilisation de la logique spécifique My Salon Aubière pour {client_name}")
                # Récupérer les données de conversions Itinéraires avec la logique My Salon Aubière
                total_conversions, found_conversions = self.get_my_salon_aubiere_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            else:
                # Récupérer les données de conversions Itinéraires avec la logique standard
                total_conversions, found_conversions = self.get_directions_conversions_data(
                    customer_id, start_date, end_date
                )
            
            # Mettre à jour le Google Sheet
            success = self.update_directions_conversions_in_sheet(client_name, month, total_conversions)
            
            if success:
                logging.info(f"🎉 Scraping Itinéraires terminé avec succès pour {client_name}")
                return {
                    'success': True,
                    'total_conversions': total_conversions,
                    'found_conversions': found_conversions
                }
            else:
                logging.error(f" Échec de la mise à jour du Google Sheet pour {client_name}")
                return {
                    'success': False,
                    'total_conversions': total_conversions,
                    'found_conversions': found_conversions
                }
        
        except Exception as e:
            logging.error(f" Erreur lors du scraping Itinéraires pour {client_name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def scrape_temps_passe_for_customer(
        self,
        customer_id: str,
        client_name: str,
        start_date: str,
        end_date: str,
        month: str,
        action_name_substring: str,
        sheet_column: str = "Temps passé Google",
    ) -> Dict[str, Any]:
        """
        Scrape une conversion action spécifique (par sous-chaîne dans le nom)
        et écrit le total dans la colonne du Sheet (par défaut 'Temps passé Google').

        Args:
            customer_id: ID Google Ads du client
            client_name: Nom de l'onglet Sheet (et nom du client)
            start_date, end_date: Période YYYY-MM-DD
            month: Nom du mois pour la ligne du Sheet
            action_name_substring: Sous-chaîne à matcher dans le nom de la conversion (insensible casse)
            sheet_column: Nom exact de la colonne du Sheet (ligne 2) où écrire la valeur

        Returns:
            Dict {success, total_conversions, found_conversions}
        """
        try:
            logging.info(f"⏱️  Scraping Temps passé '{action_name_substring}' pour {client_name} (ID: {customer_id})")

            query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action,
                metrics.all_conversions,
                metrics.conversions
            FROM campaign
            WHERE
                segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND metrics.all_conversions > 0
            """

            response = self.auth_service.fetch_report_data(customer_id, query)

            needle = action_name_substring.lower().strip()
            total_conversions = 0
            found_conversions: List[Dict[str, Any]] = []

            for row in response:
                conv_name = (row.segments.conversion_action_name or "").strip()
                conv_name_low = conv_name.lower()

                if row.metrics.conversions and row.metrics.conversions > 0:
                    value = row.metrics.conversions
                elif row.metrics.all_conversions and row.metrics.all_conversions > 0:
                    value = row.metrics.all_conversions
                else:
                    value = 0

                if needle in conv_name_low:
                    total_conversions += value
                    found_conversions.append({
                        "name": conv_name,
                        "id": row.segments.conversion_action,
                        "conversions": value,
                    })
                    logging.info(f"⏱️  CONVERSION TEMPS PASSÉ: {conv_name} = {value}")

            logging.info(f"⏱️  Total Temps passé pour {client_name}: {total_conversions}")

            # Écriture dans le Sheet
            available_sheets = self.sheets_service.get_worksheet_names()
            if client_name not in available_sheets:
                logging.error(f"Onglet '{client_name}' non trouvé dans le Google Sheet")
                return {"success": False, "total_conversions": total_conversions, "found_conversions": found_conversions}

            row_number = self.sheets_service.get_row_for_month(client_name, month)
            if row_number is None:
                logging.error(f"Mois '{month}' non trouvé dans l'onglet '{client_name}'")
                return {"success": False, "total_conversions": total_conversions, "found_conversions": found_conversions}

            column_letter = self.sheets_service.get_column_for_metric(client_name, sheet_column)
            if column_letter is None:
                logging.error(f"Colonne '{sheet_column}' non trouvée dans l'onglet '{client_name}'")
                return {"success": False, "total_conversions": total_conversions, "found_conversions": found_conversions}

            cell_range = f"{column_letter}{row_number}"
            ok = self.sheets_service.update_single_cell(client_name, cell_range, total_conversions)

            if ok:
                logging.info(f"✅ Temps passé Google écrit: {total_conversions} → {client_name}!{cell_range}")

            return {
                "success": ok,
                "total_conversions": total_conversions,
                "found_conversions": found_conversions,
            }

        except Exception as e:
            logging.error(f"❌ Erreur scrape_temps_passe_for_customer ({client_name}): {e}")
            return {"success": False, "error": str(e)}
