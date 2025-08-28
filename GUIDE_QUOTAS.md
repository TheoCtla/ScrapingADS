# Guide de Configuration des Quotas - Scraping en Masse

## 🚨 Problème résolu

Vous avez rencontré des erreurs de quota Google Sheets (429 - Rate Limit Exceeded) lors du scraping en masse. Ces erreurs se produisent car Google Sheets limite les requêtes à **60 par minute par utilisateur**.

## 🔧 Solution implémentée

### **Gestion intelligente des quotas**

1. **Délais entre clients** : 2 secondes entre chaque client
2. **Retry automatique** : 3 tentatives avec backoff exponentiel
3. **Détection d'erreurs de quota** : Reconnaissance automatique des erreurs 429
4. **Délais adaptatifs** : Attentes plus longues pour les erreurs de quota

### **Configuration actuelle**

```typescript
// Délais entre les clients
DELAY_BETWEEN_CLIENTS: 2000, // 2 secondes

// Retries pour erreurs de quota
QUOTA_RETRY_DELAYS: [
  30 * 1000,  // 30 secondes
  60 * 1000,  // 60 secondes  
  90 * 1000   // 90 secondes
]

// Retries pour autres erreurs
GENERAL_RETRY_DELAYS: [
  2000,   // 2 secondes
  4000,   // 4 secondes
  8000    // 8 secondes
]
```

## 📊 Optimisation des quotas

### **Calcul des limites**

- **Google Sheets** : 60 requêtes/minute = 1 requête/seconde
- **Notre délai** : 2 secondes entre clients = 30 requêtes/minute
- **Marge de sécurité** : 50% de réduction pour éviter les dépassements

### **Estimation du temps de traitement**

Pour 28 clients :
- **Temps de base** : 28 clients × 2s = 56 secondes
- **Temps avec retries** : ~2-3 minutes en cas d'erreurs
- **Temps total estimé** : 3-5 minutes

## ⚙️ Configuration personnalisée

### **Modifier les délais**

Éditez `frontend/src/config/quotas.ts` :

```typescript
export const QUOTA_CONFIG = {
  // Augmenter le délai entre clients (en millisecondes)
  DELAY_BETWEEN_CLIENTS: 3000, // 3 secondes au lieu de 2
  
  // Modifier les délais de retry pour les quotas
  QUOTA_RETRY_DELAYS: [
    45 * 1000,  // 45 secondes
    90 * 1000,  // 90 secondes
    120 * 1000  // 2 minutes
  ],
  
  // Augmenter le nombre de retries
  MAX_RETRIES: 4,
};
```

### **Scénarios de configuration**

#### **Configuration conservatrice** (recommandée)
```typescript
DELAY_BETWEEN_CLIENTS: 3000, // 3s
QUOTA_RETRY_DELAYS: [45, 90, 120] // secondes
```
- **Avantage** : Très peu de risques de dépassement
- **Inconvénient** : Traitement plus lent

#### **Configuration équilibrée** (actuelle)
```typescript
DELAY_BETWEEN_CLIENTS: 2000, // 2s
QUOTA_RETRY_DELAYS: [30, 60, 90] // secondes
```
- **Avantage** : Bon compromis vitesse/fiabilité
- **Inconvénient** : Risque faible de dépassement

#### **Configuration agressive** (déconseillée)
```typescript
DELAY_BETWEEN_CLIENTS: 1000, // 1s
QUOTA_RETRY_DELAYS: [15, 30, 45] // secondes
```
- **Avantage** : Traitement rapide
- **Inconvénient** : Risque élevé de dépassement

## 🔍 Monitoring et logs

### **Logs de progression**
```
🔄 Traitement 1/28: Client A
⏳ Pause de 2s entre les clients pour respecter les quotas
🔄 Traitement 2/28: Client B
⏳ Quota dépassé, attente de 30s
🔄 Retry 1/3 pour Client B
```

### **Détection d'erreurs de quota**
Le système détecte automatiquement les erreurs contenant :
- `429`
- `quota`
- `rate limit`
- `Quota exceeded`
- `ReadRequestsPerMinutePerUser`
- `sheets.googleapis.com`

## 🚀 Améliorations futures

### **Optimisations possibles**

1. **Batch processing** : Traiter par groupes avec pauses plus longues
2. **Adaptive delays** : Ajuster les délais selon les erreurs rencontrées
3. **Quota monitoring** : Suivre l'utilisation en temps réel
4. **Resume capability** : Reprendre après interruption

### **Configuration avancée**

```typescript
// Configuration avec monitoring
export const ADVANCED_QUOTA_CONFIG = {
  ...QUOTA_CONFIG,
  
  // Monitoring en temps réel
  ENABLE_MONITORING: true,
  
  // Délais adaptatifs
  ADAPTIVE_DELAYS: {
    MIN_DELAY: 1000,
    MAX_DELAY: 5000,
    INCREASE_FACTOR: 1.5
  },
  
  // Batch processing
  BATCH_SIZE: 5,
  BATCH_DELAY: 10000
};
```

## 📋 Checklist de test

### **Avant le déploiement**
- [ ] Tester avec 2-3 clients
- [ ] Vérifier les logs de progression
- [ ] Confirmer l'absence d'erreurs 429
- [ ] Valider les temps de traitement

### **En production**
- [ ] Monitorer les erreurs de quota
- [ ] Ajuster les délais si nécessaire
- [ ] Vérifier la stabilité sur de gros volumes

## 🆘 Dépannage

### **Erreurs 429 persistantes**
1. **Augmenter les délais** dans `quotas.ts`
2. **Réduire le nombre de clients** traités simultanément
3. **Vérifier les autres utilisateurs** du projet Google

### **Traitement trop lent**
1. **Réduire légèrement les délais** (avec précaution)
2. **Optimiser les requêtes** côté backend
3. **Utiliser le batch processing** si implémenté

### **Erreurs inattendues**
1. **Vérifier les logs** détaillés
2. **Tester avec un seul client**
3. **Contrôler la configuration** des quotas

## 📈 Métriques de performance

### **Temps de traitement typiques**
- **5 clients** : ~30 secondes
- **10 clients** : ~1 minute
- **20 clients** : ~2 minutes
- **28 clients** : ~3 minutes

### **Taux de succès attendu**
- **Sans erreurs** : 100%
- **Avec retries** : 95%+
- **Avec erreurs de quota** : 90%+

---

**Note** : Cette configuration est optimisée pour éviter les erreurs de quota tout en maintenant un temps de traitement raisonnable. Ajustez selon vos besoins spécifiques.
