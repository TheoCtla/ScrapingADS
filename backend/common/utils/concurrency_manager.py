"""
Gestionnaire de concurrence global pour éviter les SIGKILL sur Render
"""

import asyncio
import threading
import time
import logging
from typing import Optional, Callable, Any
from functools import wraps
from contextlib import asynccontextmanager

class ConcurrencyManager:
    """Gestionnaire de concurrence global pour limiter les opérations simultanées"""
    
    def __init__(self, max_concurrent: int = 1):
        self.max_concurrent = max_concurrent
        self._semaphore = threading.Semaphore(max_concurrent)
        self._active_operations = 0
        self._lock = threading.Lock()
        
    def get_status(self) -> dict:
        """Retourne le statut actuel de la concurrence"""
        with self._lock:
            return {
                "max_concurrent": self.max_concurrent,
                "active_operations": self._active_operations,
                "available_slots": self.max_concurrent - self._active_operations
            }
    
    def acquire(self, operation_name: str = "unknown") -> bool:
        """Acquiert un slot pour une opération"""
        acquired = self._semaphore.acquire(blocking=False)
        if acquired:
            with self._lock:
                self._active_operations += 1
            logging.info(f"🔒 Slot acquis pour '{operation_name}' - Actifs: {self._active_operations}/{self.max_concurrent}")
        else:
            logging.warning(f"⚠️ Impossible d'acquérir un slot pour '{operation_name}' - Tous les slots sont occupés")
        return acquired
    
    def release(self, operation_name: str = "unknown"):
        """Libère un slot après une opération"""
        with self._lock:
            self._active_operations = max(0, self._active_operations - 1)
        self._semaphore.release()
        logging.info(f"🔓 Slot libéré pour '{operation_name}' - Actifs: {self._active_operations}/{self.max_concurrent}")
    
    def wait_for_slot(self, timeout: int = 60) -> bool:
        """Attend qu'un slot soit disponible"""
        try:
            acquired = self._semaphore.acquire(timeout=timeout)
            if acquired:
                with self._lock:
                    self._active_operations += 1
                logging.info(f"🔒 Slot acquis après attente - Actifs: {self._active_operations}/{self.max_concurrent}")
            return acquired
        except Exception as e:
            logging.error(f"❌ Erreur lors de l'attente d'un slot: {e}")
            return False

# Instance globale
concurrency_manager = ConcurrencyManager(max_concurrent=1)

def with_concurrency_limit(operation_name: str = "scraping_operation", timeout: int = 60):
    """Décorateur pour limiter la concurrence des opérations de scraping"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Essayer d'acquérir un slot
            if not concurrency_manager.acquire(operation_name):
                # Si pas de slot disponible, attendre
                logging.info(f"⏳ Attente d'un slot disponible pour '{operation_name}'...")
                if not concurrency_manager.wait_for_slot(timeout):
                    raise Exception(f"Timeout: Impossible d'acquérir un slot pour '{operation_name}' après {timeout}s")
            
            try:
                logging.info(f"Début de l'opération '{operation_name}'")
                start_time = time.time()
                
                # Exécuter la fonction
                result = func(*args, **kwargs)
                
                execution_time = time.time() - start_time
                logging.info(f"Opération '{operation_name}' terminée en {execution_time:.2f}s")
                
                return result
                
            except Exception as e:
                logging.error(f"Erreur dans l'opération '{operation_name}': {e}")
                raise
            finally:
                # Toujours libérer le slot
                concurrency_manager.release(operation_name)
        
        return wrapper
    return decorator

def get_concurrency_status() -> dict:
    """Retourne le statut de concurrence pour le monitoring"""
    return concurrency_manager.get_status()

@asynccontextmanager
async def async_concurrency_limit(operation_name: str = "async_scraping", timeout: int = 60):
    """Context manager asynchrone pour limiter la concurrence"""
    acquired = False
    try:
        # Pour les opérations asynchrones, on utilise une approche simplifiée
        # car asyncio.Semaphore n'est pas thread-safe avec threading.Semaphore
        if concurrency_manager.acquire(operation_name):
            acquired = True
            logging.info(f"🔒 Slot acquis pour '{operation_name}' (async)")
            yield
        else:
            raise Exception(f"Aucun slot disponible pour '{operation_name}'")
    finally:
        if acquired:
            concurrency_manager.release(operation_name)
            logging.info(f"🔓 Slot libéré pour '{operation_name}' (async)")

# Fonction utilitaire pour vérifier la disponibilité
def is_slot_available() -> bool:
    """Vérifie si un slot est disponible sans l'acquérir"""
    status = concurrency_manager.get_status()
    return status["available_slots"] > 0

# Fonction pour forcer la libération (en cas d'urgence)
def force_release_all():
    """Force la libération de tous les slots (à utiliser avec précaution)"""
    with concurrency_manager._lock:
        concurrency_manager._active_operations = 0
    # Réinitialiser le semaphore
    concurrency_manager._semaphore = threading.Semaphore(concurrency_manager.max_concurrent)
    logging.warning("⚠️ Tous les slots ont été forcés à la libération")
