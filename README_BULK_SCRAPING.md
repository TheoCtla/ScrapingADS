# Fonctionnalité de Scraping en Masse

## Vue d'ensemble

La fonctionnalité "Scraper tous les clients" permet de traiter automatiquement tous les clients visibles dans la searchbar avec les mêmes paramètres sélectionnés par l'utilisateur.

## Fonctionnalités

### ✅ Fonctionnalités implémentées

1. **Bouton "Scraper tous les clients"** : Apparaît à côté du bouton d'export unitaire
2. **Traitement séquentiel** : Les clients sont traités un par un (pas de parallélisme)
3. **Réutilisation des fonctions existantes** : Utilise les mêmes endpoints et logique que le scraping unitaire
4. **Capture du contexte UI** : Les sélections (dates, métriques, plateformes) sont capturées au démarrage
5. **Barre de progression** : Affichage en temps réel de la progression (i/N)
6. **Gestion des erreurs** : Retry automatique (2 tentatives) avec backoff
7. **Annulation** : Bouton pour arrêter le traitement après l'étape en cours
8. **Résumé final** : Affichage des succès et échecs à la fin
9. **Logs détaillés** : Console avec informations sur chaque client traité

### 🔧 Architecture technique

#### Frontend
- **Composants** :
  - `BulkScrapingProgress` : Affichage de la progression
  - `UnifiedDownloadButton` : Bouton "Scraper tous" ajouté
  - `App.tsx` : Orchestration du scraping en masse

- **États** :
  - `bulkScrapingState` : État de progression et résultats
  - `authorizedClients` : Liste des clients autorisés
  - `filteredClients` : Clients visibles dans la searchbar

#### Backend
- **Endpoints** :
  - `/list-filtered-clients` : Nouveau endpoint pour simuler la searchbar
  - `/export-unified-report` : Réutilisé pour chaque client

- **Services** :
  - `ClientResolverService` : Résolution des clients
  - Services Google/Meta existants : Réutilisés sans modification

### 📋 Flux d'exécution

1. **Initialisation** :
   - Capture du contexte UI (dates, métriques, plateformes)
   - Récupération de la liste des clients filtrés
   - Validation des paramètres

2. **Traitement séquentiel** :
   - Pour chaque client :
     - Résolution des IDs Google/Meta
     - Appel à l'endpoint `/export-unified-report`
     - Retry en cas d'échec (max 2 tentatives)
     - Pause de 1s entre les clients

3. **Gestion des erreurs** :
   - Retry automatique avec backoff (2s, 4s)
   - Log des erreurs par client
   - Continuation du traitement malgré les échecs

4. **Finalisation** :
   - Affichage du résumé (succès/échecs)
   - Nettoyage de l'état

### 🎯 Utilisation

#### Démarrage du scraping en masse
1. Sélectionner les paramètres (dates, métriques, plateformes)
2. Cliquer sur "Scraper tous les clients"
3. Le traitement commence automatiquement

#### Suivi de la progression
- **Barre de progression** : Affichage visuel de l'avancement
- **Compteurs** : Progression (i/N), succès, échecs
- **Client en cours** : Nom du client actuellement traité
- **Logs console** : Informations détaillées

#### Annulation
- Cliquer sur "Annuler" pour arrêter après l'étape en cours
- Le traitement s'arrête proprement

#### Résultats
- **Résumé final** : Alert avec nombre de succès/échecs
- **Détail des échecs** : Liste des clients en échec avec erreurs
- **Persistance** : Les résultats restent visibles jusqu'au rechargement

### 🔒 Sécurité et contraintes

#### Sécurité
- Utilisation des mappings existants (pas d'exposition d'IDs)
- Validation des clients via la liste blanche
- Réutilisation des services d'authentification existants

#### Contraintes
- **Séquentiel strict** : Pas de parallélisme pour respecter les quotas
- **Rate limiting** : Pause de 2s entre les clients pour Google Sheets
- **Retry intelligent** : 3 tentatives avec backoff adaptatif
- **Gestion des quotas** : Détection automatique des erreurs 429
- **Contexte immuable** : Les sélections UI sont figées au démarrage

### 🧪 Tests

#### Tests unitaires
- `BulkScrapingProgress.test.tsx` : Tests du composant de progression
- Validation des props et interactions

#### Tests d'intégration (manuels)
1. **Scraping complet** : Tester avec 2-3 clients
2. **Gestion d'erreurs** : Simuler des erreurs API
3. **Annulation** : Tester l'arrêt en cours de traitement
4. **Contexte UI** : Vérifier que les sélections sont respectées

### 📝 Logs et monitoring

#### Logs console
```
📸 Contexte UI capturé: {startDate, endDate, metrics...}
🔄 Traitement 1/28: Client A
⏳ Pause de 2s entre les clients pour respecter les quotas
🔄 Traitement 2/28: Client B
⏳ Quota dépassé, attente de 30s
🔄 Retry 1/3 pour Client B
✅ Succès pour Client B
✅ Scraping en masse terminé
📊 Résultats: 25 succès, 3 échecs
```

#### Gestion des quotas
- **Détection automatique** des erreurs 429 (Google Sheets)
- **Retry adaptatif** : 30s, 60s, 90s pour les erreurs de quota
- **Backoff exponentiel** : 2s, 4s, 8s pour les autres erreurs
- **Pause entre clients** : 2 secondes pour respecter les limites

#### Monitoring
- Progression en temps réel
- Détection des timeouts et erreurs
- Métriques de performance

### 🔄 Évolutions futures

#### Améliorations possibles
1. **Filtrage avancé** : Utiliser le vrai terme de recherche de la searchbar
2. **Parallélisme contrôlé** : Traitement par batch avec limite de concurrence
3. **Persistance des résultats** : Sauvegarde des résultats en base
4. **Notifications** : Alertes email/Slack à la fin du traitement
5. **Planification** : Lancement automatique à des heures précises

#### Optimisations
1. **Cache des mappings** : Éviter les appels répétés
2. **Batch processing** : Traitement par groupe de clients
3. **Resume capability** : Reprendre après interruption
4. **Metrics avancées** : Temps de traitement, taux de succès

## Support et maintenance

### Débogage
- Vérifier les logs console pour les erreurs détaillées
- Contrôler les réponses API dans l'onglet Network
- Valider les mappings clients dans `client_allowlist.json`

### Maintenance
- Mise à jour des mappings clients
- Monitoring des quotas API Google/Meta
- Optimisation des timeouts et retries selon les performances
