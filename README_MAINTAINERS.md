# Guide de Maintenance - Système de Reporting Unifié

## 📋 **Gestion de la Liste Blanche des Clients**

### **Ajouter un nouveau client**

1. **Éditer le fichier de configuration** : `backend/config/client_allowlist.json`

2. **Ajouter le nom du client dans la liste blanche** :
   ```json
   {
     "allowlist": [
       "A.G. Cryolipolyse",
       "Nouveau Client",  // ← Ajouter ici
       "Addario"
     ]
   }
   ```

3. **Configurer les mappings** :
   ```json
   {
     "mappings": {
       "Nouveau Client": {
         "googleAds": {
           "customerId": "1234567890"  // ID Google Ads (optionnel)
         },
         "metaAds": {
           "adAccountId": "act_987654321"  // ID Meta Ads (optionnel)
         }
       }
     }
   }
   ```

4. **Récupérer les IDs** :
   - **Google Ads** : Utiliser l'endpoint `/list-customers` (legacy) ou consulter l'interface Google Ads
   - **Meta Ads** : Utiliser l'endpoint `/list-meta-accounts` (legacy) ou consulter l'interface Meta Business Manager

### **Supprimer un client**

1. **Retirer le nom de la liste blanche** :
   ```json
   {
     "allowlist": [
       "A.G. Cryolipolyse",
       // "Client à supprimer" ← Retirer cette ligne
       "Addario"
     ]
   }
   ```

2. **Supprimer le mapping correspondant** :
   ```json
   {
     "mappings": {
       // "Client à supprimer": { ... } ← Supprimer tout ce bloc
       "Addario": { ... }
     }
   }
   ```

### **Modifier la configuration d'un client existant**

1. **Changer les IDs** :
   ```json
   {
     "mappings": {
       "Client Existant": {
         "googleAds": {
           "customerId": "nouveau_id_google"  // ← Modifier ici
         },
         "metaAds": {
           "adAccountId": "nouveau_id_meta"  // ← Modifier ici
         }
       }
     }
   }
   ```

2. **Désactiver une plateforme** :
   ```json
   {
     "mappings": {
       "Client Existant": {
         "googleAds": null,  // ← Désactiver Google Ads
         "metaAds": {
           "adAccountId": "act_123456789"
         }
       }
     }
   }
   ```

## 🔧 **Validation et Tests**

### **Vérifier la configuration**

1. **Redémarrer le backend** pour charger la nouvelle configuration
2. **Tester l'endpoint** `/list-authorized-clients` pour vérifier que le client apparaît
3. **Tester l'endpoint** `/resolve-client` avec le nom du client pour vérifier les mappings

### **Tests automatisés**

```bash
# Lancer les tests unitaires
cd backend
python -m pytest tests/test_client_resolver.py -v

# Lancer tous les tests
python -m pytest tests/ -v
```

## 📊 **Structure de la Configuration**

### **Format du fichier `client_allowlist.json`**

```json
{
  "version": "1.0",
  "description": "Liste blanche des clients autorisés",
  "last_updated": "YYYY-MM-DD",
  "allowlist": [
    "Nom Client 1",
    "Nom Client 2"
  ],
  "mappings": {
    "Nom Client 1": {
      "googleAds": {
        "customerId": "1234567890"
      },
      "metaAds": {
        "adAccountId": "act_987654321"
      }
    },
    "Nom Client 2": {
      "googleAds": null,  // Pas de Google Ads
      "metaAds": {
        "adAccountId": "act_111222333"
      }
    }
  }
}
```

### **Règles de nommage**

- **Noms de clients** : Utiliser exactement le même nom dans `allowlist` et `mappings`
- **IDs Google Ads** : Format numérique (ex: "1234567890")
- **IDs Meta Ads** : Format avec préfixe "act_" (ex: "act_123456789")

## 🚨 **Points d'attention**

### **Sécurité**
- ✅ Toujours valider les IDs avant de les ajouter
- ✅ Vérifier les permissions d'accès aux comptes
- ✅ Tester en environnement de développement d'abord

### **Performance**
- ✅ La liste blanche est chargée au démarrage du service
- ✅ Les modifications nécessitent un redémarrage du backend
- ✅ Éviter d'ajouter des clients inutiles

### **Compatibilité**
- ✅ Maintenir la compatibilité avec les mappings existants
- ✅ Vérifier que les noms correspondent aux onglets Google Sheets
- ✅ Tester l'export après modification

## 🔍 **Dépannage**

### **Problèmes courants**

1. **Client non trouvé** :
   - Vérifier l'orthographe exacte du nom
   - Vérifier que le client est dans la liste blanche
   - Redémarrer le backend après modification

2. **IDs incorrects** :
   - Vérifier le format des IDs
   - Tester l'accès aux comptes via les APIs
   - Consulter les logs du backend

3. **Mapping manquant** :
   - Vérifier que le mapping existe dans la configuration
   - Vérifier la structure JSON
   - Redémarrer le backend

### **Logs utiles**

```bash
# Vérifier les logs du backend
tail -f backend.log | grep -i "client\|allowlist\|mapping"

# Vérifier le chargement de la configuration
grep -i "liste blanche\|mappings" backend.log
```

## 📞 **Support**

Pour toute question ou problème :
- Consulter les logs du backend
- Vérifier la configuration JSON
- Tester les endpoints de résolution
- Contacter l'équipe de développement
