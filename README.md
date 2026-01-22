# ScrappingRapport - Système de Reporting Unifié

Application de scraping et reporting pour Google Ads et Meta Ads avec export vers Google Sheets.

## Fonctionnalités

- **Sélection unifiée de clients** : Une seule barre de recherche avec liste blanche de 28 clients autorisés
- **Scraping ciblé** : Récupération des données uniquement pour le client sélectionné
- **Google Ads** : Métriques de campagnes et calculs virtuels
- **Meta Ads** : Insights et métriques formatées
- **Export Google Sheets** : Mise à jour automatique des feuilles sur le Sheet

## Configuration

### Ajouter un client

1. Éditer `backend/config/client_allowlist.json`
2. Ajouter le nom du client dans `allowlist`
3. Configurer les mappings Google Ads et/ou Meta Ads

## Structure

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

## API Endpoints

- `GET /list-authorized-clients` - Liste des clients autorisés
- `POST /resolve-client` - Résolution des IDs client
- `POST /export-unified-report` - Export vers Google Sheets

# Installation
### Backend
```bash
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt
```

### Frontend
```bash
cd frontend
npm install
```
### .env
```bash
cd ..
cp .env.exemple .env
```

## Démarrage Rapide

```bash
./start_project.sh

# Accès
Frontend: http://localhost:3000
Backend: http://localhost:5050
```

## Logs

```bash
# Backend
tail -f backend.log

# Frontend
tail -f frontend.log
```
