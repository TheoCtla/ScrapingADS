"""
Tests de performance pour éviter les SIGKILL sur Render
"""

import pytest
import time
import requests
import threading
from concurrent.futures import ThreadPoolExecutor
from backend.common.utils.concurrency_manager import concurrency_manager, get_concurrency_status
from backend.common.services.light_scraper import LightScraperService

class TestConcurrencyLimits:
    """Tests pour vérifier la limitation de concurrence"""
    
    def test_concurrency_manager_initialization(self):
        """Test l'initialisation du gestionnaire de concurrence"""
        status = get_concurrency_status()
        assert status["max_concurrent"] == 1
        assert status["active_operations"] == 0
        assert status["available_slots"] == 1
    
    def test_single_operation_acquires_slot(self):
        """Test qu'une opération peut acquérir un slot"""
        acquired = concurrency_manager.acquire("test_operation")
        assert acquired is True
        
        status = get_concurrency_status()
        assert status["active_operations"] == 1
        assert status["available_slots"] == 0
        
        # Nettoyer
        concurrency_manager.release("test_operation")
    
    def test_concurrent_operations_limited(self):
        """Test que les opérations concurrentes sont limitées"""
        # Premier slot
        acquired1 = concurrency_manager.acquire("operation_1")
        assert acquired1 is True
        
        # Deuxième slot (devrait échouer)
        acquired2 = concurrency_manager.acquire("operation_2")
        assert acquired2 is False
        
        # Vérifier le statut
        status = get_concurrency_status()
        assert status["active_operations"] == 1
        assert status["available_slots"] == 0
        
        # Nettoyer
        concurrency_manager.release("operation_1")
    
    def test_slot_release_works(self):
        """Test que la libération de slot fonctionne"""
        # Acquérir un slot
        concurrency_manager.acquire("test_release")
        
        # Vérifier qu'il est occupé
        status = get_concurrency_status()
        assert status["active_operations"] == 1
        
        # Libérer
        concurrency_manager.release("test_release")
        
        # Vérifier qu'il est libéré
        status = get_concurrency_status()
        assert status["active_operations"] == 0
        assert status["available_slots"] == 1

class TestLightScraper:
    """Tests pour le scraper léger"""
    
    def test_light_scraper_initialization(self):
        """Test l'initialisation du scraper léger"""
        scraper = LightScraperService()
        assert scraper is not None
        assert scraper.session is not None
        assert scraper.timeout == 30
    
    def test_mock_contact_conversions(self):
        """Test les conversions Contact simulées"""
        scraper = LightScraperService()
        result = scraper.scrape_contact_conversions_light("TestClient", "2024-01-01", "2024-01-31")
        
        assert result["success"] is True
        assert "total_conversions" in result
        assert "method" in result
        assert result["method"] == "light_scraper"
    
    def test_mock_directions_conversions(self):
        """Test les conversions Itinéraires simulées"""
        scraper = LightScraperService()
        result = scraper.scrape_directions_conversions_light("TestClient", "2024-01-01", "2024-01-31")
        
        assert result["success"] is True
        assert "total_conversions" in result
        assert "method" in result
        assert result["method"] == "light_scraper"
    
    def test_phone_number_extraction(self):
        """Test l'extraction de numéros de téléphone"""
        scraper = LightScraperService()
        content = "Contactez-nous au 01 23 45 67 89 ou 06 12 34 56 78"
        phones = scraper.extract_phone_numbers(content)
        
        assert len(phones) > 0
        assert any("01" in phone for phone in phones)
    
    def test_email_extraction(self):
        """Test l'extraction d'emails"""
        scraper = LightScraperService()
        content = "Email: contact@example.com ou info@test.fr"
        emails = scraper.extract_emails(content)
        
        assert len(emails) > 0
        assert "contact@example.com" in emails
        assert "info@test.fr" in emails

