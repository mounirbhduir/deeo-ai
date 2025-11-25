# 🐛 PROMPT CLAUDE CODE - FIX 2 BUGS STAGING DEEO.AI

**Projet** : DEEO.AI  
**Contexte** : Tests frontend STAGING - 2 bugs identifiés  
**Date** : 24 novembre 2025

---

## 🔴 BUG 1 : PAGE ORGANISATIONS BLANCHE

### Description
La page `/organisations` (http://localhost:5174/organisations) affiche une **page complètement blanche** au lieu d'afficher un message "Aucune organisation disponible".

### Comportement attendu
- Afficher un message explicite : "Aucune organisation disponible"
- Ou afficher un état vide avec une icône et un texte informatif
- La page ne doit PAS être blanche

### Données actuelles
```sql
-- 0 organisations en base STAGING
SELECT COUNT(*) FROM organisation; -- Résultat : 0
```

### Fichiers concernés
- `frontend/src/pages/OrganisationsList.tsx` (ou similaire)
- Possiblement un composant enfant qui crashe silencieusement

### Debug à effectuer
1. Vérifier si le composant OrganisationsList gère le cas `organisations.length === 0`
2. Vérifier la console pour erreurs JavaScript cachées
3. Vérifier que l'API `/api/v1/organisations` répond correctement (même avec liste vide)

### Solution attendue
```tsx
// Exemple de gestion état vide
if (!organisations || organisations.length === 0) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <Building2 className="h-16 w-16 text-gray-300 mb-4" />
      <h3 className="text-lg font-medium text-gray-900">Aucune organisation</h3>
      <p className="text-gray-500">Les organisations seront disponibles après enrichissement des données.</p>
    </div>
  );
}
```

---

## 🔴 BUG 2 : GRAPHES RÉSEAU ERREUR 404

### Description
La page `/graphs` (http://localhost:5174/graphs) affiche :
- **"Erreur de chargement du graphe"**
- **"Request failed with status code 404"**

### Erreurs Console (DevTools)
```
Failed to load resource: :8001/api/v1/graphs/...collaborations=1:1
the server responded with a status of 404 (Not Found)

API Error: Object
```

### Cause probable
L'endpoint API `/api/v1/graphs/` n'existe pas ou ne fonctionne pas correctement en environnement STAGING.

### Vérifications à effectuer

1. **Vérifier si l'endpoint existe dans le backend** :
   ```bash
   # Lister les routes API
   docker-compose -f docker-compose.staging.yml exec api python -c "from app.main import app; print([r.path for r in app.routes])"
   ```

2. **Tester l'endpoint directement** :
   ```bash
   curl http://localhost:8001/api/v1/graphs/collaborations
   ```

3. **Vérifier le fichier router** :
   - `backend/app/api/v1/graphs.py` (ou similaire)
   - `backend/app/api/v1/__init__.py` (vérifier si le router est inclus)

### Solutions possibles

#### Solution A : L'endpoint n'existe pas
Créer l'endpoint `/api/v1/graphs/collaborations` qui retourne les données de collaboration entre auteurs.

#### Solution B : L'endpoint existe mais crashe
Vérifier les logs backend :
```bash
docker-compose -f docker-compose.staging.yml logs -f api
```
Corriger l'erreur dans le service/repository.

#### Solution C : Frontend appelle mauvaise URL
Vérifier dans le frontend quel endpoint est appelé :
- `frontend/src/pages/NetworkGraph.tsx` (ou similaire)
- `frontend/src/services/api.ts` ou `frontend/src/api/`

### Données nécessaires pour le graphe
Le graphe de collaboration nécessite :
- Auteurs (nodes) : 1199 disponibles ✅
- Relations co-auteurs (edges) : Basées sur publications partagées

```sql
-- Vérifier si les relations existent
SELECT COUNT(*) FROM publication_auteur; -- Relations publication-auteur
```

---

## 🎯 MISSION CLAUDE CODE

### Ordre de priorité

1. **D'abord BUG 1** (Page Organisations) - Plus simple, juste du frontend
2. **Ensuite BUG 2** (Graphes 404) - Peut nécessiter backend + frontend

### Étapes recommandées

#### Pour BUG 1 :
1. Ouvrir `frontend/src/pages/OrganisationsList.tsx`
2. Identifier pourquoi la page est blanche (erreur ? pas de gestion état vide ?)
3. Ajouter gestion explicite du cas `length === 0`
4. Tester sur http://localhost:5174/organisations

#### Pour BUG 2 :
1. Vérifier si endpoint `/api/v1/graphs/` existe dans backend
2. Si non, créer l'endpoint ou adapter le frontend pour gérer l'absence
3. Si oui, debug pourquoi il retourne 404
4. Tester sur http://localhost:5174/graphs

---

## 🖥️ ENVIRONNEMENT

- **Frontend** : http://localhost:5174
- **Backend API** : http://localhost:8001/docs
- **Docker** : `docker-compose.staging.yml`

### Commandes utiles

```bash
# Logs frontend
docker-compose -f docker-compose.staging.yml logs -f frontend

# Logs backend (pour voir erreurs 404)
docker-compose -f docker-compose.staging.yml logs -f api

# Tester endpoint API
curl http://localhost:8001/api/v1/organisations
curl http://localhost:8001/api/v1/graphs/collaborations

# Vérifier routes disponibles
curl http://localhost:8001/openapi.json | grep -o '"\/api\/v1\/[^"]*"' | sort -u
```

---

## ✅ CRITÈRES DE SUCCÈS

### BUG 1 - Organisations
- [ ] Page `/organisations` affiche un message "Aucune organisation" (pas page blanche)
- [ ] Pas d'erreur console JavaScript
- [ ] Style cohérent avec le reste de l'application

### BUG 2 - Graphes
- [ ] Page `/graphs` ne montre plus erreur 404
- [ ] Soit : graphe s'affiche (si données suffisantes)
- [ ] Soit : message explicite "Graphe non disponible - données insuffisantes"
- [ ] Pas d'erreur console JavaScript

---

## 📸 CAPTURES D'ÉCRAN DE RÉFÉRENCE

### BUG 1 - Page Organisations (actuel : page blanche)
- URL : http://localhost:5174/organisations
- Problème : Page complètement vide/blanche

### BUG 2 - Page Graphes (actuel : erreur 404)
- URL : http://localhost:5174/graphs
- Message : "Erreur de chargement du graphe - Request failed with status code 404"
- Console : `Failed to load resource: :8001/api/v1/graphs/...collaborations=1:1 - 404`

---

## 🚀 PHRASE DE DÉMARRAGE

```
J'ai 2 bugs à corriger sur le frontend STAGING DEEO.AI :

BUG 1 : La page /organisations est complètement blanche au lieu d'afficher "Aucune organisation" (0 organisations en base).

BUG 2 : La page /graphs affiche "Erreur 404" car l'endpoint /api/v1/graphs/collaborations n'existe pas ou ne fonctionne pas.

Commence par le BUG 1 (plus simple). Ouvre le fichier OrganisationsList.tsx et vérifie pourquoi la page est blanche.
```

---

**Bonne chance !** 🚀
