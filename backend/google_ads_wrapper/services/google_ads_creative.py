"""
Service pour récupérer le contenu créatif des campagnes Google Ads
"""

import logging
import requests
import io
from typing import Dict, List, Any, Optional, Tuple
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

class GoogleAdsCreativeService:
    """Service pour gérer la récupération du contenu créatif Google Ads"""
    
    def __init__(self):
        """Initialise le client Google Ads"""
        try:
            from backend.config.settings import Config
            self.client = GoogleAdsClient.load_from_storage(Config.API.GOOGLE_ADS_YAML_PATH)
            logging.info("✅ Google Ads Creative Service initialisé")
        except Exception as e:
            logging.error(f"❌ Erreur lors de l'initialisation du service Google Ads Creative: {e}")
            raise
    
    def get_active_campaigns(self, customer_id: str) -> List[Dict[str, Any]]:
        """
        Récupère toutes les campagnes actives d'un client
        
        Args:
            customer_id: ID du client Google Ads
            
        Returns:
            Liste des campagnes actives avec leur ID et nom
        """
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = """
                SELECT
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign.advertising_channel_type
                FROM campaign
                WHERE campaign.status = 'ENABLED'
                ORDER BY campaign.name
            """
            
            response = ga_service.search(customer_id=customer_id, query=query)
            
            campaigns = []
            for row in response:
                campaigns.append({
                    "id": row.campaign.id,
                    "name": row.campaign.name,
                    "status": row.campaign.status.name,
                    "type": row.campaign.advertising_channel_type.name
                })
            
            logging.info(f"📊 {len(campaigns)} campagnes actives trouvées pour {customer_id}")
            return campaigns
            
        except GoogleAdsException as ex:
            logging.error(f"❌ Erreur Google Ads API: {ex}")
            return []
        except Exception as e:
            logging.error(f"❌ Erreur lors de la récupération des campagnes: {e}")
            return []
    
    def get_campaign_ads(self, customer_id: str, campaign_id: int, campaign_type: str = None) -> List[Dict[str, Any]]:
        """
        Récupère toutes les annonces d'une campagne avec leurs assets créatifs
        Adapte la stratégie selon le type de campagne (PMax ou Standard).
        
        Args:
            customer_id: ID du client Google Ads
            campaign_id: ID de la campagne
            campaign_type: Type de campagne (PERFORMANCE_MAX, SEARCH, DISPLAY, etc.)
            
        Returns:
            Liste des annonces avec leurs contenus créatifs
        """
        try:
            # Si le type n'est pas fourni, on essaie de le deviner ou on traite comme standard
            if campaign_type == 'PERFORMANCE_MAX':
                return self._get_pmax_assets(customer_id, campaign_id)
            elif campaign_type == 'SEARCH':
                return self._get_search_ads_with_extensions(customer_id, campaign_id)
            else:
                # Fallback standard (Display, Video, etc.)
                return self._get_standard_ads(customer_id, campaign_id)
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de la récupération des annonces pour la campagne {campaign_id}: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return []

    def _get_pmax_assets(self, customer_id: str, campaign_id: int) -> List[Dict[str, Any]]:
        """Récupère les Asset Groups pour les campagnes Performance Max"""
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            # 1. Récupérer les Asset Groups
            query_groups = f"""
                SELECT
                    asset_group.id,
                    asset_group.name,
                    asset_group.status,
                    asset_group.final_urls
                FROM asset_group
                WHERE campaign.id = {campaign_id}
                    AND asset_group.status = 'ENABLED'
            """
            
            response_groups = ga_service.search(customer_id=customer_id, query=query_groups)
            
            asset_groups = {}
            for row in response_groups:
                ag_id = row.asset_group.id
                asset_groups[ag_id] = {
                    "ad_group_id": ag_id, # On utilise l'ID asset group comme ad_group_id
                    "ad_group_name": row.asset_group.name,
                    "ad_id": ag_id,
                    "ad_name": f"Asset Group: {row.asset_group.name}",
                    "ad_type": "PERFORMANCE_MAX",
                    "final_urls": list(row.asset_group.final_urls) if row.asset_group.final_urls else [],
                    "headlines": [],
                    "descriptions": [],
                    "images": [],
                    "videos": []
                }
            
            if not asset_groups:
                logging.info(f"ℹ️ Aucun Asset Group trouvé pour la campagne PMax {campaign_id}")
                return []
                
            # 2. Récupérer les assets liés aux Asset Groups
            query_assets = f"""
                SELECT
                    asset_group.id,
                    asset.id,
                    asset.type,
                    asset_group_asset.field_type,
                    asset.image_asset.full_size.url,
                    asset.youtube_video_asset.youtube_video_id,
                    asset.text_asset.text
                FROM asset_group_asset
                WHERE campaign.id = {campaign_id}
                    AND asset_group_asset.status = 'ENABLED'
            """
            
            response_assets = ga_service.search(customer_id=customer_id, query=query_assets)
            
            for row in response_assets:
                ag_id = row.asset_group.id
                if ag_id not in asset_groups:
                    continue
                    
                asset = row.asset
                field_type = row.asset_group_asset.field_type.name 
                # field_type peut être HEADLINE, DESCRIPTION, MARKETING_IMAGE, LOGO, YOUTUBE_VIDEO, etc.
                
                if asset.type_.name == "IMAGE" and asset.image_asset.full_size.url:
                    asset_groups[ag_id]["images"].append(asset.image_asset.full_size.url)
                    
                elif asset.type_.name == "YOUTUBE_VIDEO" and asset.youtube_video_asset.youtube_video_id:
                    # Pour YouTube, on stocke l'ID et l'URL de la vidéo (pas téléchargeable directement)
                    video_id = asset.youtube_video_asset.youtube_video_id
                    youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                    # Stocker l'URL YouTube dans un champ séparé
                    if "youtube_videos" not in asset_groups[ag_id]:
                        asset_groups[ag_id]["youtube_videos"] = []
                    asset_groups[ag_id]["youtube_videos"].append({
                        "id": video_id,
                        "url": youtube_url,
                        "thumbnail": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                    })
                    
                elif asset.type_.name == "TEXT" and asset.text_asset.text:
                    if "HEADLINE" in field_type:
                        asset_groups[ag_id]["headlines"].append(asset.text_asset.text)
                    elif "DESCRIPTION" in field_type:
                        asset_groups[ag_id]["descriptions"].append(asset.text_asset.text)
            
            return list(asset_groups.values())
            
        except Exception as e:
            logging.error(f"❌ Erreur PMax pour {campaign_id}: {e}")
            return []

    def _get_search_ads_with_extensions(self, customer_id: str, campaign_id: int) -> List[Dict[str, Any]]:
        """Récupère les annonces Search standards + Extensions d'image"""
        # 1. Récupérer les annonces standards
        ads = self._get_standard_ads(customer_id, campaign_id)
        
        if not ads:
            return []
            
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            # 2. Récupérer les extensions d'image au niveau Campagne
            # (Note: on pourrait aussi chercher au niveau AdGroup si besoin)
            query_ext = f"""
                SELECT
                    asset.id,
                    asset.image_asset.full_size.url
                FROM campaign_asset
                WHERE campaign.id = {campaign_id}
                    AND asset.type = 'IMAGE'
                    AND campaign_asset.status = 'ENABLED'
            """
            
            response_ext = ga_service.search(customer_id=customer_id, query=query_ext)
            
            extension_images = []
            for row in response_ext:
                if row.asset.image_asset.full_size.url:
                    extension_images.append(row.asset.image_asset.full_size.url)
            
            if extension_images:
                logging.info(f"🖼️ {len(extension_images)} extensions d'image trouvées pour la campagne Search")
                # On ajoute ces images à TOUTES les annonces de la campagne
                # C'est une approximation, mais pour un rapport créatif c'est pertinent
                for ad in ads:
                    ad["images"].extend(extension_images)
            
        except Exception as e:
            logging.warning(f"⚠️ Erreur récupération extensions Search pour {campaign_id}: {e}")
            
        return ads

    def _get_standard_ads(self, customer_id: str, campaign_id: int) -> List[Dict[str, Any]]:
        """Logique standard pour récupérer les annonces via ad_group_ad"""
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            query_ads = f"""
                SELECT
                    ad_group.id,
                    ad_group.name,
                    ad_group_ad.ad.id,
                    ad_group_ad.ad.name,
                    ad_group_ad.ad.type,
                    ad_group_ad.ad.final_urls,
                    ad_group_ad.ad.responsive_search_ad.headlines,
                    ad_group_ad.ad.responsive_search_ad.descriptions,
                    ad_group_ad.ad.responsive_display_ad.headlines,
                    ad_group_ad.ad.responsive_display_ad.descriptions,
                    ad_group_ad.status
                FROM ad_group_ad
                WHERE campaign.id = {campaign_id}
                    AND ad_group_ad.status = 'ENABLED'
                ORDER BY ad_group.name, ad_group_ad.ad.id
            """
            
            response_ads = ga_service.search(customer_id=customer_id, query=query_ads)
            
            ads_map = {}
            for row in response_ads:
                ad_id = row.ad_group_ad.ad.id
                
                ad_data = {
                    "ad_group_id": row.ad_group.id,
                    "ad_group_name": row.ad_group.name,
                    "ad_id": ad_id,
                    "ad_name": row.ad_group_ad.ad.name if row.ad_group_ad.ad.name else f"Ad_{ad_id}",
                    "ad_type": row.ad_group_ad.ad.type_.name,
                    "final_urls": list(row.ad_group_ad.ad.final_urls) if row.ad_group_ad.ad.final_urls else [],
                    "headlines": [],
                    "descriptions": [],
                    "images": [],
                    "videos": []
                }
                
                # Textes
                if row.ad_group_ad.ad.type_.name == "RESPONSIVE_SEARCH_AD":
                    ad_data["headlines"] = [h.text for h in row.ad_group_ad.ad.responsive_search_ad.headlines]
                    ad_data["descriptions"] = [d.text for d in row.ad_group_ad.ad.responsive_search_ad.descriptions]
                elif row.ad_group_ad.ad.type_.name == "RESPONSIVE_DISPLAY_AD":
                    ad_data["headlines"] = [h.text for h in row.ad_group_ad.ad.responsive_display_ad.headlines]
                    ad_data["descriptions"] = [d.text for d in row.ad_group_ad.ad.responsive_display_ad.descriptions]
                
                ads_map[ad_id] = ad_data

            if not ads_map:
                return []

            # Récupération assets enrichis (Images & Vidéos) via ad_group_ad_asset_view
            query_assets = f"""
                SELECT
                    ad_group_ad.ad.id,
                    asset.id,
                    asset.type,
                    asset.image_asset.full_size.url,
                    asset.youtube_video_asset.youtube_video_id
                FROM ad_group_ad_asset_view
                WHERE campaign.id = {campaign_id}
                  AND ad_group_ad.status = 'ENABLED'
            """
            
            try:
                response_assets = ga_service.search(customer_id=customer_id, query=query_assets)
                
                for row in response_assets:
                    ad_id = row.ad_group_ad.ad.id
                    if ad_id not in ads_map:
                        continue
                        
                    asset_type = row.asset.type_.name
                    
                    if asset_type == "IMAGE":
                        if row.asset.image_asset.full_size.url:
                            ads_map[ad_id]["images"].append(row.asset.image_asset.full_size.url)
                    
                    elif asset_type == "YOUTUBE_VIDEO":
                         if row.asset.youtube_video_asset.youtube_video_id:
                            video_url = f"https://www.youtube.com/watch?v={row.asset.youtube_video_asset.youtube_video_id}"
                            ads_map[ad_id]["videos"].append(video_url)
                            
            except Exception as e:
                logging.warning(f"⚠️ Erreur récupération assets enrichis standard: {e}")
            
            return list(ads_map.values())
            
        except Exception as e:
            logging.error(f"❌ Erreur standard ads pour {campaign_id}: {e}")
            return []
    
    def download_media_file(self, url: str) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Télécharge un fichier média depuis une URL
        
        Args:
            url: URL du fichier à télécharger
            
        Returns:
            Tuple (contenu du fichier en bytes, extension du fichier avec point, ex: '.jpg')
        """
        try:
            logging.info(f"📥 Téléchargement de {url}")
            
            response = requests.get(url, timeout=60, stream=True)
            response.raise_for_status()
            
            # Déterminer l'extension depuis le Content-Type ou l'URL
            content_type = response.headers.get('Content-Type', '')
            extension = None
            
            if 'image/jpeg' in content_type or url.endswith('.jpg') or url.endswith('.jpeg'):
                extension = '.jpg'
            elif 'image/png' in content_type or url.endswith('.png'):
                extension = '.png'
            elif 'image/gif' in content_type or url.endswith('.gif'):
                extension = '.gif'
            elif 'video/mp4' in content_type or url.endswith('.mp4'):
                extension = '.mp4'
            elif 'video/quicktime' in content_type or url.endswith('.mov'):
                extension = '.mov'
            elif 'video' in content_type:
                extension = '.mp4'  # Par défaut pour les vidéos
            else:
                # Essayer d'extraire depuis l'URL (seulement si ça ressemble à une extension valide)
                if '.' in url:
                    potential_ext = url.split('.')[-1].split('?')[0].split('/')[0][:4]
                    if potential_ext.lower() in ['jpg', 'jpeg', 'png', 'gif', 'mp4', 'mov', 'webp']:
                        extension = f'.{potential_ext.lower()}'
                    else:
                        # Fallback: détecter par contenu
                        extension = '.jpg'  # Par défaut
            
            # Lire le contenu
            file_content = response.content
            file_size_mb = len(file_content) / (1024 * 1024)
            
            
            return file_content, extension
            
        except requests.exceptions.Timeout:
            logging.error(f"❌ Timeout lors du téléchargement de {url}")
            return None, None
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Erreur lors du téléchargement de {url}: {e}")
            return None, None
        except Exception as e:
            logging.error(f"❌ Erreur inattendue lors du téléchargement: {e}")
            return None, None

