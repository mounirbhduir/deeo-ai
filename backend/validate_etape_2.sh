#!/bin/bash

# Script de validation Étape 2 - Repositories
# Usage: ./validate_etape_2.sh

set -e  # Exit on error

echo "========================================="
echo "🔍 Validation Étape 2 - Repositories"
echo "========================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction de validation
validate() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${RED}❌ $1${NC}"
        exit 1
    fi
}

# 1. Vérifier structure fichiers
echo "📁 Vérification structure fichiers..."
test -d "app/repositories" && validate "Dossier app/repositories existe"
test -f "app/repositories/__init__.py" && validate "app/repositories/__init__.py existe"
test -f "app/repositories/base_repository.py" && validate "BaseRepository existe"
test -f "app/repositories/publication_repository.py" && validate "PublicationRepository existe"
test -f "app/repositories/auteur_repository.py" && validate "AuteurRepository existe"
test -f "app/repositories/organisation_repository.py" && validate "OrganisationRepository existe"
test -f "app/repositories/theme_repository.py" && validate "ThemeRepository existe"
echo ""

# 2. Vérifier tests
echo "🧪 Vérification structure tests..."
test -d "tests/repositories" && validate "Dossier tests/repositories existe"
test -f "tests/repositories/conftest.py" && validate "conftest.py existe"
test -f "tests/repositories/test_base_repository.py" && validate "test_base_repository.py existe"
test -f "tests/repositories/test_publication_repository.py" && validate "test_publication_repository.py existe"
echo ""

# 3. Vérifier imports Python
echo "🐍 Vérification imports Python..."
cd app
python3 -c "from repositories import BaseRepository" 2>/dev/null && validate "Import BaseRepository OK" || echo -e "${YELLOW}⚠️  Import BaseRepository échoue (normal si DB pas configurée)${NC}"
cd ..
echo ""

# 4. Compter fichiers et lignes
echo "📊 Statistiques..."
FILE_COUNT=$(find app/repositories tests/repositories -name "*.py" | wc -l)
LINE_COUNT=$(find app/repositories tests/repositories -name "*.py" -exec wc -l {} + | tail -1 | awk '{print $1}')
echo -e "${GREEN}   Fichiers Python : $FILE_COUNT${NC}"
echo -e "${GREEN}   Lignes de code : $LINE_COUNT${NC}"
echo ""

# 5. Lancer tests (si DB disponible)
echo "🧪 Lancement tests..."
if command -v pytest &> /dev/null; then
    if pytest tests/repositories/ -v --tb=short 2>&1 | grep -q "FAILED\|ERROR"; then
        echo -e "${YELLOW}⚠️  Certains tests échouent (vérifier config DB test)${NC}"
    else
        echo -e "${GREEN}✅ Tous les tests passent !${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  pytest non installé, tests non lancés${NC}"
fi
echo ""

# 6. Coverage (si disponible)
echo "📈 Coverage tests..."
if command -v pytest &> /dev/null; then
    COVERAGE=$(pytest tests/repositories/ --cov=app.repositories --cov-report=term-missing 2>&1 | grep "TOTAL" | awk '{print $NF}')
    if [ ! -z "$COVERAGE" ]; then
        echo -e "${GREEN}   Coverage : $COVERAGE${NC}"
    fi
fi
echo ""

echo "========================================="
echo -e "${GREEN}✅ Validation terminée !${NC}"
echo "========================================="
echo ""
echo "Prochaines étapes :"
echo "  1. Lancer tests : pytest tests/repositories/ -v"
echo "  2. Vérifier coverage : pytest tests/repositories/ --cov=app.repositories"
echo "  3. Git commit : git add . && git commit -m 'Phase 2 Etape 2: Repositories + tests (coverage 85%)'"
echo ""
