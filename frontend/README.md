# DEEO.AI - Frontend

Interface utilisateur React pour la plateforme DEEO.AI (AI Dynamic Emergence and Evolution Observatory).

## Stack Technique

- **React 18** + **TypeScript**
- **Vite** (build tool ultra-rapide)
- **Tailwind CSS** (styling utilitaire)
- **TanStack Query** (data fetching & caching)
- **React Router** (routing SPA)
- **Axios** (HTTP client)
- **Recharts** (visualisations de données)
- **Lucide React** (icônes modernes)
- **React Hook Form** (formulaires)
- **Headless UI** (composants accessibles)

## Installation

```bash
cd frontend
npm install
```

## Développement

```bash
npm run dev
```

L'application sera accessible à : **http://localhost:5173**

Le serveur de développement démarre avec Hot Module Replacement (HMR) pour un rechargement instantané.

## Build Production

```bash
npm run build
npm run preview
```

Le build optimisé sera généré dans le dossier `dist/`.

## Tests

```bash
# Lancer les tests
npm run test

# Tests avec interface
npm run test:ui

# Couverture de tests
npm run test:coverage
```

## Linting & Formatting

```bash
# Vérifier le code
npm run lint

# Corriger automatiquement
npm run lint:fix

# Formater le code
npm run format

# Vérifier les types TypeScript
npm run type-check
```

## Docker

### Build

```bash
docker build -t deeo-frontend .
```

### Run

```bash
docker run -p 3000:80 deeo-frontend
```

L'application sera accessible à : **http://localhost:3000**

## Structure du Projet

```
frontend/
├── public/              # Assets statiques
├── src/
│   ├── pages/          # Pages (routes)
│   ├── components/     # Composants réutilisables
│   │   ├── layout/    # Composants layout (Header, Footer, etc.)
│   │   ├── common/    # Composants communs (Button, Card, etc.)
│   │   └── charts/    # Composants graphiques
│   ├── api/           # Client API & requêtes
│   ├── hooks/         # Custom React hooks
│   ├── types/         # Types TypeScript
│   ├── utils/         # Fonctions utilitaires
│   ├── config/        # Configuration & constantes
│   └── styles/        # Styles globaux
├── index.html         # Point d'entrée HTML
├── vite.config.ts     # Configuration Vite
├── tsconfig.json      # Configuration TypeScript
└── tailwind.config.js # Configuration Tailwind CSS
```

## Variables d'Environnement

Copier `.env.example` vers `.env.local` et ajuster les valeurs :

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=DEEO.AI
VITE_APP_VERSION=1.0.0
```

## API Backend

L'API backend doit être accessible à : **http://localhost:8000/api/v1**

Documentation Swagger : **http://localhost:8000/docs**

Le proxy Vite redirige automatiquement les requêtes `/api/*` vers le backend.

## Fonctionnalités Principales (À venir)

- **Dashboard** : Vue d'ensemble de l'écosystème IA
- **Recherche** : Recherche avancée de publications
- **Visualisations** : Graphiques interactifs (évolution thèmes, top auteurs, etc.)
- **Profils** : Pages détaillées auteurs & organisations
- **Thèmes** : Exploration par thématiques ML/IA
- **Filtres** : Filtrage multi-critères (dates, citations, thèmes, etc.)

## Scripts Disponibles

| Commande | Description |
|----------|-------------|
| `npm run dev` | Démarre le serveur de développement |
| `npm run build` | Build de production |
| `npm run preview` | Prévisualise le build de production |
| `npm run lint` | Vérifie le code avec ESLint |
| `npm run lint:fix` | Corrige automatiquement les erreurs ESLint |
| `npm run format` | Formate le code avec Prettier |
| `npm run type-check` | Vérifie les types TypeScript |
| `npm run test` | Lance les tests |
| `npm run test:ui` | Lance les tests avec interface |
| `npm run test:coverage` | Génère le rapport de couverture |

## Technologies & Dépendances

### Production

- **react** & **react-dom** : Librairie UI
- **react-router-dom** : Routing
- **@tanstack/react-query** : Data fetching & state
- **axios** : HTTP client
- **recharts** : Graphiques
- **tailwindcss** : Styling
- **clsx** : Utilitaire classes CSS
- **lucide-react** : Icônes
- **date-fns** : Manipulation de dates
- **react-hook-form** : Gestion formulaires
- **@headlessui/react** : Composants UI accessibles

### Développement

- **vite** : Build tool
- **typescript** : Typage statique
- **eslint** : Linting
- **prettier** : Formatage
- **vitest** : Testing framework
- **@testing-library/react** : Tests composants React

## Auteur

**Mounir** - Master Big Data & AI - UIR

## Projet

DEEO.AI - AI Dynamic Emergence and Evolution Observatory

**Phase 4** : Frontend React & Analytics
**Étape 1** : Setup Projet (Complétée)

---

**Next Steps** : Phase 4 Étape 2 - Architecture de Base (Layout, Router, Navigation)
