# 📋 Guide d'Utilisation - Script `populate_real_data.py`

## 📖 Description

Script automatique de peuplement de la base de données STAGING avec des **données réelles** collectées depuis arXiv.

### Fonctionnalités

- ✅ **Collecte automatique** de publications depuis arXiv (catégories IA)
- ✅ **Pipeline ETL complet** : Extract, Transform, Load
- ✅ **Déduplication** : Évite les doublons
- ✅ **Gestion relations** : Auteurs, thèmes, organisations
- ✅ **Logs détaillés** : Progression en temps réel
- ✅ **Statistiques complètes** : Bilan final de la collecte

### Catégories Collectées

- `cs.AI` - Artificial Intelligence
- `cs.LG` - Machine Learning
- `cs.CV` - Computer Vision
- `cs.CL` - Computation and Language
- `cs.NE` - Neural and Evolutionary Computing
- `stat.ML` - Machine Learning (Statistics)

---

## 🚀 Utilisation

### 1. Depuis l'Hôte (via Docker Compose)

```bash
# Collecte standard (15,000 publications)
docker-compose -f docker-compose.staging.yml exec api python scripts/populate_real_data.py

# Collecte limitée pour test (500 publications)
docker-compose -f docker-compose.staging.yml exec api python scripts/populate_real_data.py --max-publications 500

# Avec batch size personnalisé
docker-compose -f docker-compose.staging.yml exec api python scripts/populate_real_data.py --max-publications 10000 --batch-size 50

# Sur 6 mois seulement
docker-compose -f docker-compose.staging.yml exec api python scripts/populate_real_data.py --date-range-months 6
```

### 2. Depuis le Conteneur

```bash
# Entrer dans le conteneur
docker-compose -f docker-compose.staging.yml exec api bash

# Exécuter le script
python scripts/populate_real_data.py --max-publications 1000
```

---

## ⚙️ Options

| Option | Type | Défaut | Description |
|--------|------|--------|-------------|
| `--max-publications` | int | 15000 | Nombre maximum de publications à collecter |
| `--batch-size` | int | 100 | Taille des batchs pour requêtes arXiv |
| `--date-range-months` | int | 24 | Nombre de mois en arrière (2 ans par défaut) |

---

## 📊 Exemple de Sortie

```
================================================================================
🚀 DÉMARRAGE PEUPLEMENT STAGING AVEC DONNÉES RÉELLES
================================================================================
Configuration:
  - Max publications: 15000
  - Batch size: 100
  - Date range: 2023-11-20 to 2025-11-20
  - Categories: cs.AI, cs.LG, cs.CV, cs.CL, cs.NE, stat.ML

================================================================================
📥 ÉTAPE 1/2 : COLLECTE PUBLICATIONS ARXIV
================================================================================

[1/8] 🔍 Requête: 'deep learning'
  ✅ Collectées: 187
  ➕ Créées: 178
  🔄 Mises à jour: 5
  ⏭️  Ignorées: 4
  👥 Auteurs: 456
  🏷️  Thèmes: 12

[2/8] 🔍 Requête: 'neural networks'
  ✅ Collectées: 165
  ➕ Créées: 152
  ...

================================================================================
🤖 ÉTAPE 2/2 : CLASSIFICATION ML THÉMATIQUE
================================================================================
ℹ️  Les thèmes ont déjà été assignés par le pipeline arXiv
✅ Étape de classification complétée

================================================================================
📊 STATISTIQUES FINALES
================================================================================

📚 DONNÉES DANS LA BASE :
    Publications    : 1523
    Auteurs         : 3891
    Thèmes          : 47

📊 OPÉRATIONS EFFECTUÉES :
    Collectées      : 1587
    Créées          : 1523
    Mises à jour    : 32
    Ignorées        : 32
    Nouveaux auteurs: 3891
    Nouveaux thèmes : 47

✅ Aucune erreur

🎯 STATISTIQUES PAR REQUÊTE :
    'deep learning':
      - Collectées : 187
      - Créées     : 178
      - Durée      : 45.2s
    ...

================================================================================
✅ PEUPLEMENT TERMINÉ EN 0:12:34
================================================================================
```

---

## 🔧 Architecture Technique

### Pipeline ETL

Le script utilise `ArxivPipeline` qui orchestre :

1. **Extract** : Collecte depuis arXiv API avec rate limiting
2. **Transform** : Mappage vers modèles de base de données
3. **Load** : Insertion avec déduplication

### Composants Utilisés

