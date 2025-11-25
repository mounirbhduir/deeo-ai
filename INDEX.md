# 📦 PACKAGE COMPLET - DEEO.AI MULTI-ENVIRONNEMENTS

**Date de génération** : 19 novembre 2025  
**Version** : 1.0  
**Projet** : DEEO.AI - Master Big Data & AI (UIR)

---

## 📋 FICHIERS GÉNÉRÉS (9 fichiers)

### 🔷 Fichiers Docker Compose (3)

| Fichier | Description | Environnement | Ports |
|---------|-------------|---------------|-------|
| **docker-compose.dev.yml** | Configuration développement | DEV | 5173, 8000, 5432 |
| **docker-compose.staging.yml** | Configuration pre-production | STAGING | 5174, 8001, 5433 |
| **docker-compose.prod.yml** | Configuration production | PROD | 80, 443 |

**Caractéristiques** :
- ✅ Services : PostgreSQL, Redis, FastAPI, React, Nginx (prod), PgAdmin (optionnel)
- ✅ Volumes persistants nommés
- ✅ Networks isolés par environnement
- ✅ Health checks configurés
- ✅ Restart policies adaptés
- ✅ Resource limits (staging/prod)

---

### 🔶 Fichiers Configuration (.env) (3)

| Fichier | Description | Usage |
|---------|-------------|-------|
| **.env.dev** | Variables environnement DEV | Mock data, debug activé |
| **.env.staging** | Variables environnement STAGING | Données réelles, pipelines activés |
| **.env.prod** | Variables environnement PROD | Production, sécurité renforcée |

**Contenu** :
- ✅ Database URLs
- ✅ Redis configuration
- ✅ API settings (CORS, debug, etc.)
- ✅ Phase 3 pipelines config
- ✅ Security secrets (à changer en prod !)
- ✅ Logging levels

---

### 📘 Documentation (2)

| Fichier | Description | Pages |
|---------|-------------|-------|
| **README_ENVIRONMENTS.md** | Guide complet environnements | ~35 pages |
| **QUICK_START.md** | Installation rapide 5 minutes | ~10 pages |

**README_ENVIRONMENTS.md** contient :
- ✅ Vue d'ensemble architecture multi-environnements
- ✅ Guide détaillé pour chaque environnement
- ✅ Workflow de développement recommandé
- ✅ Migration des données (DEV → STAGING → PROD)
- ✅ Commandes utiles complètes
- ✅ Troubleshooting exhaustif
- ✅ Checklist démarrage

**QUICK_START.md** contient :
- ✅ Installation en 5 minutes
- ✅ Commandes essentielles
- ✅ Basculement entre environnements
- ✅ Problèmes fréquents
- ✅ Checklist démarrage rapide

---

### 🛠️ Scripts Utilitaires (2)

| Fichier | Type | Description |
|---------|------|-------------|
| **Makefile** | Makefile | Commandes simplifiées (Linux/Mac/Git Bash) |
| **install-environments.ps1** | PowerShell | Installation automatique (Windows) |

**Makefile** - Commandes disponibles :
```bash
make help              # Afficher aide
make dev-up            # Démarrer DEV
make dev-down          # Arrêter DEV
make staging-up        # Démarrer STAGING
make staging-populate  # Peupler STAGING avec données réelles
make status            # Status tous environnements
make all-down          # Arrêter tout
```

**install-environments.ps1** - Fonctionnalités :
- ✅ Vérification prérequis (Docker, docker-compose)
- ✅ Vérification fichiers de configuration
- ✅ Création .env depuis .env.dev
- ✅ Création dossiers nécessaires
- ✅ Démarrage automatique DEV
- ✅ Vérification santé services

---

## 🚀 INSTALLATION

### Étape 1 : Télécharger les Fichiers

Télécharger **tous les 9 fichiers** depuis Claude.ai :

```
📦 Package DEEO.AI Multi-Environnements
├── docker-compose.dev.yml
├── docker-compose.staging.yml
├── docker-compose.prod.yml
├── .env.dev
├── .env.staging
├── .env.prod
├── Makefile
├── install-environments.ps1
├── README_ENVIRONMENTS.md
└── QUICK_START.md
```

### Étape 2 : Copier dans le Projet

