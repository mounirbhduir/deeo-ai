# 🚀 PROMPT CLAUDE CODE - FIX STAGING DEEO.AI

**Projet** : DEEO.AI - AI Dynamic Emergence and Evolution Observatory  
**Contexte** : Environnement STAGING avec données arXiv partielles  
**Objectif** : Faire fonctionner le frontend + enrichir les données  
**Date** : 24 novembre 2025

---

## 📌 CONTEXTE CRITIQUE (À LIRE EN PREMIER)

### Situation Actuelle

L'environnement **STAGING** est opérationnel avec des données **réelles mais incomplètes** :

| Entité | Quantité | Problème |
|--------|----------|----------|
| **Publications** | 251 | ✅ OK (arXiv) |
| **Auteurs** | 1199 | ⚠️ Sans h-index, sans affiliations |
| **Organisations** | **0** | 🔴 VIDE (pas dans arXiv) |

### Pourquoi le Frontend Crash ?

**arXiv fournit** :
- ✅ Titre, abstract, date
- ✅ Noms des auteurs
- ✅ Catégories (cs.AI, cs.LG, etc.)
- ✅ arXiv ID

**arXiv NE fournit PAS** :
- ❌ `auteur.h_index` → null
- ❌ `auteur.nombre_citations` → 0
- ❌ `auteur.semantic_scholar_id` → null
- ❌ `publication.nombre_citations` → 0
- ❌ `publication.doi` → null (souvent)
- ❌ Affiliations → pas d'organisations

**Le frontend assume que ces champs existent** → Erreurs JavaScript !

---

## 🎯 MISSION EN 2 PHASES

### PHASE A : FALLBACKS FRONTEND (Priorité 1) ⚡

**Objectif** : Faire fonctionner le frontend avec les données actuelles (251 publications)

**Tâches** :

1. **Créer `frontend/src/utils/dataHelpers.ts`** :
   - Fonctions `safeAuthor()`, `safePublication()`, `safeOrganisation()`
   - Valeurs par défaut pour tous les champs potentiellement null
   - Export propre pour utilisation dans composants

2. **Identifier et modifier les composants qui crashent** :
   - Probablement : `AuthorProfile.tsx`, `PublicationCard.tsx`, `OrganisationProfile.tsx`
   - Dashboard, statistiques, graphiques
   - Tout composant affichant h-index, citations, organisations

3. **Ajouter gestion des états vides** :
   - "Aucune organisation disponible" si liste vide
   - "H-index non disponible" si null
   - "Citations : N/A" si pas enrichi

4. **Tester** :
   - Naviguer sur toutes les pages sans erreur console
   - Vérifier que les données s'affichent (même si partielles)

**Critères de succès Phase A** :
- ✅ Frontend accessible sur http://localhost:5174 sans erreur console
- ✅ Dashboard affiche les 251 publications
- ✅ Profils auteurs affichent "H-index : N/A" au lieu de crash
- ✅ Pages organisations gèrent état vide gracieusement

---

### PHASE B : ENRICHISSEMENT SEMANTIC SCHOLAR (Priorité 2) 🔧

**Objectif** : Enrichir les données avec Semantic Scholar API

**Tâches** :

1. **Vérifier/Créer le service d'enrichissement** :
   - Fichier : `backend/app/pipelines/semantic_scholar_enricher.py`
   - Utiliser l'API Semantic Scholar (gratuite, 100 req/5 min)
   - Enrichir : citations, h-index, affiliations

2. **Données à récupérer depuis Semantic Scholar** :
   ```python
   # Pour chaque publication (via DOI ou titre)
   publication.nombre_citations = paper['citationCount']
   publication.influential_citations = paper['influentialCitationCount']
   
   # Pour chaque auteur (via nom ou ID)
   auteur.h_index = author['hIndex']
   auteur.semantic_scholar_id = author['authorId']
   auteur.nombre_citations = author['citationCount']
   
   # Affiliations → créer organisations
   for affiliation in author['affiliations']:
       organisation = get_or_create(affiliation['name'])
       link_author_to_organisation(auteur, organisation)
   ```

3. **Gérer le rate limiting** :
   - 100 requêtes / 5 minutes
   - Ajouter délai entre requêtes (3 secondes)
   - Retry avec backoff exponentiel si erreur 429

