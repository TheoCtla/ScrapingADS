# Système de Reporting Unifié Google Ads & Meta Ads

> **Plateforme de scraping et d'analyse de données publicitaires multi-plateformes**

Un système complet pour récupérer, analyser et consolider les données publicitaires de Google Ads et Meta Ads dans des Google Sheets automatisés. Développé pour optimiser le suivi des performances marketing multi-canal.

---

## Fonctionnalités

### **Sélection Unifiée de Clients**
- **Liste blanche centralisée** des clients autorisés
- **Sélection unique** via une interface unifiée
- **Résolution automatique** des IDs Google Ads et Meta Ads
- **Validation stricte** contre la liste blanche
- **Gestion des plateformes manquantes** avec messages informatifs

### **Google Ads Integration**
- **Scraping ciblé** des comptes Google Ads clients
- **Métriques complètes** : Clics, Impressions, CTR, CPC, CPL, Conversions
- **Conversions spécialisées** : Contact et Itinéraires (objectifs personnalisés)
- **Export CSV** et **mise à jour Google Sheets** automatique
- **Mapping client-compte** centralisé et versionné

### **Meta Ads Integration**
- **Récupération des insights** Meta Ads via Graph API
- **Métriques unifiées** : Clics, Impressions, CTR, CPC, CPL
- **Conversions Meta** : Contact et Recherche de lieux
- **Synchronisation** avec le même système Google Sheets
- **Mapping client-compte** centralisé et versionné

### **Google Sheets Automation**
- **Mise à jour automatique** des données dans Google Sheets
- **Structure intelligente** : détection automatique des onglets clients
- **Gestion des périodes** : mois et métriques dynamiques
- **Formatage professionnel** des données
- **Sécurité** : authentification Service Account

### **Interface Utilisateur**
- **Dashboard React** moderne et responsive
- **Sélection de clients** intuitive
- **Périodes personnalisables** (date range picker)
- **Métriques configurables** (checkboxes par catégorie)
- **Export unifié** Google + Meta en un clic

### **Architecture Technique**
- **Backend Flask** robuste et scalable
- **API RESTful** complète
- **Gestion d'erreurs** avancée
- **Logging** détaillé
- **Configuration centralisée** via variables d'environnement

---

## Prérequis

### **Outils de développement**
- **Python 3.8+** avec pip
- **Node.js 16+** avec npm
- **Git** pour la gestion de version

### **APIs et Services**
- **Compte Google Ads** avec accès API
- **Compte Meta Business** avec accès Graph API
- **Google Sheets** avec permissions d'écriture
- **Google Cloud Project** (pour Service Account)

### **Fichiers de configuration**
- **Google Ads API** : `google-ads.yaml`
- **Google Sheets** : `credentials.json` (Service Account)
- **Variables d'environnement** : fichier `.env`, s'aider du fichier .env.exemple

---

## Installation

### 1. **Cloner le projet**
```bash
git clone <https://github.com/TheoCtla/ScrapingADS.git>
cd scrappingRapport
```

### 2. **Configuration des variables d'environnement**
```bash
# Créer le fichier .env avec les variables nécessaires (aidez-vous du .env.exemple)
```

### 3. **Backend (Python/Flask)**
```bash
# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install flask flask-cors python-dotenv google-api-python-client google-auth google-ads requests

# Démarrer le serveur
./start_project.sh
```

### 4. **Frontend (React)**
```bash
cd frontend
npm install
npm run dev
```

---

## Configuration

### Configuration Google Sheets

1. **Créer un projet Google Cloud**
2. **Activer les APIs** : Google Sheets API, Google Ads API
3. **Créer un Service Account** et télécharger `credentials.json`
4. **Placer** `credentials.json` dans `backend/config/`
5. **Partager** votre Google Sheet avec l'email du Service Account

### Configuration Google Ads

1. **Créer** un fichier `google-ads.yaml` dans `backend/config/`
2. **Créer** un fichier `credentials.json` dans `backend/config/`
3. **Vérifier** les permissions sur les comptes clients

