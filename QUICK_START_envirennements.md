# ⚡ QUICK START - DEEO.AI MULTI-ENVIRONNEMENTS

**Installation rapide en 5 minutes** | Guide complet: `README_ENVIRONMENTS.md`

---

## 📦 PACKAGE COMPLET GÉNÉRÉ

Vous disposez maintenant de **7 fichiers de configuration** pour gérer 3 environnements :

### Fichiers Docker Compose

✅ **docker-compose.dev.yml** - Développement (mock data, port 5173)  
✅ **docker-compose.staging.yml** - Staging (données réelles, port 5174)  
✅ **docker-compose.prod.yml** - Production (démo soutenance, port 80/443)

### Fichiers Configuration

✅ **.env.dev** - Variables environnement DEV  
✅ **.env.staging** - Variables environnement STAGING  
✅ **.env.prod** - Variables environnement PRODUCTION (changer mots de passe !)

### Outils

✅ **Makefile** - Commandes simplifiées (`make dev-up`, `make staging-up`, etc.)

---

## 🚀 INSTALLATION INITIALE (5 min)

### Étape 1 : Copier Fichiers dans Votre Projet

```powershell
# Dans PowerShell Windows
cd C:\Users\user\deeo-ai-poc

# Copier tous les fichiers téléchargés depuis Claude.ai dans la racine
# - docker-compose.dev.yml
# - docker-compose.staging.yml
# - docker-compose.prod.yml
# - .env.dev
# - .env.staging
# - .env.prod
# - Makefile
```

### Étape 2 : Configurer Environnement DEV

```powershell
# Copier fichier environnement
cd C:\Users\user\deeo-ai-poc
Copy-Item .env.dev .env

# Vérifier contenu
Get-Content .env | Select-String "POSTGRES"
```

### Étape 3 : Démarrer Environnement DEV

```powershell
# Vérifier Docker Desktop actif
docker ps

# Démarrer services DEV
docker-compose -f docker-compose.dev.yml up -d

# Vérifier status
docker-compose -f docker-compose.dev.yml ps

# Résultat attendu :
# NAME                    STATUS
# deeo-postgres-dev       Up (healthy)
# deeo-redis-dev          Up (healthy)
# deeo-api-dev            Up
# deeo-frontend-dev       Up
```

### Étape 4 : Accéder à l'Application

Ouvrir navigateur :

- **Frontend** : http://localhost:5173
- **Backend API** : http://localhost:8000/docs
- **PgAdmin** (optionnel) : http://localhost:5050

✅ **TERMINÉ !** Vous pouvez maintenant développer sur environnement DEV.

---

## 🎯 UTILISATION QUOTIDIENNE

### Workflow Typique

```powershell
# Matin : Démarrer DEV
docker-compose -f docker-compose.dev.yml up -d

# Développer normalement
cd frontend
npm run dev

# Voir logs si besoin
docker-compose -f docker-compose.dev.yml logs -f api

# Soir : Arrêter DEV
docker-compose -f docker-compose.dev.yml down
```

### Commandes Essentielles

```powershell
# Démarrer DEV
docker-compose -f docker-compose.dev.yml up -d

# Arrêter DEV
docker-compose -f docker-compose.dev.yml down

# Voir logs
docker-compose -f docker-compose.dev.yml logs -f

# Reset complet (supprime données)
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d

# Lancer tests
docker-compose -f docker-compose.dev.yml exec api pytest
```

---

## 🟢 UTILISATION STAGING (Données Réelles)

### Première Utilisation (1 fois)

```powershell
# 1. Copier configuration STAGING
cd C:\Users\user\deeo-ai-poc
Copy-Item .env.staging .env

# 2. Démarrer STAGING
docker-compose -f docker-compose.staging.yml up -d

# 3. Attendre que services soient UP (30 sec)
docker-compose -f docker-compose.staging.yml ps

# 4. Peupler avec données réelles (ATTENTION : 3-4 heures)
docker-compose -f docker-compose.staging.yml exec api python scripts/populate_real_data.py

# 5. Vérifier données
docker-compose -f docker-compose.staging.yml exec postgres psql -U deeo_user -d deeo_ai_staging -c "SELECT COUNT(*) FROM publication;"
# Résultat attendu : ~15,000+
```

### Accès STAGING

- **Frontend** : http://localhost:5174
- **Backend API** : http://localhost:8001/docs

---

## 🔄 BASCULER ENTRE ENVIRONNEMENTS

### Méthode 1 : Ports Différents (Recommandé)

**Les deux environnements tournent EN PARALLÈLE** :

```powershell
# DEV toujours actif
docker-compose -f docker-compose.dev.yml up -d
# Accès : http://localhost:5173

# STAGING en parallèle
docker-compose -f docker-compose.staging.yml up -d
# Accès : http://localhost:5174

# Vérifier les deux
docker ps
# Vous verrez 8 conteneurs (4 DEV + 4 STAGING)
```

### Méthode 2 : Alterner (Si Ressources Limitées)

```powershell
# Utiliser DEV
docker-compose -f docker-compose.dev.yml up -d
# Travailler...

# Basculer vers STAGING
docker-compose -f docker-compose.dev.yml down
Copy-Item .env.staging .env
docker-compose -f docker-compose.staging.yml up -d

# Retour DEV
docker-compose -f docker-compose.staging.yml down
Copy-Item .env.dev .env
docker-compose -f docker-compose.dev.yml up -d
```