```powershell
# PowerShell Windows
cd C:\Users\user\deeo-ai-poc

# Copier tous les fichiers téléchargés ici
# Vérifier présence
Get-ChildItem | Where-Object { $_.Name -like "docker-compose*" -or $_.Name -like ".env*" }
```

### Étape 3 : Installation Automatique (Recommandé)

```powershell
# Lancer script d'installation
.\install-environments.ps1

# Le script va :
# 1. Vérifier prérequis
# 2. Créer .env depuis .env.dev
# 3. Créer dossiers nécessaires
# 4. Démarrer environnement DEV
```

### Étape 4 : Installation Manuelle (Alternative)

```powershell
# 1. Copier fichier environnement
Copy-Item .env.dev .env

# 2. Démarrer environnement DEV
docker-compose -f docker-compose.dev.yml up -d

# 3. Vérifier status
docker-compose -f docker-compose.dev.yml ps

# 4. Accéder application
Start-Process "http://localhost:5173"
```

---

## 📊 COMPARAISON ENVIRONNEMENTS

| Critère | DEV | STAGING | PROD |
|---------|-----|---------|------|
| **Données** | Mock (50 pubs) | Réelles (15k+) | Réelles (15k+) |
| **Frontend** | :5173 | :5174 | :80/443 |
| **Backend** | :8000 | :8001 | :80/api |
| **PostgreSQL** | :5432 | :5433 | Interne |
| **Debug** | ✅ ON | ❌ OFF | ❌ OFF |
| **Hot Reload** | ✅ Oui | ✅ Oui | ❌ Non |
| **Pipelines Phase 3** | ❌ | ✅ | ✅ |
| **SSL/HTTPS** | ❌ | ❌ | ✅ |
| **Monitoring** | ❌ | ❌ | ✅ (optionnel) |
| **Usage Quotidien** | 90% | 10% | 1 fois |

---

## 🎯 WORKFLOW RECOMMANDÉ

### Développement Quotidien (90% du temps)

```powershell
# Démarrer DEV
docker-compose -f docker-compose.dev.yml up -d

# Développer normalement
cd frontend
npm run dev

cd backend
# Modifier code, hot reload automatique

# Tests
docker-compose -f docker-compose.dev.yml exec api pytest

# Arrêter fin journée
docker-compose -f docker-compose.dev.yml down
```

### Validation Pre-Soutenance (10% du temps)

```powershell
# Démarrer STAGING
docker-compose -f docker-compose.staging.yml up -d

# Tester performance avec données réelles
Start-Process "http://localhost:5174"

# Screenshots pour rapport
# Tests de charge
# Vérification temps de réponse

# Arrêter
docker-compose -f docker-compose.staging.yml down
```

### Démo Soutenance (1 fois)

**Option A : Local**
```powershell
# Utiliser STAGING local
docker-compose -f docker-compose.staging.yml up -d
# Démo sur http://localhost:5174 avec projecteur
```

**Option B : VPS Cloud (recommandé)**
```bash
# Sur serveur VPS
docker-compose -f docker-compose.prod.yml up -d
# Démo sur https://deeo-ai.votredomaine.com
```

---

## 💡 COMMANDES ESSENTIELLES

### Démarrage/Arrêt

```powershell
# Démarrer DEV
docker-compose -f docker-compose.dev.yml up -d

# Démarrer STAGING
docker-compose -f docker-compose.staging.yml up -d

# Arrêter DEV
docker-compose -f docker-compose.dev.yml down

# Arrêter tout
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.staging.yml down
```

### Logs & Debug

```powershell
# Logs temps réel DEV
docker-compose -f docker-compose.dev.yml logs -f

# Logs API uniquement
docker-compose -f docker-compose.dev.yml logs -f api

# Shell dans conteneur API
docker-compose -f docker-compose.dev.yml exec api bash

# PostgreSQL shell
docker-compose -f docker-compose.dev.yml exec postgres psql -U deeo_user -d deeo_ai_dev
```

### Tests

```powershell
# Tests backend
docker-compose -f docker-compose.dev.yml exec api pytest

# Tests avec coverage
docker-compose -f docker-compose.dev.yml exec api pytest --cov=app --cov-report=html

# Tests E2E frontend
cd frontend
npm run test:e2e
```

### Reset & Cleanup

```powershell
# Reset DEV (supprime données)
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d

# Cleanup Docker complet (PRUDENCE)
docker system prune -a --volumes
```