---

## API Endpoints

| Route | Méthode | Description |
|-------|---------|-------------|
| `/list-authorized-clients` | GET | Liste des clients autorisés (liste blanche) |
| `/resolve-client` | POST | Résolution nom client → IDs Google/Meta |
| `/export-unified-report` | POST | Export unifié Google + Meta (nouveau format) |
| `/update_sheet` | POST | Mise à jour manuelle Google Sheets |
| `/list-customers` | GET | Liste des clients Google Ads (LEGACY) |
| `/list-meta-accounts` | GET | Liste des comptes Meta Ads (LEGACY) |
| `/export-report` | POST | Export Google Ads + mise à jour Sheets (LEGACY) |

---

## Utilisation

### Démarrage rapide
```bash
# Démarrer tous les services
./start_project.sh

### Interface utilisateur
1. **Ouvrir** http://localhost:3000
2. **Sélectionner** un client autorisé dans la liste blanche
3. **Choisir** la période d'analyse, la période pré remplie est le dernier mois entier
4. **Sélectionner** les métriques souhaitées (Google Ads et/ou Meta Ads)
5. **Vérifier** la mise à jour dans Google Sheets

---

## Structure du Projet


scrappingRapport/
├── backend/
│   ├── config/
│   │   ├── credentials.json
│   │   ├── google-ads.yaml
│   │   ├── client_allowlist.json
│   │   ├── client_mappings.json
│   │   └── meta_mappings.json
│   ├── common/
│   │   └── services/
│   │       └── client_resolver.py
│   ├── main.py
│   ├── config/settings.py
│   ├── tests/
│   │   └── test_client_resolver.py
│   └── exports/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── unified/
│   │   │   │   └── ClientSelector/
│   │   │   ├── google/
│   │   │   └── meta/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── .env
├── .env.exemple
├── start_project.sh
├── README.md
└── README_MAINTAINERS.md
```

---

## Sécurité

- **Variables sensibles** dans `.env` (protégé par `.gitignore`)
- **Authentification** Service Account pour Google Sheets
- **Tokens d'API** sécurisés et renouvelables
- **Validation** des permissions et accès
- **Logging** sécurisé sans données sensibles

---

## Développement

### Scripts utiles
```bash
# Démarrer le projet complet
./start_project.sh
```

### Tests
```bash
# Test du backend
python -m pytest backend/tests/

# Test du frontend
cd frontend && npm test
```

---

## Changelog

### Version 2.0 - Refonte Unifiée (Janvier 2025)
- ✅ **Liste blanche centralisée** : Remplacement des deux sélecteurs par un système unifié
- ✅ **Sélection unique** : Interface simplifiée avec une seule barre de recherche
- ✅ **Scraping ciblé** : Plus de scraping global, uniquement le client sélectionné
- ✅ **Mapping centralisé** : Configuration unifiée dans `client_allowlist.json`
- ✅ **Gestion d'erreurs robuste** : Messages informatifs pour les plateformes manquantes
- ✅ **Tests unitaires** : Couverture complète du service de résolution client
- ✅ **Documentation** : Guide de maintenance pour les mainteneurs

### Version 1.0 - Système Initial
- Système de scraping Google Ads et Meta Ads
- Interface avec sélecteurs séparés
- Export vers Google Sheets

---

## Support

Pour toute question ou problème :
- **Issues** : Créer une issue sur le repository
- **Documentation** : Consulter les fichiers de configuration et `README_MAINTAINERS.md`
- **Logs** : Vérifier `backend.log` et `frontend.log`

---

## Licence

Ce projet est développé pour un usage interne et professionnel.

---

## Auteur

**Théo Catala**

- **LinkedIn** : [Théo Catala](https://www.linkedin.com/in/th%C3%A9o-catala-200841240/)

---

*Dernière mise à jour : 30 Juillet 2025* 
