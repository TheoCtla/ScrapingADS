# 📊 Système de Reporting Unifié Google Ads & Meta Ads

> **Plateforme de scraping et d'analyse de données publicitaires multi-plateformes**

Un système complet pour récupérer, analyser et consolider les données publicitaires de Google Ads et Meta Ads dans des Google Sheets automatisés. Développé pour optimiser le suivi des performances marketing multi-canal.

---

## 🚀 Fonctionnalités

### 📈 **Google Ads Integration**
- **Scraping automatisé** des comptes Google Ads clients
- **Métriques complètes** : Clics, Impressions, CTR, CPC, CPL, Conversions
- **Conversions spécialisées** : Contact et Itinéraires (objectifs personnalisés)
- **Export CSV** et **mise à jour Google Sheets** automatique
- **Gestion multi-clients** avec mapping automatique

### 📱 **Meta Ads Integration**
- **Récupération des insights** Meta Ads via Graph API
- **Métriques unifiées** : Clics, Impressions, CTR, CPC, CPL
- **Conversions Meta** : Contact et Recherche de lieux
- **Synchronisation** avec le même système Google Sheets
- **Mapping client-compte** automatisé

### 📋 **Google Sheets Automation**
- **Mise à jour automatique** des données dans Google Sheets
- **Structure intelligente** : détection automatique des onglets clients
- **Gestion des périodes** : mois et métriques dynamiques
- **Formatage professionnel** des données
- **Sécurité** : authentification Service Account

### 🎯 **Interface Utilisateur**
- **Dashboard React** moderne et responsive
- **Sélection de clients** intuitive
- **Périodes personnalisables** (date range picker)
- **Métriques configurables** (checkboxes par catégorie)
- **Export unifié** Google + Meta en un clic

### 🔧 **Architecture Technique**
- **Backend Flask** robuste et scalable
- **API RESTful** complète
- **Gestion d'erreurs** avancée
- **Logging** détaillé
- **Configuration centralisée** via variables d'environnement

---

## 📋 Prérequis

### 🛠️ **Outils de développement**
- **Python 3.8+** avec pip
- **Node.js 16+** avec npm
- **Git** pour la gestion de version

### 🔑 **APIs et Services**
- **Compte Google Ads** avec accès API
- **Compte Meta Business** avec accès Graph API
- **Google Sheets** avec permissions d'écriture
- **Google Cloud Project** (pour Service Account)

### 📁 **Fichiers de configuration**
- **Google Ads API** : `google-ads.yaml`
- **Google Sheets** : `credentials.json` (Service Account)
- **Variables d'environnement** : fichier `.env`, s'aider du fichier .env.exemple

---

## ⚙️ Installation

### 1. **Cloner le projet**
```bash
git clone <repository-url>
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

## 🔧 Configuration

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

## 📡 API Endpoints

| Route | Méthode | Description |
|-------|---------|-------------|
| `/list-customers` | GET | Liste des clients Google Ads |
| `/list-meta-accounts` | GET | Liste des comptes Meta Ads |
| `/export-report` | POST | Export Google Ads + mise à jour Sheets |
| `/export-unified-report` | POST | Export unifié Google + Meta |
| `/update_sheet` | POST | Mise à jour manuelle Google Sheets |

---

## 🚀 Utilisation

### Démarrage rapide
```bash
# Démarrer tous les services
./start_project.sh

### Interface utilisateur
1. **Ouvrir** http://localhost:3000
2. **Sélectionner** un client dans la liste
3. **Choisir** la période d'analyse
4. **Sélectionner** les métriques souhaitées
5. **Cliquer** sur "Télécharger les stats"
6. **Vérifier** la mise à jour dans Google Sheets

---

## 📁 Structure du Projet

```
scrappingRapport/
├── backend/
│   ├── config/
│   │   ├── credentials.json
│   │   ├── google-ads.yaml
│   │   ├── client_mappings.json
│   │   └── meta_mappings.json
│   ├── main.py
│   ├── config/settings.py
│   └── exports/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── .env
├── .env.exemple
├── start_project.sh
└── README.md
```

---

## 🛡️ Sécurité

- **Variables sensibles** dans `.env` (protégé par `.gitignore`)
- **Authentification** Service Account pour Google Sheets
- **Tokens d'API** sécurisés et renouvelables
- **Validation** des permissions et accès
- **Logging** sécurisé sans données sensibles

---

## 🔧 Développement

### Scripts utiles
```bash
# Démarrer le projet complet
./start_project.sh

# Démarrer uniquement le backend
./start_backend.sh

# Démarrer uniquement le frontend
cd frontend && npm run dev

# Nettoyer les processus
pkill -f "python.*main.py"
pkill -f "vite"
```

### Tests
```bash
# Test du backend
python -m pytest backend/tests/

# Test du frontend
cd frontend && npm test
```

---

## 📞 Support

Pour toute question ou problème :
- **Issues** : Créer une issue sur le repository
- **Documentation** : Consulter les fichiers de configuration
- **Logs** : Vérifier `backend.log` et `frontend.log`

---

## 📄 Licence

Ce projet est développé pour un usage interne et professionnel.

---

## 👨‍💻 Auteur

**Théo Catala**

- **LinkedIn** : [Théo Catala](https://www.linkedin.com/in/th%C3%A9o-catala-200841240/)

---

*Dernière mise à jour : 30 Juillet 2025* 