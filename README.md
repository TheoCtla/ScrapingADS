# ScrappingRapport - Système de Reporting Unifié

Application de scraping et reporting pour Google Ads et Meta Ads avec export vers Google Sheets.

## 🚀 Démarrage Rapide

```bash
# Installation et démarrage
./start_project.sh

# Accès
Frontend: http://localhost:3000
Backend: http://localhost:5050
```

## 📋 Fonctionnalités

- **Sélection unifiée de clients** : Une seule barre de recherche avec liste blanche de 28 clients autorisés
- **Scraping ciblé** : Récupération des données uniquement pour le client sélectionné
- **Google Ads** : Métriques de campagnes et calculs virtuels
- **Meta Ads** : Insights et métriques formatées
- **Export Google Sheets** : Mise à jour automatique des feuilles sur le Sheet

## 🔧 Configuration


### Variables d'environnement

```bash
# Meta
META_ACCESS_TOKEN=
META_BUSINESS_ID=

# Google
GOOGLE_SHEET_ID=
GOOGLE_CREDENTIALS_FILE=/etc/secrets/credentials.json
GOOGLE_ADS_YAML_PATH=/etc/secrets/google-ads.yaml

#Flask
FLASK_DEBUG=True
FLASK_PORT=5050
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001


#frontend
VITE_API_URL=https://scrapingads.onrender.com
VITE_APP_NAME=ScrappingRapport
VITE_APP_VERSION=1.0.0

#drive
GOOGLE_DRIVE_FOLDER_ID=
```

## 📁 Structure

```
scrappingRapport/
├── backend/
│   ├── config/
│   │   ├── client_allowlist.json    # Liste blanche des clients
│   │   └── settings.py              # Configuration
│   ├── common/services/
│   │   ├── client_resolver.py       # Résolution des clients
│   │   └── google_sheets.py         # Export Google Sheets
│   ├── google/services/             # Services Google Ads
│   ├── meta/services/               # Services Meta Ads
│   └── main.py                      # API Flask
├── frontend/
│   └── src/components/              # Composants React
└── start_project.sh                 # Script de démarrage
```

## 🛠️ API Endpoints

- `GET /list-authorized-clients` - Liste des clients autorisés
- `POST /resolve-client` - Résolution des IDs client
- `POST /export-unified-report` - Export vers Google Sheets


## 📝 Logs

```bash
# Backend
tail -f backend.log

# Frontend
tail -f frontend.log
```
