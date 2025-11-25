# 🔴 PROMPT CLAUDE CODE - BUG CRITIQUE MANY-TO-MANY PUBLICATIONS-AUTEURS

**Projet** : DEEO.AI  
**Contexte** : STAGING avec 251 publications et 1199 auteurs  
**Bug** : Relations Many-to-Many entre publications et auteurs mal gérées  
**Date** : 24 novembre 2025

---

## 🔴 DESCRIPTION DU BUG CRITIQUE

### Symptômes

1. **Fiche publication** : Affiche correctement plusieurs auteurs (ex: "Kastreva, Whittington, Komm et 1 autres")
2. **Page auteurs** (`/authors`) : Chaque auteur n'a qu'**une seule publication** alors qu'ils devraient en avoir plusieurs
3. **Recherche publications** : Rechercher par nom d'auteur ne retourne pas toutes ses publications

### Données Actuelles

```
Publications : 251
Auteurs : 1199

Ratio : 1199 / 251 = ~4.77 auteurs par publication en moyenne
```

**Conclusion** : Il y a forcément des auteurs qui ont co-écrit PLUSIEURS publications !

---

## 📊 STRUCTURE BASE DE DONNÉES (CORRECTE)

### Table d'Association `publication_auteur` (Many-to-Many)

```sql
CREATE TABLE publication_auteur (
    publication_id UUID NOT NULL,  -- FK vers publication(id)
    auteur_id UUID NOT NULL,       -- FK vers auteur(id)
    ordre INTEGER NOT NULL,         -- Position dans la liste d'auteurs
    role VARCHAR(50),               -- Ex: "first_author", "corresponding"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (publication_id, auteur_id),
    UNIQUE (publication_id, ordre)
);
```

**Cette table EXISTE déjà dans la base de données !**

### Vérification des Données

```sql
-- Vérifier combien de relations existent
SELECT COUNT(*) FROM publication_auteur;
-- Attendu : ~1199 relations (4.77 x 251)

-- Exemple : Trouver auteurs avec plusieurs publications
SELECT auteur_id, COUNT(*) as nb_publications 
FROM publication_auteur 
GROUP BY auteur_id 
HAVING COUNT(*) > 1
ORDER BY nb_publications DESC
LIMIT 10;

-- Vérifier pour une publication spécifique
SELECT p.titre, COUNT(pa.auteur_id) as nb_auteurs
FROM publication p
JOIN publication_auteur pa ON p.id = pa.publication_id
GROUP BY p.id, p.titre
ORDER BY nb_auteurs DESC
LIMIT 5;
```

---

## 🔍 DIAGNOSTIC : OÙ EST LE BUG ?

### Hypothèse 1 : Backend API - Repositories (TRÈS PROBABLE)

**Fichier** : `backend/app/repositories/auteur_repository.py`

**Problème** : La méthode qui récupère les publications d'un auteur ne fait probablement pas le JOIN avec `publication_auteur`.

**Code actuel (incorrect)** :
```python
# ❌ INCORRECT - Query directe sans JOIN
async def get_publications(self, auteur_id: int):
    result = await self.session.execute(
        select(Publication).where(Publication.auteur_id == auteur_id)
        # ❌ PAS DE JOIN avec publication_auteur !
    )
    return result.scalars().all()
```

**Code attendu (correct)** :
```python
# ✅ CORRECT - JOIN avec table d'association
async def get_publications(self, auteur_id: int):
    result = await self.session.execute(
        select(Publication)
        .join(PublicationAuteur, Publication.id == PublicationAuteur.publication_id)
        .where(PublicationAuteur.auteur_id == auteur_id)
        .order_by(PublicationAuteur.ordre)  # Respecter ordre co-auteurs
    )
    return result.scalars().all()
```

---

### Hypothèse 2 : Backend API - Services (POSSIBLE)

**Fichier** : `backend/app/services/auteur_service.py`

Vérifier que le service n'ajoute pas de filtre incorrect ou ne limite pas le nombre de publications.

---

### Hypothèse 3 : Backend API - Endpoints (MOINS PROBABLE)

**Fichier** : `backend/app/api/v1/auteurs.py`

Vérifier que l'endpoint `/api/v1/auteurs/{id}` retourne bien toutes les publications via les relations.

---

### Hypothèse 4 : Frontend - Affichage (MOINS PROBABLE)

**Fichier** : `frontend/src/pages/AuthorProfile.tsx`

Si l'API retourne correctement les données, le frontend devrait les afficher.

---

## 🎯 MISSION CLAUDE CODE

