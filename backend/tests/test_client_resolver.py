"""
Tests unitaires pour le service de résolution client
"""

import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import tempfile
import os

from backend.common.services.client_resolver import ClientResolverService

class TestClientResolverService(unittest.TestCase):
    """Tests pour le service de résolution client"""
    
    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.sample_config = {
            "version": "1.0",
            "allowlist": [
                "A.G. Cryolipolyse",
                "Addario",
                "Alexander Sachs",
                "AvivA Chartres",
                "Laserel"
            ],
            "mappings": {
                "A.G. Cryolipolyse": {
                    "googleAds": {"customerId": "9321943301"},
                    "metaAds": {"adAccountId": "537778268027569"}
                },
                "Addario": {
                    "googleAds": {"customerId": "1513412386"},
                    "metaAds": {"adAccountId": "588031303241243"}
                },
                "Alexander Sachs": {
                    "googleAds": {"customerId": "5312260895"},
                    "metaAds": None
                },
                "AvivA Chartres": {
                    "googleAds": {"customerId": "1364759792"},
                    "metaAds": {"adAccountId": "3469876616467752"}
                },
                "Laserel": {
                    "googleAds": None,
                    "metaAds": {"adAccountId": "5093614030719328"}
                }
            }
        }
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_load_allowlist_success(self, mock_json_load, mock_file):
        """Test du chargement réussi de la liste blanche"""
        mock_json_load.return_value = self.sample_config
        
        resolver = ClientResolverService()
        
        # Vérifier que la liste blanche est chargée
        self.assertEqual(len(resolver.allowlist), 5)
        self.assertIn("A.G. Cryolipolyse", resolver.allowlist)
        self.assertIn("Laserel", resolver.allowlist)
        
        # Vérifier que les mappings sont chargés
        self.assertEqual(len(resolver.mappings), 5)
        self.assertIn("A.G. Cryolipolyse", resolver.mappings)
    
    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_load_allowlist_file_not_found(self, mock_file):
        """Test du comportement quand le fichier de configuration n'existe pas"""
        resolver = ClientResolverService()
        
        self.assertEqual(resolver.allowlist, [])
        self.assertEqual(resolver.mappings, {})
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load', side_effect=json.JSONDecodeError("Invalid JSON", "", 0))
    def test_load_allowlist_invalid_json(self, mock_json_load, mock_file):
        """Test du comportement avec un JSON invalide"""
        resolver = ClientResolverService()
        
        self.assertEqual(resolver.allowlist, [])
        self.assertEqual(resolver.mappings, {})
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_get_allowlist_sorted(self, mock_json_load, mock_file):
        """Test que la liste blanche est retournée triée alphabétiquement"""
        mock_json_load.return_value = self.sample_config
        
        resolver = ClientResolverService()
        allowlist = resolver.get_allowlist()
        
        # Vérifier que la liste est triée
        expected_sorted = [
            "A.G. Cryolipolyse",
            "Addario", 
            "Alexander Sachs",
            "AvivA Chartres",
            "Laserel"
        ]
        self.assertEqual(allowlist, expected_sorted)
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_is_client_authorized(self, mock_json_load, mock_file):
        """Test de la validation d'autorisation client"""
        mock_json_load.return_value = self.sample_config
        
        resolver = ClientResolverService()
        
        # Clients autorisés
        self.assertTrue(resolver.is_client_authorized("A.G. Cryolipolyse"))
        self.assertTrue(resolver.is_client_authorized("Laserel"))
        
        # Clients non autorisés
        self.assertFalse(resolver.is_client_authorized("Client Inconnu"))
        self.assertFalse(resolver.is_client_authorized(""))
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_resolve_client_accounts_success(self, mock_json_load, mock_file):
        """Test de la résolution réussie des comptes client"""
        mock_json_load.return_value = self.sample_config
        
        resolver = ClientResolverService()
        
        # Client avec Google et Meta
        result = resolver.resolve_client_accounts("A.G. Cryolipolyse")
        self.assertEqual(result["googleAds"]["customerId"], "9321943301")
        self.assertEqual(result["metaAds"]["adAccountId"], "537778268027569")
        
        # Client avec Google seulement
        result = resolver.resolve_client_accounts("Alexander Sachs")
        self.assertEqual(result["googleAds"]["customerId"], "5312260895")
        self.assertIsNone(result["metaAds"])
        
        # Client avec Meta seulement
        result = resolver.resolve_client_accounts("Laserel")
        self.assertIsNone(result["googleAds"])
        self.assertEqual(result["metaAds"]["adAccountId"], "5093614030719328")
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_resolve_client_accounts_unauthorized(self, mock_json_load, mock_file):
        """Test de la résolution pour un client non autorisé"""
        mock_json_load.return_value = self.sample_config
        
        resolver = ClientResolverService()
        
        result = resolver.resolve_client_accounts("Client Inconnu")
        self.assertIsNone(result["googleAds"])
        self.assertIsNone(result["metaAds"])
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_get_available_platforms(self, mock_json_load, mock_file):
        """Test de la récupération des plateformes disponibles"""
        mock_json_load.return_value = self.sample_config
        
        resolver = ClientResolverService()
        
        # Client avec les deux plateformes
        platforms = resolver.get_available_platforms("A.G. Cryolipolyse")
        self.assertEqual(set(platforms), {"googleAds", "metaAds"})
        
        # Client avec Google seulement
        platforms = resolver.get_available_platforms("Alexander Sachs")
        self.assertEqual(platforms, ["googleAds"])
        
        # Client avec Meta seulement
        platforms = resolver.get_available_platforms("Laserel")
        self.assertEqual(platforms, ["metaAds"])
        
        # Client non autorisé
        platforms = resolver.get_available_platforms("Client Inconnu")
        self.assertEqual(platforms, [])
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_validate_client_selection(self, mock_json_load, mock_file):
        """Test de la validation de sélection client"""
        mock_json_load.return_value = self.sample_config
        
        resolver = ClientResolverService()
        
        # Sélection valide
        is_valid, error = resolver.validate_client_selection("A.G. Cryolipolyse")
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
        
        # Client non autorisé
        is_valid, error = resolver.validate_client_selection("Client Inconnu")
        self.assertFalse(is_valid)
        self.assertIn("non autorisé", error)
        
        # Aucun client sélectionné
        is_valid, error = resolver.validate_client_selection("")
        self.assertFalse(is_valid)
        self.assertIn("Aucun client sélectionné", error)
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_get_client_info(self, mock_json_load, mock_file):
        """Test de la récupération des informations client"""
        mock_json_load.return_value = self.sample_config
        
        resolver = ClientResolverService()
        
        # Client complet
        info = resolver.get_client_info("A.G. Cryolipolyse")
        self.assertEqual(info["name"], "A.G. Cryolipolyse")
        self.assertTrue(info["authorized"])
        self.assertEqual(set(info["available_platforms"]), {"googleAds", "metaAds"})
        self.assertTrue(info["google_ads"]["configured"])
        self.assertEqual(info["google_ads"]["customer_id"], "9321943301")
        self.assertTrue(info["meta_ads"]["configured"])
        self.assertEqual(info["meta_ads"]["ad_account_id"], "537778268027569")
        
        # Client Google seulement
        info = resolver.get_client_info("Alexander Sachs")
        self.assertEqual(info["available_platforms"], ["googleAds"])
        self.assertTrue(info["google_ads"]["configured"])
        self.assertFalse(info["meta_ads"]["configured"])
        
        # Client non autorisé
        info = resolver.get_client_info("Client Inconnu")
        self.assertEqual(info, {})

if __name__ == '__main__':
    unittest.main()
