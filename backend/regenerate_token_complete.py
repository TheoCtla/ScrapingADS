#!/usr/bin/env python3
"""
Régénération complète du token avec tous les scopes nécessaires
"""

import webbrowser
import urllib.parse

# Configuration
CLIENT_ID = '1023682396452-el4hfko5a54p1l3gj3drhhj8l93keacd.apps.googleusercontent.com'
CLIENT_SECRET = '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'
DEVELOPER_TOKEN = 'M1hyDPi_kibHFNDBTbwAQw'
LOGIN_CUSTOMER_ID = '3477628754'

# TOUS les scopes nécessaires pour Google Ads
SCOPES = [
    'https://www.googleapis.com/auth/adwords',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/cloud-platform.read-only'
]

def generate_complete_auth_url():
    """Génère l'URL d'autorisation avec TOUS les scopes"""
    
    print("🔄 RÉGÉNÉRATION COMPLÈTE DU TOKEN GOOGLE ADS")
    print("=" * 60)
    print()
    print("⚠️  IMPORTANT : Cette régénération inclut TOUS les scopes nécessaires")
    print("   Cela devrait résoudre définitivement l'erreur 'Channel deallocated!'")
    print()
    
    # Paramètres de l'URL d'autorisation
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
        'scope': ' '.join(SCOPES),
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent',  # Force la demande de consentement
        'include_granted_scopes': 'true'
    }
    
    # Construction de l'URL
    base_url = 'https://accounts.google.com/o/oauth2/auth'
    auth_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    print("🌐 URL d'autorisation complète :")
    print(f"   {auth_url}")
    print()
    
    # Ouverture automatique du navigateur
    try:
        webbrowser.open(auth_url)
        print("🚀 Ouverture automatique du navigateur...")
    except:
        print("⚠️  Impossible d'ouvrir automatiquement le navigateur")
        print("   Copiez et collez l'URL ci-dessus dans votre navigateur")
    
    print()
    print("📋 INSTRUCTIONS :")
    print("1. Autorisez l'application dans votre navigateur")
    print("2. Copiez le code d'autorisation affiché")
    print("3. Collez-le ci-dessous")
    print()
    
    return auth_url

if __name__ == "__main__":
    generate_complete_auth_url()
