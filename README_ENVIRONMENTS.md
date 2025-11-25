# 🌍 GUIDE DES ENVIRONNEMENTS - DEEO.AI

**Projet** : DEEO.AI - AI Dynamic Emergence and Evolution Observatory  
**Date** : 19 novembre 2025  
**Version** : 1.0

---

## 📋 SOMMAIRE

- [Vue d'Ensemble](#vue-densemble)
- [Environnement DEV](#environnement-dev)
- [Environnement STAGING](#environnement-staging)
- [Environnement PRODUCTION](#environnement-production)
- [Workflow de Développement](#workflow-de-développement)
- [Migration des Données](#migration-des-données)
- [Commandes Utiles](#commandes-utiles)
- [Troubleshooting](#troubleshooting)

---

## 🎯 VUE D'ENSEMBLE

DEEO.AI utilise **3 environnements distincts** pour séparer développement, tests, et démo finale.

### Architecture Multi-Environnements

```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  DEV (Mock Data) │  │ STAGING (Réel)   │  │  PROD (Démo)     │
│                  │  │                   │  │                   │
│  localhost:5173  │  │ localhost:5174    │  │ deeo-ai.com      │
│  localhost:8000  │  │ localhost:8001    │  │ api.deeo-ai.com  │
│                  │  │                   │  │                   │
│  Fast iteration  │  │ Pre-production    │  │ Soutenance       │
│  Tests rapides   │  │ Tests réalistes   │  │ Démo jury        │
│  50 publications │  │ 15,000+ pubs      │  │ 15,000+ pubs     │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

### Comparaison Rapide

| Critère | DEV | STAGING | PROD |
|---------|-----|---------|------|
| **Données** | Mock (50 pubs) | Réelles (15k+) | Réelles (15k+) |
| **Ports** | 5173, 8000, 5432 | 5174, 8001, 5433 | 80, 443 |
| **Debug** | ✅ Activé | ❌ Désactivé | ❌ Désactivé |
| **Hot Reload** | ✅ Oui | ✅ Oui | ❌ Non |
| **Logs** | DEBUG | INFO | WARNING |
| **Pipelines Phase 3** | ❌ | ✅ | ✅ |
| **SSL/HTTPS** | ❌ | ❌ | ✅ |
| **Usage** | Quotidien (90%) | Validation (10%) | Démo (1 fois) |

---

## 🔵 ENVIRONNEMENT DEV

### Description

**Environnement de développement rapide** avec données fictives légères.

### Caractéristiques

- **Données** : Mock data (50 publications, 30 auteurs, 15 organisations)
- **Réinitialisation** : Facile et rapide (`docker-compose down -v`)
- **Debug** : Mode activé, logs détaillés
- **Performance** : Démarrage <30 secondes

### Fichiers

- `docker-compose.dev.yml`
- `.env.dev`

### Quand l'Utiliser ?

✅ **Développement quotidien** :
- Créer nouveaux composants frontend
- Ajouter endpoints backend
- Tests unitaires/intégration
- Debugging

✅ **Tests rapides** :
- Vérifier fonctionnalité
- Itération rapide
- Expérimentation

❌ **NE PAS utiliser pour** :
- Tests de performance
- Validation finale
- Screenshots démo

---

### 🚀 DÉMARRAGE DEV

#### Configuration Initiale (1 fois)

```bash
# 1. Copier fichier environnement
cd deeo-ai-poc
cp .env.dev .env

# 2. Vérifier Docker Desktop actif
docker ps

# 3. Démarrer services
docker-compose -f docker-compose.dev.yml up -d

# 4. Vérifier services UP
docker-compose -f docker-compose.dev.yml ps

# Résultat attendu :
# deeo-postgres-dev   Up (healthy)
# deeo-redis-dev      Up (healthy)
# deeo-api-dev        Up
# deeo-frontend-dev   Up
```

#### Accès

- **Frontend** : http://localhost:5173
- **Backend API** : http://localhost:8000
- **API Docs** : http://localhost:8000/docs
- **PgAdmin** : http://localhost:5050 (optionnel, avec `--profile tools`)

#### Commandes Courantes

```bash
# Démarrer
docker-compose -f docker-compose.dev.yml up -d

# Arrêter
docker-compose -f docker-compose.dev.yml down

# Voir logs
docker-compose -f docker-compose.dev.yml logs -f

# Logs API uniquement
docker-compose -f docker-compose.dev.yml logs -f api

# Reset complet (supprime données)
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d

# Entrer dans conteneur API
docker-compose -f docker-compose.dev.yml exec api bash

# Lancer tests
docker-compose -f docker-compose.dev.yml exec api pytest
```

---

## 🟢 ENVIRONNEMENT STAGING

### Description

**Environnement de test avec données réelles** pour validation pré-production.

### Caractéristiques

- **Données** : Réelles (15,000+ publications arXiv)
- **Pipelines** : Activés (arXiv, Semantic Scholar, ML)
- **Performance** : Conditions production
- **Cohabitation** : Tourne en parallèle de DEV (ports différents)

### Fichiers

- `docker-compose.staging.yml`
- `.env.staging`

### Quand l'Utiliser ?

✅ **Tests réalistes** :
- Performance avec gros volumes
- Recherche avec 15k+ publications
- Graphe réseau complet
- Dashboard avec vraies métriques

✅ **Validation avant soutenance** :
- Scénarios démo
- Temps de réponse
- Screenshots finaux

✅ **Développement features "heavy"** :
- Optimisation SQL
- Pagination
- Agrégations complexes

❌ **NE PAS utiliser pour** :
- Développement quotidien (trop lent)
- Tests unitaires simples
- Modifications DB fréquentes

---

### 🚀 DÉMARRAGE STAGING

#### Configuration Initiale (1 fois)

```bash
# 1. Copier fichier environnement
cd deeo-ai-poc
cp .env.staging .env

# 2. IMPORTANT : Changer les mots de passe
# Éditer .env et remplacer :
# - POSTGRES_PASSWORD=deeo_password_staging_CHANGEZ_MOI
# - SECRET_KEY=...

# 3. Démarrer services
docker-compose -f docker-compose.staging.yml up -d

# 4. Vérifier services UP
docker-compose -f docker-compose.staging.yml ps
```

#### Peuplement Données Réelles (1 fois, ~4h)

**IMPORTANT** : Cette étape prend **3-4 heures** et doit être faite **une seule fois**.

```bash
# Option A : Script automatique (recommandé)
docker-compose -f docker-compose.staging.yml exec api python scripts/populate_real_data.py

# Option B : Commandes manuelles
# 1. Collecter arXiv (15k publications)
docker-compose -f docker-compose.staging.yml exec api python -m app.pipelines.arxiv_collector --max 15000

# 2. Enrichir Semantic Scholar
docker-compose -f docker-compose.staging.yml exec api python -m app.pipelines.semantic_scholar_enricher --all

# 3. Classification ML
docker-compose -f docker-compose.staging.yml exec api python -m app.pipelines.ml_classifier --all

# 4. Vérifier nombre publications
docker-compose -f docker-compose.staging.yml exec postgres psql -U deeo_user -d deeo_ai_staging -c "SELECT COUNT(*) FROM publication;"
# Résultat attendu : ~15,000+
```

#### Accès

- **Frontend** : http://localhost:5174
- **Backend API** : http://localhost:8001
- **API Docs** : http://localhost:8001/docs
- **PostgreSQL** : localhost:5433
- **PgAdmin** : http://localhost:5051 (avec `--profile tools`)

#### Commandes Courantes

```bash
# Démarrer
docker-compose -f docker-compose.staging.yml up -d

# Arrêter
docker-compose -f docker-compose.staging.yml down

# Voir logs
docker-compose -f docker-compose.staging.yml logs -f api

# Vérifier données
docker-compose -f docker-compose.staging.yml exec postgres psql -U deeo_user -d deeo_ai_staging -c "SELECT COUNT(*) FROM publication;"

# Backup base de données
docker-compose -f docker-compose.staging.yml exec postgres pg_dump -U deeo_user deeo_ai_staging > backup_staging.sql

# Restore backup
cat backup_staging.sql | docker-compose -f docker-compose.staging.yml exec -T postgres psql -U deeo_user -d deeo_ai_staging
```

---

## 🟡 ENVIRONNEMENT PRODUCTION

### Description

**Environnement optimisé pour démo soutenance** avec données réelles.

### Caractéristiques

- **Build optimisé** : Frontend minifié, backend Gunicorn
- **SSL/HTTPS** : Certificats Let's Encrypt
- **Monitoring** : Prometheus + Grafana (optionnel)
- **Sécurité** : Ports internes, mots de passe sécurisés

### Fichiers

- `docker-compose.prod.yml`
- `.env.prod`

### Quand l'Utiliser ?

✅ **Démo soutenance** :
- Présentation jury
- Captures vidéo
- Tests acceptance finaux

✅ **Déploiement cloud** :
- VPS (Hetzner, DigitalOcean)
- AWS/GCP/Azure

❌ **NE PAS utiliser pour** :
- Développement
- Tests
- Modifications fréquentes

---

### 🚀 DÉPLOIEMENT PRODUCTION

#### Configuration (Local)

```bash
# 1. Copier fichier environnement
cd deeo-ai-poc
cp .env.prod .env

# 2. CRITIQUE : Générer mots de passe sécurisés
openssl rand -hex 32
# Copier résultat dans .env pour SECRET_KEY et JWT_SECRET

# 3. Éditer .env.prod
# Remplacer TOUS les "CHANGEZ_MOI"

# 4. Build production
docker-compose -f docker-compose.prod.yml build

# 5. Démarrer
docker-compose -f docker-compose.prod.yml up -d

# 6. Vérifier
docker-compose -f docker-compose.prod.yml ps
```

#### Accès (Local)

- **Application** : http://localhost
- **HTTPS** : https://localhost (si SSL configuré)

#### Configuration SSL (Let's Encrypt)

```bash
# 1. Configurer domaine dans .env.prod
DOMAIN=deeo-ai.votredomaine.com
CERTBOT_EMAIL=votre-email@example.com

# 2. Obtenir certificat
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  -d deeo-ai.votredomaine.com \
  --email votre-email@example.com \
  --agree-tos \
  --no-eff-email

# 3. Redémarrer Nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

---

## 🔄 WORKFLOW DE DÉVELOPPEMENT

### Scénario Typique

```bash
# 90% du temps : DEV (mock data)
docker-compose -f docker-compose.dev.yml up -d

# Développer feature
cd frontend/src/components
# Créer nouveau composant

# Tester
npm run test
docker-compose -f docker-compose.dev.yml exec api pytest

# 10% du temps : STAGING (données réelles)
docker-compose -f docker-compose.staging.yml up -d

# Valider performance
# Vérifier temps de réponse
# Screenshots démo

# Commit Git
git add .
git commit -m "feat: Add new component"
git push
```

---

## 📦 MIGRATION DES DONNÉES

### De DEV vers STAGING

```bash
# DEV utilise mock data (rien à migrer)
# STAGING se peuple avec script populate_real_data.py
```

### De STAGING vers PROD

```bash
# 1. Dump STAGING
docker-compose -f docker-compose.staging.yml exec postgres pg_dump -U deeo_user deeo_ai_staging > data_staging.sql

# 2. Restore dans PROD
cat data_staging.sql | docker-compose -f docker-compose.prod.yml exec -T postgres psql -U deeo_user -d deeo_ai
```

### Backup Automatique

```bash
# Script backup quotidien (cron)
#!/bin/bash
DATE=$(date +%Y%m%d-%H%M%S)
docker-compose -f docker-compose.staging.yml exec postgres pg_dump -U deeo_user deeo_ai_staging > backups/backup_$DATE.sql
```

---

## 💡 COMMANDES UTILES

### Gestion Multi-Environnements

```bash
# Démarrer DEV + STAGING en parallèle
docker-compose -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.staging.yml up -d

# Vérifier tous les conteneurs
docker ps

# Arrêter tous les environnements
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.staging.yml down
docker-compose -f docker-compose.prod.yml down

# Cleanup complet (ATTENTION : supprime données)
docker-compose -f docker-compose.dev.yml down -v
docker system prune -a --volumes
```

### Debugging

```bash
# Logs temps réel
docker-compose -f docker-compose.dev.yml logs -f

# Logs API uniquement
docker-compose -f docker-compose.dev.yml logs -f api

# Entrer dans conteneur
docker-compose -f docker-compose.dev.yml exec api bash

# Shell PostgreSQL
docker-compose -f docker-compose.dev.yml exec postgres psql -U deeo_user -d deeo_ai_dev

# Redis CLI
docker-compose -f docker-compose.dev.yml exec redis redis-cli
```

### Tests

```bash
# Tests backend DEV
docker-compose -f docker-compose.dev.yml exec api pytest

# Tests avec coverage
docker-compose -f docker-compose.dev.yml exec api pytest --cov=app --cov-report=html

# Tests E2E frontend
cd frontend
npm run test:e2e
```

---

## 🐛 TROUBLESHOOTING

### Problème : Conteneurs ne démarrent pas

```bash
# Vérifier Docker Desktop actif
docker ps

# Vérifier logs
docker-compose -f docker-compose.dev.yml logs

# Reset complet
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
```

### Problème : Base de données vide

```bash
# Vérifier tables
docker-compose -f docker-compose.dev.yml exec postgres psql -U deeo_user -d deeo_ai_dev -c "\dt"

# DEV : Relancer avec fixtures
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.dev.yml exec api python scripts/populate_mock_data.py

# STAGING : Peupler avec données réelles
docker-compose -f docker-compose.staging.yml exec api python scripts/populate_real_data.py
```

### Problème : Ports déjà utilisés

```bash
# Identifier processus utilisant port
netstat -ano | findstr :5173
netstat -ano | findstr :8000

# Arrêter processus (Windows)
taskkill /PID <PID> /F

# Ou changer port dans docker-compose.yml
ports:
  - "5175:5173"  # Nouveau port externe
```

### Problème : Frontend ne se connecte pas au backend

```bash
# Vérifier variable VITE_API_URL
docker-compose -f docker-compose.dev.yml exec frontend env | grep VITE

# Vérifier backend accessible
curl http://localhost:8000/api/health

# Vérifier CORS
# Logs backend doivent montrer requête OPTIONS
```

---

## 📚 RESSOURCES ADDITIONNELLES

### Documentation

- **Architecture** : `docs/ARCHITECTURE.md`
- **API** : http://localhost:8000/docs (Swagger)
- **Phase 3** : `docs/PHASE_3_PIPELINES.md`

### Scripts Utiles

- `scripts/populate_mock_data.py` : Générer mock data
- `scripts/populate_real_data.py` : Collecter données réelles
- `scripts/reset_dev_db.sh` : Reset DB dev
- `scripts/backup_db.sh` : Backup base de données

---

## ✅ CHECKLIST DÉMARRAGE RAPIDE

### Première Utilisation

- [ ] Docker Desktop installé et actif
- [ ] Cloner projet : `git clone ...`
- [ ] Copier `.env.dev` vers `.env`
- [ ] Démarrer DEV : `docker-compose -f docker-compose.dev.yml up -d`
- [ ] Vérifier accès : http://localhost:5173
- [ ] Tester API : http://localhost:8000/docs

### Avant Soutenance

- [ ] Peupler STAGING avec données réelles (1 fois)
- [ ] Valider performance STAGING
- [ ] Prendre screenshots sur STAGING
- [ ] Tester scénarios démo
- [ ] Backup STAGING : `pg_dump ...`
- [ ] Préparer PROD ou déployer VPS

---

## 🎯 RECOMMANDATION FINALE

**Pour votre thèse** :

1. **Développement quotidien** : **DEV uniquement** (90% du temps)
2. **Validation pre-soutenance** : **STAGING** (10% du temps)
3. **Démo soutenance** : **STAGING local** OU **PROD sur VPS** (selon choix)

**Budget 0€** : DEV + STAGING suffisent (local)  
**Budget 5-10€** : Ajouter VPS 1 mois pour démo online

---

**Date de création** : 19 novembre 2025  
**Version** : 1.0  
**Auteur** : Mounir + Claude Sonnet 4.5  
**Projet** : DEEO.AI - Master Big Data & AI (UIR)
