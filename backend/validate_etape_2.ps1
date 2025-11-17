# Script de Validation Étape 2 - Repositories
# DEEO.AI Phase 2

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VALIDATION ÉTAPE 2 - REPOSITORIES" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Vérifier structure repositories
Write-Host "[1/5] Vérification structure app/repositories..." -ForegroundColor Yellow
$repoFiles = @(
    "app/repositories/__init__.py",
    "app/repositories/base_repository.py",
    "app/repositories/publication_repository.py",
    "app/repositories/auteur_repository.py",
    "app/repositories/organisation_repository.py",
    "app/repositories/theme_repository.py"
)

$missingRepoFiles = @()
foreach ($file in $repoFiles) {
    if (-not (Test-Path $file)) {
        $missingRepoFiles += $file
    }
}

if ($missingRepoFiles.Count -eq 0) {
    Write-Host "✓ Tous les fichiers repositories présents (6/6)" -ForegroundColor Green
} else {
    Write-Host "✗ Fichiers manquants :" -ForegroundColor Red
    $missingRepoFiles | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    exit 1
}

# Vérifier structure tests
Write-Host "`n[2/5] Vérification structure tests/repositories..." -ForegroundColor Yellow
$testFiles = @(
    "tests/repositories/conftest.py",
    "tests/repositories/test_base_repository.py",
    "tests/repositories/test_publication_repository.py",
    "tests/repositories/test_auteur_repository.py",
    "tests/repositories/test_organisation_repository.py",
    "tests/repositories/test_theme_repository.py"
)

$missingTestFiles = @()
foreach ($file in $testFiles) {
    if (-not (Test-Path $file)) {
        $missingTestFiles += $file
    }
}

if ($missingTestFiles.Count -eq 0) {
    Write-Host "✓ Tous les fichiers tests présents (6/6)" -ForegroundColor Green
} else {
    Write-Host "✗ Fichiers manquants :" -ForegroundColor Red
    $missingTestFiles | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    exit 1
}

# Vérifier syntaxe Python (compilation)
Write-Host "`n[3/5] Vérification syntaxe Python..." -ForegroundColor Yellow
$syntaxOk = $true
Get-ChildItem -Path "app/repositories/*.py" | ForEach-Object {
    $result = docker-compose exec -T api python -m py_compile $_.FullName.Replace('C:\Users\user\deeo-ai-workspace\deeo-ai-poc\backend\', '/app/') 2>&1
    if ($LASTEXITCODE -ne 0) {
        $syntaxOk = $false
        Write-Host "✗ Erreur dans $($_.Name)" -ForegroundColor Red
    }
}

if ($syntaxOk) {
    Write-Host "✓ Syntaxe Python valide" -ForegroundColor Green
} else {
    Write-Host "✗ Erreurs de syntaxe détectées" -ForegroundColor Red
    exit 1
}

# Vérifier imports
Write-Host "`n[4/5] Vérification imports..." -ForegroundColor Yellow
$importResult = docker-compose exec -T api python -c "from app.repositories import BaseRepository, PublicationRepository, AuteurRepository, OrganisationRepository, ThemeRepository" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Tous les imports fonctionnent" -ForegroundColor Green
} else {
    Write-Host "✗ Erreurs d'imports" -ForegroundColor Red
    Write-Host $importResult -ForegroundColor Red
    exit 1
}

# Compter méthodes implémentées
Write-Host "`n[5/5] Comptage méthodes repositories..." -ForegroundColor Yellow
$baseMethodCount = (Select-String -Path "app/repositories/base_repository.py" -Pattern "^\s+async def " | Measure-Object).Count
$pubMethodCount = (Select-String -Path "app/repositories/publication_repository.py" -Pattern "^\s+async def " | Measure-Object).Count
$autMethodCount = (Select-String -Path "app/repositories/auteur_repository.py" -Pattern "^\s+async def " | Measure-Object).Count

Write-Host "  BaseRepository: $baseMethodCount méthodes" -ForegroundColor Cyan
Write-Host "  PublicationRepository: $pubMethodCount méthodes" -ForegroundColor Cyan
Write-Host "  AuteurRepository: $autMethodCount méthodes" -ForegroundColor Cyan

if ($baseMethodCount -ge 6 -and $pubMethodCount -ge 6 -and $autMethodCount -ge 4) {
    Write-Host "✓ Nombre de méthodes conforme" -ForegroundColor Green
} else {
    Write-Host "✗ Nombre de méthodes insuffisant" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "VALIDATION RÉUSSIE ✓" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan
Write-Host "Prochaines étapes :" -ForegroundColor Yellow
Write-Host "  1. Lancer les tests : docker-compose exec api pytest tests/repositories/ --cov=app.repositories -v" -ForegroundColor White
Write-Host "  2. Commit Git : git add . && git commit -m 'Phase 2 Etape 2: Repositories + tests'" -ForegroundColor White