### Étape 1 : Vérifier les Données en Base (5 min)

```bash
# Accès PostgreSQL
docker-compose -f docker-compose.staging.yml exec postgres psql -U deeo_user -d deeo_ai_staging

# Vérifier la table existe et a des données
SELECT COUNT(*) FROM publication_auteur;

# Trouver auteurs avec plusieurs publications
SELECT a.nom, a.prenom, COUNT(pa.publication_id) as nb_pubs
FROM auteur a
JOIN publication_auteur pa ON a.id = pa.auteur_id
GROUP BY a.id, a.nom, a.prenom
HAVING COUNT(pa.publication_id) > 1
ORDER BY nb_pubs DESC
LIMIT 10;

# Vérifier une publication avec plusieurs auteurs
SELECT p.titre, a.nom, a.prenom, pa.ordre
FROM publication p
JOIN publication_auteur pa ON p.id = pa.publication_id
JOIN auteur a ON pa.auteur_id = a.id
WHERE p.titre ILIKE '%tokenisation%'
ORDER BY pa.ordre;
```

**Résultat attendu** : 
- La table `publication_auteur` contient ~1199 entrées
- Plusieurs auteurs ont plus d'1 publication
- Les publications ont bien plusieurs auteurs

---

### Étape 2 : Corriger Backend - Repository (15 min)

**Fichier** : `backend/app/repositories/auteur_repository.py`

#### 2.1 Vérifier les imports

```python
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload
from app.models import Auteur, Publication, PublicationAuteur  # ← IMPORTANT
```

#### 2.2 Corriger la méthode `get_with_publications()`

```python
async def get_with_publications(self, auteur_id: int) -> Optional[Auteur]:
    """
    Récupérer un auteur avec TOUTES ses publications via la table publication_auteur.
    """
    result = await self.session.execute(
        select(Auteur)
        .options(
            selectinload(Auteur.publications)  # ← Charger relation many-to-many
        )
        .where(Auteur.id == auteur_id)
    )
    return result.scalar_one_or_none()
```

**Note** : Cela suppose que le modèle `Auteur` a une relation définie :

```python
# Dans backend/app/models/auteur.py
class Auteur(Base):
    __tablename__ = 'auteur'
    
    # ... autres champs ...
    
    # Relation Many-to-Many avec Publication via publication_auteur
    publications = relationship(
        "Publication",
        secondary="publication_auteur",  # ← Table d'association
        back_populates="auteurs"
    )
```

#### 2.3 Vérifier le modèle Publication

```python
# Dans backend/app/models/publication.py
class Publication(Base):
    __tablename__ = 'publication'
    
    # ... autres champs ...
    
    # Relation Many-to-Many avec Auteur via publication_auteur
    auteurs = relationship(
        "Auteur",
        secondary="publication_auteur",  # ← Table d'association
        back_populates="publications",
        order_by="PublicationAuteur.ordre"  # ← Respecter ordre
    )
```

---

### Étape 3 : Vérifier le Modèle SQLAlchemy `publication_auteur` (5 min)

**Fichier** : `backend/app/models/association_publication_auteur.py` (ou similaire)

Vérifier que la table d'association est bien définie :

```python
from sqlalchemy import Column, Integer, String, UUID, DateTime, ForeignKey, Table
from app.models.base import Base

# Table d'association Many-to-Many
PublicationAuteur = Table(
    'publication_auteur',
    Base.metadata,
    Column('publication_id', UUID, ForeignKey('publication.id'), primary_key=True),
    Column('auteur_id', UUID, ForeignKey('auteur.id'), primary_key=True),
    Column('ordre', Integer, nullable=False),
    Column('role', String(50), nullable=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)
```

**OU** si c'est un modèle complet :

```python
class PublicationAuteur(Base):
    __tablename__ = 'publication_auteur'
    
    publication_id = Column(UUID, ForeignKey('publication.id'), primary_key=True)
    auteur_id = Column(UUID, ForeignKey('auteur.id'), primary_key=True)
    ordre = Column(Integer, nullable=False)
    role = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

### Étape 4 : Tester l'API Backend (5 min)

```bash
# Test 1 : Récupérer un auteur avec ses publications
curl http://localhost:8001/api/v1/auteurs/1 | jq '.publications | length'
# Attendu : > 1 pour certains auteurs