---

## 📊 COMPARAISON RAPIDE

| Environnement | Données | Frontend | Backend | Usage |
|---------------|---------|----------|---------|-------|
| **DEV** | Mock (50 pubs) | :5173 | :8000 | Développement quotidien |
| **STAGING** | Réelles (15k+) | :5174 | :8001 | Tests réalistes |
| **PROD** | Réelles (15k+) | :80 | :80/api | Démo soutenance |

---

## 🛠️ UTILISATION MAKEFILE (Linux/Mac/Git Bash)

Si vous avez `make` installé :

```bash
# Aide
make help

# Démarrer DEV
make dev-up

# Arrêter DEV
make dev-down

# Logs DEV
make dev-logs

# Démarrer STAGING
make staging-up

# Status de tous les environnements
make status
```

**Note Windows** : Makefile fonctionne avec Git Bash ou WSL. Sinon, utilisez commandes `docker-compose` directement.

---

## ⚠️ POINTS D'ATTENTION

### 1. Fichiers .env

**IMPORTANT** : Ne commitez JAMAIS les fichiers `.env` dans Git !

```bash
# Vérifier .gitignore contient :
.env
.env.*
!.env.example
```

### 2. Mots de Passe Production

**AVANT d'utiliser .env.prod**, changez TOUS les mots de passe :

```powershell
# Générer mot de passe sécurisé (PowerShell)
$password = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
Write-Host $password

# Remplacer dans .env.prod :
# POSTGRES_PASSWORD=<nouveau_password>
# REDIS_PASSWORD=<nouveau_password>
# SECRET_KEY=<nouveau_password>
```

### 3. Ressources Système

**Environnements en parallèle** (DEV + STAGING) nécessitent :
- **RAM** : 4-6 GB minimum
- **Disque** : 10-15 GB disponibles
- **CPU** : 2 cores minimum

Si ressources limitées, utilisez **méthode 2** (alterner).

---

## 🐛 PROBLÈMES FRÉQUENTS

### Erreur : "Port already in use"

```powershell
# Identifier processus utilisant port
netstat -ano | findstr :5173

# Arrêter processus (remplacer PID)
taskkill /PID <PID> /F

# Ou arrêter environnement concurrent
docker-compose -f docker-compose.dev.yml down
```

### Erreur : "Database connection failed"

```powershell
# Vérifier PostgreSQL UP
docker-compose -f docker-compose.dev.yml ps postgres

# Voir logs PostgreSQL
docker-compose -f docker-compose.dev.yml logs postgres

# Restart PostgreSQL
docker-compose -f docker-compose.dev.yml restart postgres
```

### Conteneurs ne démarrent pas

```powershell
# Reset complet
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d

# Si toujours problème, cleanup Docker
docker system prune -a --volumes
```

---

## 📚 DOCUMENTATION COMPLÈTE

Pour plus de détails :

- **Guide complet** : `README_ENVIRONMENTS.md`
- **Workflow développement** : Section "Workflow de Développement"
- **Migration données** : Section "Migration des Données"
- **Troubleshooting** : Section "Troubleshooting"

---

## ✅ CHECKLIST DÉMARRAGE RAPIDE

- [ ] Fichiers copiés dans `deeo-ai-poc/`
- [ ] `.env` créé depuis `.env.dev`
- [ ] Docker Desktop actif (`docker ps`)
- [ ] DEV démarré (`docker-compose -f docker-compose.dev.yml up -d`)
- [ ] Frontend accessible (http://localhost:5173)
- [ ] Backend accessible (http://localhost:8000/docs)
- [ ] Tests passent (`docker-compose -f docker-compose.dev.yml exec api pytest`)

---

## 🎯 PROCHAINES ÉTAPES RECOMMANDÉES

### Maintenant (Immédiat)

1. ✅ **Tester environnement DEV** : Développer feature, vérifier hot reload
2. ✅ **Lire README_ENVIRONMENTS.md** : Comprendre stratégie complète

### Cette Semaine

3. ✅ **Configurer STAGING** : Démarrer une fois pour vérifier setup
4. ✅ **Peupler STAGING** : Lancer script `populate_real_data.py` (4h)

### Avant Soutenance (2-4 semaines)

5. ✅ **Valider sur STAGING** : Tests performance, screenshots démo
6. ✅ **Préparer PROD** : Décider local vs VPS
7. ✅ **Backup STAGING** : `pg_dump` pour sécurité

---

## 💬 BESOIN D'AIDE ?

Si problème avec setup :

1. **Vérifier logs** : `docker-compose -f docker-compose.dev.yml logs`
2. **Vérifier status** : `docker-compose -f docker-compose.dev.yml ps`
3. **Consulter Troubleshooting** : `README_ENVIRONMENTS.md`
4. **Reset et réessayer** : `docker-compose down -v && docker-compose up -d`

---

**Installation terminée !** 🎉  
**Bon développement sur DEEO.AI !** 🚀

---

**Créé le** : 19 novembre 2025  
**Version** : 1.0  
**Projet** : DEEO.AI - Master Big Data & AI (UIR)
