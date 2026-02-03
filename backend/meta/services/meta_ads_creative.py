"""
Service pour récupérer le contenu créatif des campagnes Meta Ads
"""

import logging
import requests
from typing import Dict, List, Any, Optional, Tuple

from backend.config.settings import Config

class MetaAdsCreativeService:
    """Service pour gérer la récupération du contenu créatif Meta Ads"""
    
    def __init__(self):
        self.access_token = Config.API.META_ACCESS_TOKEN
        self.api_version = "v22.0"  # Updated to latest version
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        logging.info("✅ Meta Ads Creative Service initialisé")
    
    def get_active_campaigns(self, ad_account_id: str) -> List[Dict[str, Any]]:
        """
        Récupère toutes les campagnes actives d'un compte publicitaire
        
        Args:
            ad_account_id: ID du compte publicitaire Meta
            
        Returns:
            Liste des campagnes actives avec leur ID et nom
        """
        try:
            url = f"{self.base_url}/act_{ad_account_id}/campaigns"
            
            # Meta API requires JSON-encoded array for filtering parameters
            import json
            params = {
                "access_token": self.access_token,
                "fields": "id,name,status,objective",
                "filtering": json.dumps([{"field": "effective_status", "operator": "IN", "value": ["ACTIVE"]}]),
                "limit": 100
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            campaigns = data.get("data", [])
            
            logging.info(f"📊 {len(campaigns)} campagnes actives trouvées pour {ad_account_id}")
            return campaigns
            
        except requests.exceptions.HTTPError as e:
            # Log detailed error information
            logging.error(f"❌ Erreur HTTP {e.response.status_code} lors de la récupération des campagnes Meta")
            try:
                error_data = e.response.json()
                logging.error(f"❌ Détails de l'erreur Meta: {error_data}")
            except:
                logging.error(f"❌ Réponse brute: {e.response.text}")
            return []
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Erreur lors de la récupération des campagnes Meta: {e}")
            return []
        except Exception as e:
            logging.error(f"❌ Erreur inattendue: {e}")
            return []
    
    def get_campaign_creatives(self, ad_account_id: str, campaign_id: str) -> List[Dict[str, Any]]:
        """
        Récupère toutes les créations publicitaires d'une campagne
        
        Args:
            ad_account_id: ID du compte publicitaire
            campaign_id: ID de la campagne
            
        Returns:
            Liste des créations avec leurs contenus créatifs
        """
        try:
            # Étape 1: Récupérer toutes les annonces de la campagne
            url = f"{self.base_url}/act_{ad_account_id}/ads"
            
            # Combine campaign filter and status filter in one filtering parameter
            import json
            filters = [
                {"field": "campaign.id", "operator": "EQUAL", "value": campaign_id},
                {"field": "effective_status", "operator": "IN", "value": ["ACTIVE"]}
            ]
            
            params = {
                "access_token": self.access_token,
                "fields": "id,name,creative,status",
                "filtering": json.dumps(filters),
                "limit": 100
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            ads = data.get("data", [])
            
            logging.info(f"📝 {len(ads)} annonces trouvées pour la campagne {campaign_id}")
            
            # Étape 2: Pour chaque annonce, récupérer les détails du creative
            creatives = []
            for ad in ads:
                if "creative" in ad and "id" in ad["creative"]:
                    creative_id = ad["creative"]["id"]
                    creative_data = self._get_creative_details(creative_id)
                    
                    if creative_data:
                        creative_data["ad_id"] = ad["id"]
                        creative_data["ad_name"] = ad.get("name", f"Ad_{ad['id']}")
                        creatives.append(creative_data)
            
            logging.info(f"🎨 {len(creatives)} créations récupérées")
            return creatives
            
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Erreur lors de la récupération des annonces Meta: {e}")
            return []
        except Exception as e:
            logging.error(f"❌ Erreur inattendue: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return []
    
    def _get_creative_details(self, creative_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les détails d'une création publicitaire
        
        Args:
            creative_id: ID de la création
            
        Returns:
            Dictionnaire avec les détails de la création
        """
        try:
            url = f"{self.base_url}/{creative_id}"
            
            params = {
                "access_token": self.access_token,
                # Request comprehensive fields to see what's available
                "fields": "id,name,title,body,image_url,image_hash,video_id,thumbnail_url,object_story_spec,effective_object_story_id,asset_feed_spec,object_type,url_tags,link_url,call_to_action_type"
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            creative = response.json()
            
            # Debug: log what Meta returns
            logging.info(f"🔍 Creative {creative_id} data: {creative}")
            
            # Extraire les informations créatives
            creative_data = {
                "creative_id": creative.get("id"),
                "creative_name": creative.get("name", ""),
                "title": "",
                "body": "",
                "call_to_action": "",
                "link_url": "",
                "images": [],
                "videos": []
            }
            
            # Check if this is an Advantage+ catalog ad with asset_feed_spec
            if "asset_feed_spec" in creative:
                feed_spec = creative["asset_feed_spec"]
                
                # Extract title
                if "titles" in feed_spec and feed_spec["titles"]:
                    creative_data["title"] = feed_spec["titles"][0].get("text", "")
                
                # Extract body
                if "bodies" in feed_spec and feed_spec["bodies"]:
                    creative_data["body"] = feed_spec["bodies"][0].get("text", "")
                
                # Extract description (fallback if no body)
                if not creative_data["body"] and "descriptions" in feed_spec and feed_spec["descriptions"]:
                    creative_data["body"] = feed_spec["descriptions"][0].get("text", "")
                
                # Extract link URL
                if "link_urls" in feed_spec and feed_spec["link_urls"]:
                    creative_data["link_url"] = feed_spec["link_urls"][0].get("website_url", "")
                
                # Extract call to action
                if "call_to_action_types" in feed_spec and feed_spec["call_to_action_types"]:
                    creative_data["call_to_action"] = feed_spec["call_to_action_types"][0]
                
                # Extract images from image hashes
                if "images" in feed_spec:
                    for img in feed_spec["images"]:
                        if "hash" in img:
                            # Construct image URL from hash
                            image_url = f"https://scontent.xx.fbcdn.net/v/t45.1600-4/{img['hash']}"
                            creative_data["images"].append(image_url)
                
                # Extract videos
                if "videos" in feed_spec:
                    for video in feed_spec["videos"]:
                        if "video_id" in video:
                            video_url = self._get_video_url(video["video_id"])
                            if video_url:
                                creative_data["videos"].append(video_url)
            
            # Fallback: Use thumbnail_url if no images found
            if not creative_data["images"] and "thumbnail_url" in creative and creative["thumbnail_url"]:
                creative_data["images"].append(creative["thumbnail_url"])
            
            # Try to get actual post content if effective_object_story_id is available
            if "effective_object_story_id" in creative and not creative_data["title"]:
                story_id = creative["effective_object_story_id"]
                story_data = self._get_story_details(story_id)
                if story_data:
                    creative_data["title"] = story_data.get("name", "")
                    creative_data["body"] = story_data.get("message", "")
                    creative_data["link_url"] = story_data.get("link", "")
                    
                    # Get images from story
                    if "full_picture" in story_data:
                        creative_data["images"].append(story_data["full_picture"])
            
            logging.info(f"✅ Creative data extracted: title={creative_data['title'][:50] if creative_data['title'] else ''}, images={len(creative_data['images'])}, videos={len(creative_data['videos'])}")
            return creative_data
            
        except requests.exceptions.RequestException as e:
            logging.warning(f"⚠️ Impossible de récupérer les détails du creative {creative_id}: {e}")
            return None
        except Exception as e:
            logging.warning(f"⚠️ Erreur lors de la récupération du creative {creative_id}: {e}")
            return None
    
    def _get_video_url(self, video_id: str) -> Optional[str]:
        """
        Récupère l'URL de téléchargement d'une vidéo
        
        Args:
            video_id: ID de la vidéo
            
        Returns:
            URL de la vidéo ou None
        """
        try:
            url = f"{self.base_url}/{video_id}"
            
            params = {
                "access_token": self.access_token,
                "fields": "source,picture"
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            video_data = response.json()
            return video_data.get("source")
            
        except Exception as e:
            logging.warning(f"⚠️ Impossible de récupérer l'URL de la vidéo {video_id}: {e}")
            return None
    
    def _get_story_details(self, story_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les détails d'un post Facebook/Instagram
        
        Args:
            story_id: ID du post (effective_object_story_id)
            
        Returns:
            Dictionnaire avec les détails du post ou None
        """
        try:
            url = f"{self.base_url}/{story_id}"
            
            params = {
                "access_token": self.access_token,
                "fields": "message,link,full_picture,name"
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            # Dynamic Ads don't have accessible story content - this is expected
            logging.debug(f"Story {story_id} not accessible (likely Dynamic Ad): {e.response.status_code}")
            return None
        except Exception as e:
            logging.debug(f"Could not fetch story {story_id}: {e}")
            return None
    
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
            
            # Pour les vidéos Meta, ajouter le token d'accès
            if "facebook.com" in url or "fbcdn.net" in url:
                separator = "&" if "?" in url else "?"
                url = f"{url}{separator}access_token={self.access_token}"
            
            response = requests.get(url, timeout=120, stream=True)  # Timeout plus long pour les vidéos
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