4. **Script d'exécution** :
   ```bash
   # Enrichir toutes les publications
   docker-compose -f docker-compose.staging.yml exec api \
     python -m app.pipelines.semantic_scholar_enricher --all
   ```

**Critères de succès Phase B** :
- ✅ Script d'enrichissement fonctionne sans erreur
- ✅ Publications ont `nombre_citations > 0` (au moins certaines)
- ✅ Auteurs ont `h_index` renseigné
- ✅ Organisations créées (> 50)
- ✅ Frontend affiche données enrichies

---

## 📁 STRUCTURE FICHIERS À MODIFIER/CRÉER

### Phase A (Frontend)

```
frontend/src/
├── utils/
│   └── dataHelpers.ts          🆕 CRÉER
├── components/
│   ├── AuthorProfile.tsx       📝 MODIFIER
│   ├── PublicationCard.tsx     📝 MODIFIER
│   ├── OrganisationProfile.tsx 📝 MODIFIER
│   ├── Dashboard/
│   │   └── StatsCards.tsx      📝 MODIFIER (si existe)
│   └── ...
└── pages/
    ├── AuthorsPage.tsx         📝 VÉRIFIER
    ├── OrganisationsPage.tsx   📝 VÉRIFIER
    └── ...
```

### Phase B (Backend)

```
backend/app/
├── pipelines/
│   ├── semantic_scholar_enricher.py  📝 VÉRIFIER/AMÉLIORER
│   └── arxiv_pipeline.py             ✅ EXISTANT
├── services/
│   └── enrichment_service.py         🆕 CRÉER SI NÉCESSAIRE
└── scripts/
    └── enrich_staging_data.py        🆕 CRÉER
```

---

## 🔧 EXEMPLE CODE ATTENDU

### dataHelpers.ts (Phase A)

```typescript
// frontend/src/utils/dataHelpers.ts

export interface SafeAuthor {
  id: number;
  nom: string;
  prenom: string | null;
  h_index: number;
  nombre_publications: number;
  nombre_citations: number;
  semantic_scholar_id: string | null;
  orcid: string | null;
  email: string | null;
}

export const safeAuthor = (author: any): SafeAuthor => ({
  id: author?.id ?? 0,
  nom: author?.nom ?? 'Inconnu',
  prenom: author?.prenom ?? null,
  h_index: author?.h_index ?? 0,
  nombre_publications: author?.nombre_publications ?? 0,
  nombre_citations: author?.nombre_citations ?? 0,
  semantic_scholar_id: author?.semantic_scholar_id ?? null,
  orcid: author?.orcid ?? null,
  email: author?.email ?? null,
});

export const safePublication = (pub: any) => ({
  id: pub?.id ?? 0,
  titre: pub?.titre ?? 'Sans titre',
  abstract: pub?.abstract ?? '',
  date_publication: pub?.date_publication ?? null,
  nombre_citations: pub?.nombre_citations ?? 0,
  nombre_auteurs: pub?.nombre_auteurs ?? pub?.auteurs?.length ?? 0,
  doi: pub?.doi ?? null,
  arxiv_id: pub?.arxiv_id ?? null,
  url: pub?.url ?? null,
  type_publication: pub?.type_publication ?? 'article',
  source: pub?.source ?? 'arXiv',
  auteurs: (pub?.auteurs ?? []).map(safeAuthor),
  themes: pub?.themes ?? [],
});

export const safeOrganisation = (org: any) => ({
  id: org?.id ?? 0,
  nom: org?.nom ?? 'Organisation inconnue',
  nom_court: org?.nom_court ?? null,
  type_organisation: org?.type_organisation ?? 'other',
  pays: org?.pays ?? null,
  ville: org?.ville ?? null,
  nombre_publications: org?.nombre_publications ?? 0,
  nombre_chercheurs: org?.nombre_chercheurs ?? 0,
  ranking_mondial: org?.ranking_mondial ?? null,
  url: org?.url ?? null,
});

// Helper pour affichage conditionnel
export const displayValue = (value: any, fallback: string = 'N/A'): string => {
  if (value === null || value === undefined) return fallback;
  if (typeof value === 'number' && value === 0) return fallback;
  return String(value);
};

// Helper pour listes vides
export const hasData = (arr: any[]): boolean => {
  return Array.isArray(arr) && arr.length > 0;
};
```

### Exemple Modification Composant