class TestPerformanceLimits:
    """Tests de performance pour éviter les SIGKILL"""
    
    def test_memory_usage_stable(self):
        """Test que l'utilisation mémoire reste stable"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Simuler plusieurs opérations
        for i in range(10):
            scraper = LightScraperService()
            result = scraper.scrape_contact_conversions_light(f"Client{i}", "2024-01-01", "2024-01-31")
            scraper.close()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # L'augmentation mémoire ne devrait pas dépasser 50MB
        assert memory_increase < 50 * 1024 * 1024, f"Mémoire augmentée de {memory_increase / 1024 / 1024:.2f}MB"
    
    def test_concurrent_requests_limited(self):
        """Test que les requêtes concurrentes sont limitées"""
        results = []
        
        def make_request():
            try:
                acquired = concurrency_manager.acquire("concurrent_test")
                if acquired:
                    time.sleep(0.1)  # Simuler une opération
                    concurrency_manager.release("concurrent_test")
                    results.append("success")
                else:
                    results.append("blocked")
            except Exception as e:
                results.append(f"error: {e}")
        
        # Lancer 5 requêtes simultanées
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            for future in futures:
                future.result()
        
        # Seule une requête devrait réussir, les autres être bloquées
        assert results.count("success") == 1
        assert results.count("blocked") == 4
    
    def test_timeout_handling(self):
        """Test la gestion des timeouts"""
        # Acquérir le seul slot disponible
        concurrency_manager.acquire("timeout_test")
        
        # Essayer d'acquérir un autre slot avec timeout court
        start_time = time.time()
        acquired = concurrency_manager.wait_for_slot(timeout=1)
        end_time = time.time()
        
        # Devrait échouer après ~1 seconde
        assert acquired is False
        assert 0.9 <= (end_time - start_time) <= 1.5
        
        # Nettoyer
        concurrency_manager.release("timeout_test")

class TestIntegration:
    """Tests d'intégration pour l'API"""
    
    def test_health_endpoint(self, client):
        """Test l'endpoint de santé"""
        response = client.get('/healthz')
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
    
    def test_concurrency_status_endpoint(self, client):
        """Test l'endpoint de statut de concurrence"""
        response = client.get('/concurrency-status')
        assert response.status_code == 200
        data = response.get_json()
        assert "concurrency" in data
        assert "timestamp" in data
    
    def test_light_scraping_endpoints(self, client):
        """Test les endpoints de scraping léger"""
        # Test Contact
        response = client.post('/scrape-light-contact', json={
            "client_name": "TestClient",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        
        # Test Directions
        response = client.post('/scrape-light-directions', json={
            "client_name": "TestClient",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

# Fixtures pour les tests
@pytest.fixture
def client():
    """Fixture pour le client de test Flask"""
    from backend.main import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Tests de charge (à exécuter séparément)
class TestLoadTesting:
    """Tests de charge pour valider les performances"""
    
    def test_sustained_load(self, client):
        """Test de charge soutenue"""
        start_time = time.time()
        successful_requests = 0
        failed_requests = 0
        
        # Faire 20 requêtes sur 30 secondes
        for i in range(20):
            try:
                response = client.get('/healthz')
                if response.status_code == 200:
                    successful_requests += 1
                else:
                    failed_requests += 1
            except Exception:
                failed_requests += 1
            
            time.sleep(1.5)  # 1.5s entre les requêtes
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Vérifier que la plupart des requêtes réussissent
        success_rate = successful_requests / (successful_requests + failed_requests)
        assert success_rate >= 0.8, f"Taux de succès trop faible: {success_rate:.2%}"
        assert duration <= 35, f"Test trop long: {duration:.2f}s"
    
    def test_memory_under_load(self, client):
        """Test de mémoire sous charge"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Faire plusieurs requêtes de scraping léger
        for i in range(5):
            response = client.post('/scrape-light-contact', json={
                "client_name": f"LoadTestClient{i}",
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            })
            assert response.status_code == 200
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # L'augmentation mémoire ne devrait pas dépasser 100MB
        assert memory_increase < 100 * 1024 * 1024, f"Mémoire augmentée de {memory_increase / 1024 / 1024:.2f}MB"
