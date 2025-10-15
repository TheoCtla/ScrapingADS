# 🚀 Guide de Déploiement Render - Anti SIGKILL

## 📋 Variables d'Environnement Requises

### Variables Obligatoires
```bash
# Google Ads API
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_DEVELOPER_TOKEN=your_token
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token

# Meta Ads API
META_ACCESS_TOKEN=your_access_token

# Google Sheets
GOOGLE_SHEETS_CREDENTIALS_FILE=path/to/credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id
```

### Variables d'Optimisation (Recommandées)
```bash
# Configuration Gunicorn
WEB_CONCURRENCY=1
GUNICORN_WORKERS=1
GUNICORN_THREADS=1
GUNICORN_TIMEOUT=120
GUNICORN_MAX_REQUESTS=200
GUNICORN_MAX_REQUESTS_JITTER=50

# Configuration Python
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
PYTHON_VERSION=3.11.0
```

## 🔧 Configuration Render

### 1. Plan Recommandé
- **Plan**: Starter (512MB RAM)
- **Région**: Oregon (US West)
- **Auto-deploy**: Activé

### 2. Build Command
```bash
pip install -r backend/requirements.txt
```

### 3. Start Command
```bash
gunicorn backend.main:app -c gunicorn.conf.py
```

### 4. Health Check
- **Path**: `/healthz`
- **Timeout**: 30s

## 📊 Monitoring et Debugging

### Endpoints de Monitoring
- `GET /healthz` - Santé de l'application
- `GET /concurrency-status` - État de concurrence
- `GET /` - Status général

### Logs à Surveiller
```bash
# Rechercher ces patterns dans les logs Render
grep "SIGKILL\|out of memory\|MemoryError" logs
grep "Slot acquis\|Slot libéré" logs
grep "Worker.*démarré\|Worker.*abandonné" logs
```

## 🚨 Résolution des Problèmes

### SIGKILL "Out of Memory"
1. **Vérifier la concurrence** :
   ```bash
   curl https://your-app.onrender.com/concurrency-status
   ```

2. **Forcer la libération des slots** (si nécessaire) :
   ```python
   from backend.common.utils.concurrency_manager import force_release_all
   force_release_all()
   ```

3. **Utiliser le mode léger** :
   - Endpoint `/scrape-light-contact` au lieu de `/export-unified-report`
   - Endpoint `/scrape-light-directions` pour les itinéraires

### Timeouts
- Vérifier `GUNICORN_TIMEOUT=120`
- Utiliser les endpoints légers pour les opérations longues
- Surveiller les logs de concurrence

## 🔄 Mise à Jour

### Variables d'Environnement à Ajouter
```bash
# Nouvelles variables pour l'optimisation
WEB_CONCURRENCY=1
GUNICORN_WORKERS=1
GUNICORN_THREADS=1
GUNICORN_TIMEOUT=120
GUNICORN_MAX_REQUESTS=200
GUNICORN_MAX_REQUESTS_JITTER=50
```

### Fichiers à Déployer
- `gunicorn.conf.py` (nouveau)
- `backend/common/utils/concurrency_manager.py` (nouveau)
- `backend/common/services/light_scraper.py` (nouveau)
- `Procfile` (modifié)
- `requirements.txt` (modifié)

## 📈 Optimisations Appliquées

### 1. Limitation de Concurrence
- **1 worker, 1 thread** maximum
- **Sémaphore global** pour les opérations de scraping
- **Timeouts stricts** (120s max)

### 2. Mode Scraping Léger
- **Sans navigateur** (requests + BeautifulSoup)
- **Endpoints dédiés** pour les opérations légères
- **Timeouts courts** (30s)

### 3. Configuration Gunicorn
- **Max requests limitées** (200 + jitter)
- **Graceful shutdown** (30s)
- **Logging optimisé**

### 4. Nettoyage Mémoire
- **Garbage collection** automatique
- **Libération des slots** après chaque opération
- **Session HTTP** réutilisée

## ✅ Checklist Post-Deploy

- [ ] Variables d'environnement configurées
- [ ] Health check `/healthz` fonctionne
- [ ] Concurrency status `/concurrency-status` accessible
- [ ] Mode léger `/scrape-light-contact` testé
- [ ] Logs sans erreurs SIGKILL
- [ ] Performance acceptable (< 30s par requête)

## 🆘 Support

En cas de problème :
1. Vérifier les logs Render
2. Tester `/concurrency-status`
3. Utiliser les endpoints légers
4. Contacter l'équipe de développement