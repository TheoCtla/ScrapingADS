#!/usr/bin/env python3
"""
Test simple de connexion Google Ads
"""

import sys
import os

# Ajouter le répertoire backend au path
sys.path.append('/Users/theocatala/Desktop/scrappingRapport/backend')

def test_google_ads_basic():
    """Test basique de connexion Google Ads"""
    
    print("🔍 TEST SIMPLE GOOGLE ADS")
    print("=" * 40)
    print()
    
    try:
        from google.ads.googleads.client import GoogleAdsClient
        from google.ads.googleads.errors import GoogleAdsException
        print("✅ Import Google Ads réussi")
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False
    
    # Test 1: Initialisation
    print("\n🧪 Test 1: Initialisation du client...")
    try:
        config_path = '/Users/theocatala/Desktop/scrappingRapport/backend/config/google-ads.yaml'
        client = GoogleAdsClient.load_from_storage(config_path)
        print("✅ Client initialisé")
        print(f"   Login Customer ID: {client.login_customer_id}")
    except Exception as e:
        print(f"❌ Erreur d'initialisation: {e}")
        return False
    
    # Test 2: Ancien client (qui fonctionne)
    print("\n🧪 Test 2: Test avec un ancien client...")
    try:
        ga_service = client.get_service("GoogleAdsService")
        query = "SELECT customer.id FROM customer LIMIT 1"
        response = ga_service.search(customer_id="9321943301", query=query)  # A.G. Cryolipolyse
        results = list(response)
        
        if results:
            print("✅ Ancien client fonctionne")
        else:
            print("⚠️ Ancien client: Aucune donnée")
            
    except Exception as e:
        print(f"❌ Ancien client échoue: {e}")
    
    # Test 3: Nouveau client problématique
    print("\n🧪 Test 3: Test avec Bedroom Perpignan...")
    try:
        query = "SELECT customer.id FROM customer LIMIT 1"
        response = ga_service.search(customer_id="2620320258", query=query)  # Bedroom Perpignan
        results = list(response)
        
        if results:
            print("✅ Bedroom Perpignan fonctionne maintenant !")
            return True
        else:
            print("⚠️ Bedroom Perpignan: Aucune donnée")
            
    except GoogleAdsException as ex:
        error_code = ex.error.code().name if hasattr(ex.error, 'code') else 'UNKNOWN'
        error_message = ex.failure.errors[0].message if ex.failure.errors else str(ex)
        
        print(f"❌ Bedroom Perpignan échoue encore")
        print(f"   Code: {error_code}")
        print(f"   Message: {error_message}")
        
        if "Channel deallocated" in error_message:
            print("\n🔍 DIAGNOSTIC:")
            print("   L'erreur 'Channel deallocated!' persiste")
            print("   CAUSES POSSIBLES:")
            print("   1. Le nouveau token n'est pas déployé sur Render")
            print("   2. Le compte client nécessite une approbation spéciale")
            print("   3. Problème de configuration gRPC")
            print("   4. Le compte client n'est pas accessible")
            
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
    
    return False

if __name__ == "__main__":
    success = test_google_ads_basic()
    
    if not success:
        print("\n💡 RECOMMANDATIONS:")
        print("1. Vérifiez que Render a bien redéployé avec le nouveau token")
        print("2. Attendez 5-10 minutes pour que le déploiement soit complet")
        print("3. Vérifiez les logs Render pour des erreurs de déploiement")
        print("4. Le compte client pourrait nécessiter une approbation spéciale")
        print("5. Essayez de régénérer le token OAuth avec tous les scopes nécessaires")
