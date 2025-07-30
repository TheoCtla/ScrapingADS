#!/usr/bin/env python3
"""
Script de démarrage pour l'application de reporting publicitaire refactorisée
"""

import sys
import os

# Ajouter le répertoire parent au PYTHONPATH pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Importer et lancer l'application
if __name__ == "__main__":
    from backend.main import app, Config
    
    print("🚀 Démarrage du système de reporting publicitaire refactorisé")
    print("="*60)
    print(f"📍 Backend refactorisé - Port: {Config.FLASK.PORT}")
    print(f"🌐 Interface disponible sur: http://localhost:{Config.FLASK.PORT}")
    print("="*60)
    
    # Démarrer l'application
    app.run(
        debug=Config.FLASK.DEBUG,
        port=Config.FLASK.PORT,
        host='0.0.0.0'
    ) 