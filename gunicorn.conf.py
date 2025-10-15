"""
Configuration Gunicorn optimisée pour Render - Anti SIGKILL
"""

import os
import multiprocessing

# Configuration de base
bind = f"0.0.0.0:{os.getenv('PORT', 5000)}"
workers = int(os.getenv('WEB_CONCURRENCY', 1))
threads = 1
worker_class = "sync"
worker_connections = 1000

# Timeouts optimisés pour éviter les SIGKILL
timeout = 120
keepalive = 2
graceful_timeout = 30

# Limitation des requêtes pour éviter l'accumulation mémoire
max_requests = 200
max_requests_jitter = 50

# Préchargement pour optimiser les performances
preload_app = True

# Logging optimisé
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Variables d'environnement pour la mémoire
raw_env = [
    'PYTHONUNBUFFERED=1',
    'PYTHONDONTWRITEBYTECODE=1',
]

# Configuration mémoire
worker_tmp_dir = "/dev/shm" if os.path.exists("/dev/shm") else None

# Limitation des processus enfants
worker_max_requests_jitter = 50

# Configuration pour éviter les fuites mémoire
def when_ready(server):
    """Callback appelé quand le serveur est prêt"""
    server.log.info("🚀 Serveur Gunicorn optimisé démarré")

def worker_int(worker):
    """Callback appelé lors de l'interruption d'un worker"""
    worker.log.info("⚠️ Worker interrompu - nettoyage en cours")

def pre_fork(server, worker):
    """Callback appelé avant le fork d'un worker"""
    server.log.info(f"🔄 Démarrage worker {worker.pid}")

def post_fork(server, worker):
    """Callback appelé après le fork d'un worker"""
    server.log.info(f"✅ Worker {worker.pid} démarré")

def worker_abort(worker):
    """Callback appelé lors de l'abandon d'un worker"""
    worker.log.info(f"❌ Worker {worker.pid} abandonné")