# Test 2 : Lister auteurs avec nombre de publications
curl http://localhost:8001/api/v1/auteurs | jq '.[] | {nom: .nom, nb_pubs: (.publications | length)}'
```

---

### Étape 5 : Vérifier Frontend (5 min)

**Fichier** : `frontend/src/pages/AuthorProfile.tsx`

Vérifier que le composant affiche correctement `author.publications` :

```typescript
// Exemple d'affichage
{author.publications && author.publications.length > 0 ? (
  <div>
    <h3>Publications ({author.publications.length})</h3>
    {author.publications.map(pub => (
      <PublicationCard key={pub.id} publication={pub} />
    ))}
  </div>
) : (
  <p>Aucune publication</p>
)}
```

---

### Étape 6 : Corriger la Recherche de Publications par Auteur (10 min)

**Fichier** : `backend/app/repositories/publication_repository.py`

```python
async def search(self, query: str, skip: int = 0, limit: int = 20) -> List[Publication]:
    """
    Recherche publications par titre, abstract, ou NOM D'AUTEUR.
    """
    stmt = (
        select(Publication)
        .options(selectinload(Publication.auteurs))
        .join(PublicationAuteur, Publication.id == PublicationAuteur.publication_id, isouter=True)
        .join(Auteur, PublicationAuteur.auteur_id == Auteur.id, isouter=True)
        .where(
            or_(
                Publication.titre.ilike(f'%{query}%'),
                Publication.abstract.ilike(f'%{query}%'),
                Auteur.nom.ilike(f'%{query}%'),      # ← Recherche par nom auteur
                Auteur.prenom.ilike(f'%{query}%')     # ← Recherche par prénom
            )
        )
        .distinct()  # ← IMPORTANT : éviter doublons
        .offset(skip)
        .limit(limit)
    )
    
    result = await self.session.execute(stmt)
    return result.scalars().all()
```

---

## ✅ CRITÈRES DE SUCCÈS

### Backend API

- [ ] Modèles `Auteur` et `Publication` ont relations `many-to-many` définies
- [ ] Table `publication_auteur` utilisée correctement
- [ ] Endpoint `/api/v1/auteurs/{id}` retourne toutes les publications de l'auteur
- [ ] Recherche publications par nom auteur fonctionne

### Frontend

- [ ] Page `/authors/{id}` affiche toutes les publications de l'auteur (pas juste 1)
- [ ] Page `/authors` affiche le bon nombre de publications par auteur
- [ ] Recherche publications par nom auteur retourne tous les résultats

### Tests SQL

```sql
-- Test 1 : Auteurs avec plusieurs publications
SELECT COUNT(*) FROM (
    SELECT auteur_id 
    FROM publication_auteur 
    GROUP BY auteur_id 
    HAVING COUNT(*) > 1
) AS multi_pub_authors;
-- Attendu : > 0

-- Test 2 : Publications avec plusieurs auteurs
SELECT COUNT(*) FROM (
    SELECT publication_id 
    FROM publication_auteur 
    GROUP BY publication_id 
    HAVING COUNT(*) > 1
) AS multi_author_pubs;
-- Attendu : > 100 (la plupart des publications ont plusieurs auteurs)
```

---

## 🖥️ ENVIRONNEMENT

- **Backend** : http://localhost:8001
- **Frontend** : http://localhost:5174
- **PostgreSQL** : localhost:5433
- **Docker** : `docker-compose.staging.yml`

### Commandes Utiles

```bash
# Logs backend
docker-compose -f docker-compose.staging.yml logs -f api

# Accès PostgreSQL
docker-compose -f docker-compose.staging.yml exec postgres psql -U deeo_user -d deeo_ai_staging

# Redémarrer API après modifications
docker-compose -f docker-compose.staging.yml restart api
```

---

## 🎬 PHRASE DE DÉMARRAGE

```
BUG CRITIQUE DEEO.AI : Relations Many-to-Many publications-auteurs mal gérées.

PROBLÈME : 
- Chaque auteur n'affiche qu'1 publication alors qu'ils en ont plusieurs
- La table publication_auteur existe en base mais n'est pas utilisée correctement
- Recherche par nom d'auteur ne retourne pas toutes les publications

ACTION :
1. Vérifie que les modèles Auteur et Publication ont relations many-to-many définies
2. Corrige auteur_repository.py pour utiliser la table publication_auteur
3. Corrige la recherche dans publication_repository.py pour inclure noms d'auteurs
4. Teste l'API : /api/v1/auteurs/{id} doit retourner toutes ses publications

Commence par vérifier backend/app/models/auteur.py et publication.py pour voir si les relations sont définies.
```

---

**Bonne chance !** 🚀

**Ce bug est CRITIQUE car il fausse toutes les statistiques auteurs !**