```typescript
// AVANT (crash si author.h_index est null)
const AuthorCard = ({ author }) => (
  <div>
    <h3>{author.nom}</h3>
    <p>H-index: {author.h_index}</p>  {/* 💥 CRASH si null */}
  </div>
);

// APRÈS (avec fallback)
import { safeAuthor, displayValue } from '@/utils/dataHelpers';

const AuthorCard = ({ author }) => {
  const safe = safeAuthor(author);
  return (
    <div>
      <h3>{safe.nom}</h3>
      <p>H-index: {displayValue(safe.h_index, 'Non disponible')}</p>
    </div>
  );
};
```

---

## 🖥️ ENVIRONNEMENT DE TRAVAIL

### Accès STAGING

- **Frontend** : http://localhost:5174
- **Backend API** : http://localhost:8001/docs
- **PostgreSQL** : localhost:5433 (user: deeo_user, db: deeo_ai_staging)

### Commandes Utiles

```bash
# Vérifier services UP
docker-compose -f docker-compose.staging.yml ps

# Logs frontend
docker-compose -f docker-compose.staging.yml logs -f frontend

# Logs backend
docker-compose -f docker-compose.staging.yml logs -f api

# Accès PostgreSQL
docker-compose -f docker-compose.staging.yml exec postgres psql -U deeo_user -d deeo_ai_staging

# Compter données
docker-compose -f docker-compose.staging.yml exec postgres psql -U deeo_user -d deeo_ai_staging -c "SELECT COUNT(*) FROM publication;"
```

### Données Actuelles

```sql
-- Publications : 251
-- Auteurs : 1199
-- Organisations : 0 (vide!)
-- Thèmes : ~10-15 (catégories arXiv)
```

---

## ✅ CHECKLIST DE VALIDATION

### Phase A (Frontend)

- [ ] `dataHelpers.ts` créé avec toutes les fonctions safe
- [ ] Composants modifiés pour utiliser helpers
- [ ] Aucune erreur console sur http://localhost:5174
- [ ] Dashboard affiche données (même partielles)
- [ ] Page auteurs fonctionne
- [ ] Page publications fonctionne
- [ ] Page organisations gère état vide
- [ ] Graphe réseau fonctionne (si applicable)

### Phase B (Enrichissement)

- [ ] Script enrichissement créé/amélioré
- [ ] Rate limiting géré (100 req/5 min)
- [ ] Test sur 10 publications d'abord
- [ ] Enrichissement complet lancé
- [ ] Vérification données en base après enrichissement
- [ ] Frontend affiche données enrichies

---

## 🎬 APPROCHE RECOMMANDÉE

### Ordre d'Exécution

1. **D'abord** : Lire et comprendre la structure frontend existante
2. **Ensuite** : Créer `dataHelpers.ts`
3. **Puis** : Identifier les composants qui utilisent les données
4. **Modifier** : Composants un par un, tester à chaque modification
5. **Valider** : Navigation complète sans erreur
6. **Enfin** : Passer à Phase B (enrichissement)

### Tips

- **Utiliser la console DevTools** pour identifier les erreurs
- **Modifier UN composant à la fois** et vérifier
- **Committer après chaque correction** fonctionnelle
- **Tester sur http://localhost:5174** après chaque modification

---

## 🚀 PHRASE DE LANCEMENT CLAUDE CODE

```
Je travaille sur DEEO.AI (projet thèse). L'environnement STAGING a 251 publications arXiv mais le frontend crash car les données ne sont pas enrichies (h_index null, organisations vides, etc.).

Mission en 2 phases :
1. PHASE A : Créer des fallbacks frontend pour gérer les données null
2. PHASE B : Enrichir les données avec Semantic Scholar API

Commence par la PHASE A : crée le fichier dataHelpers.ts et identifie les composants à modifier.
```

---

## 📚 RÉFÉRENCES

- **Frontend** : `frontend/src/` (React + TypeScript + Vite)
- **Backend** : `backend/app/` (FastAPI + SQLAlchemy)
- **Docker** : `docker-compose.staging.yml`
- **API Semantic Scholar** : https://api.semanticscholar.org/

---

**Bonne chance avec Claude Code !** 🚀

**"Excellence is our standard. Quality is our commitment. Impact is our goal."**

---

**Prompt généré le** : 24 novembre 2025  
**Version** : 1.0  
**Projet** : DEEO.AI - Master Big Data & AI (UIR)
