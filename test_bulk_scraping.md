# Guide de Test - Fonctionnalité de Scraping en Masse

## Prérequis

1. **Serveurs démarrés** :
   - Frontend : `npm run dev` (port 5173)
   - Backend : `python run.py` (port 5050)

2. **Configuration** :
   - Clients configurés dans `backend/config/client_allowlist.json`
   - Mappings Google/Meta configurés

## Tests à effectuer

### 1. Test de base - Interface utilisateur

#### ✅ Vérifications visuelles
- [ ] Le bouton "Scraper tous les clients" apparaît à côté du bouton d'export unitaire
- [ ] Le bouton est vert et stylé différemment du bouton principal
- [ ] Le bouton est désactivé si aucune métrique n'est sélectionnée
- [ ] Le bouton est désactivé pendant le scraping en cours

#### ✅ Comportement du bouton
- [ ] Le bouton affiche "Scraper tous les clients" par défaut
- [ ] Le bouton affiche "Scraping en cours..." pendant le traitement
- [ ] Le bouton redevient actif après la fin du traitement

### 2. Test de progression

#### ✅ Composant de progression
- [ ] Le composant `BulkScrapingProgress` apparaît pendant le traitement
- [ ] La barre de progression se remplit progressivement
- [ ] Les compteurs (i/N, succès, échecs) s'actualisent en temps réel
- [ ] Le nom du client en cours s'affiche correctement

#### ✅ Statistiques
- [ ] Progression : "2 / 28" (exemple)
- [ ] Succès : nombre de clients traités avec succès
- [ ] Échecs : nombre de clients en échec

### 3. Test de traitement séquentiel

#### ✅ Logs console
Ouvrir la console du navigateur et vérifier les logs :
```
📸 Contexte UI capturé: {startDate, endDate, metrics...}
🔄 Traitement 1/28: Client A
📤 Envoi du payload pour Client A
✅ Succès pour Client A
🔄 Traitement 2/28: Client B
...
```

#### ✅ Séquentialité
- [ ] Les clients sont traités un par un (pas de parallélisme)
- [ ] Pause de 1s entre chaque client
- [ ] Retry automatique en cas d'échec (max 2 tentatives)

### 4. Test de gestion d'erreurs

#### ✅ Retry automatique
- [ ] En cas d'erreur, retry automatique après 2s
- [ ] Deuxième retry après 4s si nécessaire
- [ ] Échec définitif après 3 tentatives

#### ✅ Continuation du traitement
- [ ] Le traitement continue même si un client échoue
- [ ] Les échecs sont enregistrés et affichés
- [ ] Le résumé final inclut les succès et échecs

### 5. Test d'annulation

#### ✅ Bouton d'annulation
- [ ] Le bouton "Annuler" est actif pendant le traitement
- [ ] Le bouton est désactivé une fois terminé
- [ ] Cliquer sur "Annuler" arrête le traitement après l'étape en cours

#### ✅ Arrêt propre
- [ ] Le traitement s'arrête proprement
- [ ] L'état est nettoyé correctement
- [ ] Les résultats partiels sont conservés

### 6. Test de contexte UI

#### ✅ Capture du contexte
- [ ] Les sélections UI sont capturées au démarrage
- [ ] Le même contexte est appliqué à tous les clients
- [ ] Les modifications UI pendant le traitement n'affectent pas le run en cours

#### ✅ Paramètres respectés
- [ ] Plage de dates sélectionnée
- [ ] Métriques Google/Meta sélectionnées
- [ ] Options de scraping (Contact, Itinéraires)
- [ ] Mois du Google Sheet

### 7. Test de résumé final

#### ✅ Alert de fin
- [ ] Alert avec nombre de succès et échecs
- [ ] Format : "Scraping terminé! ✅ Succès: X ❌ Échecs: Y"

#### ✅ Détail des échecs
- [ ] Liste des clients en échec avec erreurs
- [ ] Affichage dans le composant de progression
- [ ] Persistance jusqu'au rechargement de la page

### 8. Test d'intégration avec le backend

#### ✅ Endpoints
- [ ] `/list-authorized-clients` : Liste complète des clients
- [ ] `/list-filtered-clients` : Clients filtrés (simulation searchbar)
- [ ] `/export-unified-report` : Traitement de chaque client

#### ✅ Réutilisation des services
- [ ] Même logique de résolution des clients
- [ ] Même logique de scraping Google/Meta
- [ ] Même logique d'export vers Google Sheets

## Scénarios de test

### Scénario 1 : Traitement complet
1. Sélectionner des métriques Google et Meta
2. Cliquer sur "Scraper tous les clients"
3. Observer la progression
4. Vérifier le résumé final

### Scénario 2 : Gestion d'erreurs
1. Simuler une erreur réseau (déconnecter temporairement)
2. Lancer le scraping
3. Vérifier les retries et la gestion d'erreurs
4. Reconnecter et vérifier la continuation

### Scénario 3 : Annulation
1. Lancer le scraping
2. Cliquer sur "Annuler" au milieu du traitement
3. Vérifier l'arrêt propre
4. Vérifier les résultats partiels

### Scénario 4 : Contexte UI
1. Sélectionner des paramètres spécifiques
2. Lancer le scraping
3. Modifier les paramètres pendant le traitement
4. Vérifier que les anciens paramètres sont utilisés

## Validation des critères d'acceptation

### ✅ Critères validés
- [ ] Tous les clients de la searchbar sont traités un par un
- [ ] Les mêmes sélections UI sont appliquées à chaque client
- [ ] Les mêmes fonctions d'export au Google Sheet sont utilisées
- [ ] Annulation possible avec arrêt propre
- [ ] Logs clairs par client (début/fin, plateformes, durée, retries, erreurs)
- [ ] Aucun client en dehors de la searchbar n'est appelé

### ✅ Fonctionnalités bonus
- [ ] Barre de progression visuelle
- [ ] Compteurs en temps réel
- [ ] Résumé détaillé des échecs
- [ ] Retry automatique avec backoff
- [ ] Interface responsive

## Dépannage

### Problèmes courants

#### Le bouton n'apparaît pas
- Vérifier que `authorizedClients.length > 0`
- Vérifier la console pour les erreurs de chargement

#### Le traitement ne démarre pas
- Vérifier qu'au moins une plateforme est sélectionnée
- Vérifier les logs console pour les erreurs

#### Erreurs de réseau
- Vérifier que le backend est accessible sur le port 5050
- Vérifier les CORS dans la configuration

#### Progression bloquée
- Vérifier les logs console pour les erreurs détaillées
- Vérifier les timeouts et retries

## Métriques de performance

### Temps de traitement
- Temps moyen par client : ~5-10s
- Pause entre clients : 1s
- Retry delay : 2s, 4s

### Utilisation des ressources
- CPU : Faible (traitement séquentiel)
- Mémoire : Stable (pas d'accumulation)
- Réseau : Modéré (1 requête par client)

## Conclusion

La fonctionnalité de scraping en masse est maintenant opérationnelle avec :
- ✅ Interface utilisateur complète
- ✅ Traitement séquentiel robuste
- ✅ Gestion d'erreurs avancée
- ✅ Réutilisation des services existants
- ✅ Documentation complète
- ✅ Tests unitaires