```python
app/pipelines/
├── arxiv_collector.py      # Collection arXiv avec retry logic
├── arxiv_pipeline.py        # Orchestrateur ETL complet
├── arxiv_mappers.py         # Transformation données
├── deduplication.py         # Gestion doublons
└── ml_classifier.py         # Classification thématique
```

### Gestion Erreurs

- **Rate limiting** : Respect des limites arXiv (1 req/3s)
- **Retry automatique** : 3 tentatives avec backoff exponentiel
- **Skip gracieux** : Continue en cas d'erreur sur une publication
- **Logs détaillés** : Toutes les erreurs sont logguées

---

## 🐛 Troubleshooting

### Erreur : "No such file or directory"

```bash
# Vérifier que le script existe
docker-compose -f docker-compose.staging.yml exec api ls -la scripts/

# Si absent, recréer le script
# (uploader depuis l'hôte ou recréer dans le conteneur)
```

### Erreur : "Module 'app' not found"

```bash
# Le script doit être exécuté depuis /app dans le conteneur
docker-compose -f docker-compose.staging.yml exec api bash
cd /app
python scripts/populate_real_data.py
```

### Erreur : "Connection refused" (PostgreSQL)

```bash
# Vérifier que PostgreSQL est UP
docker-compose -f docker-compose.staging.yml ps

# Vérifier les variables d'environnement
docker-compose -f docker-compose.staging.yml exec api env | grep DATABASE
```

### Performances Lentes

```bash
# Réduire le nombre de publications pour test
python scripts/populate_real_data.py --max-publications 500

# Augmenter le batch size (attention au rate limit)
python scripts/populate_real_data.py --batch-size 50
```

### Interruption (Ctrl+C)

Le script gère gracieusement les interruptions. Les publications déjà insérées restent en base grâce aux commits transactionnels.

---

## 📈 Monitoring

### Vérifier Progression en Base

```bash
# Depuis l'hôte
docker-compose -f docker-compose.staging.yml exec postgres psql -U deeo_user -d deeo_ai_staging -c "SELECT COUNT(*) FROM publications;"

# Nombre d'auteurs
docker-compose -f docker-compose.staging.yml exec postgres psql -U deeo_user -d deeo_ai_staging -c "SELECT COUNT(*) FROM auteurs;"

# Thèmes créés
docker-compose -f docker-compose.staging.yml exec postgres psql -U deeo_user -d deeo_ai_staging -c "SELECT label, COUNT(*) as nb FROM themes GROUP BY label ORDER BY nb DESC LIMIT 10;"
```

### Logs en Temps Réel

```bash
# Suivre les logs du conteneur API
docker-compose -f docker-compose.staging.yml logs -f api
```

---

## 🔄 Réinitialisation

Pour effacer les données et recommencer :

```bash
# Entrer dans PostgreSQL
docker-compose -f docker-compose.staging.yml exec postgres psql -U deeo_user -d deeo_ai_staging

# Truncate tables (dans psql)
TRUNCATE TABLE publications CASCADE;
TRUNCATE TABLE auteurs CASCADE;
TRUNCATE TABLE themes CASCADE;
```

**⚠️ Attention** : `CASCADE` supprime aussi les relations (publication_auteurs, publication_themes, etc.)

---

## 📝 Notes Importantes

### Rate Limiting arXiv

L'API arXiv limite à **1 requête par 3 secondes**. Le script respecte cette limite automatiquement avec `aiolimiter`.

### Temps d'Exécution Estimé

- **500 publications** : ~3-5 minutes
- **5,000 publications** : ~30-45 minutes
- **15,000 publications** : ~1.5-2 heures

Le temps varie selon :
- La charge de l'API arXiv
- La vitesse réseau
- Le nombre d'auteurs/thèmes nouveaux

### Semantic Scholar

L'enrichissement Semantic Scholar (citations, h-index) n'est **pas encore implémenté** dans ce script. Il sera ajouté dans une version ultérieure avec `semantic_scholar_enricher.py`.

---

## ✅ Checklist Post-Exécution

- [ ] Vérifier nombre de publications en base
- [ ] Vérifier que les relations auteurs sont créées
- [ ] Vérifier que les thèmes sont assignés
- [ ] Tester l'API frontend (`/api/v1/publications`)
- [ ] Vérifier logs pour erreurs éventuelles
- [ ] Backup de la base (optionnel)

---

**Créé le** : 20 novembre 2025
**Version** : 1.0.0
**Auteur** : Claude Code Assistant
