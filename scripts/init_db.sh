#!/bin/bash
# Script d'initialisation PostgreSQL - Activer extensions

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Activer extensions
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
    
    -- Afficher extensions activées
    SELECT extname, extversion FROM pg_extension;
EOSQL

echo "✅ Extensions PostgreSQL activées"