---

## 🐛 TROUBLESHOOTING RAPIDE

### Problème : Services ne démarrent pas

```powershell
# Vérifier Docker actif
docker ps

# Voir logs
docker-compose -f docker-compose.dev.yml logs

# Reset
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
```

### Problème : Port déjà utilisé

```powershell
# Identifier processus
netstat -ano | findstr :5173

# Arrêter processus
taskkill /PID <PID> /F
```

### Problème : Base de données vide

```powershell
# Vérifier tables
docker-compose -f docker-compose.dev.yml exec postgres psql -U deeo_user -d deeo_ai_dev -c "\dt"

# Repeupler (DEV)
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
```

---

## ⚠️ POINTS IMPORTANTS

### 1. Fichiers Sensibles

**NE JAMAIS commiter** :
- ❌ `.env` (contient mots de passe)
- ❌ `.env.dev`, `.env.staging`, `.env.prod` (templates OK, pas avec vrais mots de passe)

**Vérifier .gitignore** :
```
.env
.env.*
!.env.example
```

### 2. Mots de Passe Production

**AVANT d'utiliser .env.prod en production** :
```powershell
# Générer mot de passe sécurisé
openssl rand -hex 32

# Remplacer dans .env.prod :
POSTGRES_PASSWORD=<nouveau_password>
REDIS_PASSWORD=<nouveau_password>
SECRET_KEY=<nouveau_password>
JWT_SECRET=<nouveau_password>
```

### 3. Peuplement STAGING (1 fois)

**ATTENTION** : Peuplement données réelles prend **3-4 heures** :
```powershell
docker-compose -f docker-compose.staging.yml exec api python scripts/populate_real_data.py
```

À faire **une seule fois**, puis conserver les données.

---

## 📚 DOCUMENTATION COMPLÈTE

### Guides Inclus

- **README_ENVIRONMENTS.md** : Guide complet (~35 pages)
  - Architecture détaillée
  - Workflow développement
  - Migration données
  - Troubleshooting exhaustif

- **QUICK_START.md** : Installation rapide (~10 pages)
  - Setup 5 minutes
  - Commandes essentielles
  - FAQ

### Liens Utiles

- **Swagger API DEV** : http://localhost:8000/docs
- **Swagger API STAGING** : http://localhost:8001/docs
- **PgAdmin DEV** : http://localhost:5050 (avec `--profile tools`)
- **PgAdmin STAGING** : http://localhost:5051 (avec `--profile tools`)

---

## ✅ CHECKLIST FINALE

### Installation Initiale

- [ ] 9 fichiers téléchargés depuis Claude.ai
- [ ] Fichiers copiés dans `C:\Users\user\deeo-ai-poc\`
- [ ] Docker Desktop installé et actif
- [ ] Script `install-environments.ps1` exécuté
- [ ] Environnement DEV démarré et accessible

### Validation DEV

- [ ] Frontend accessible : http://localhost:5173
- [ ] Backend accessible : http://localhost:8000/docs
- [ ] Tests passent : `docker-compose -f docker-compose.dev.yml exec api pytest`
- [ ] Hot reload fonctionne (modifier composant frontend)

### Préparation STAGING

- [ ] STAGING démarré une fois pour vérifier setup
- [ ] Script `populate_real_data.py` créé dans `backend/scripts/`
- [ ] Peuplement STAGING lancé (attendre 3-4h)
- [ ] Données vérifiées : ~15,000 publications

### Avant Soutenance

- [ ] Tests performance STAGING OK
- [ ] Screenshots pris sur STAGING
- [ ] Backup STAGING effectué : `pg_dump`
- [ ] Décision déploiement : Local ou VPS ?

---

## 🎉 FÉLICITATIONS !

Vous disposez maintenant d'une **infrastructure professionnelle multi-environnements** pour DEEO.AI !

**Prochaines étapes** :
1. ✅ Tester environnement DEV
2. ✅ Lire documentation complète
3. ✅ Configurer STAGING quand prêt
4. ✅ Développer sereinement !

**Bon développement ! 🚀**

---

**Package créé le** : 19 novembre 2025  
**Version** : 1.0  
**Auteur** : Mounir + Claude Sonnet 4.5  
**Projet** : DEEO.AI - Master Big Data & AI (UIR)

---

**FIN DU FICHIER INDEX**
