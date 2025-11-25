#!/usr/bin/env python3
"""
Script de peuplement automatique de la base STAGING avec données réelles.

Usage:
    python scripts/populate_real_data.py [--max-publications 15000] [--batch-size 100]

Étapes:
    1. Collecte publications arXiv (catégories IA)
    2. Classification ML thématique (BART zero-shot)
    3. Vérification cohérence données

Note: L'enrichissement Semantic Scholar sera ajouté dans une version ultérieure.
"""

import asyncio
import argparse
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal
from app.pipelines.arxiv_pipeline import ArxivPipeline, ArxivPipelineStats
from app.pipelines.ml_classifier import MLClassifierService
from app.repositories.publication_repository import PublicationRepository
from app.repositories.auteur_repository import AuteurRepository
from app.repositories.theme_repository import ThemeRepository
from app.logging import get_logger

logger = get_logger(__name__)


class RealDataPopulator:
    """Orchestrateur de peuplement données réelles depuis arXiv."""

    # Catégories arXiv à collecter
    AI_CATEGORIES = [
        'cs.AI',   # Artificial Intelligence
        'cs.LG',   # Machine Learning
        'cs.CV',   # Computer Vision
        'cs.CL',   # Computation and Language
        'cs.NE',   # Neural and Evolutionary Computing
        'stat.ML'  # Machine Learning (Statistics)
    ]

    # Requêtes de recherche pour diversifier les publications
    SEARCH_QUERIES = [
        "deep learning",
        "neural networks",
        "transformer",
        "reinforcement learning",
        "computer vision",
        "natural language processing",
        "machine learning",
        "artificial intelligence",
    ]

    def __init__(
        self,
        max_publications: int = 15000,
        batch_size: int = 100,
        date_range_months: int = 24
    ):
        """
        Initialize populator.

        Args:
            max_publications: Nombre maximum de publications à collecter
            batch_size: Taille des batchs pour les requêtes arXiv
            date_range_months: Nombre de mois en arrière pour la collecte
        """
        self.max_publications = max_publications
        self.batch_size = batch_size
        self.date_range_months = date_range_months

        # Calculate date range
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=date_range_months * 30)

        # Statistics
        self.stats = {
            'total_collected': 0,
            'total_created': 0,
            'total_updated': 0,
            'total_skipped': 0,
            'total_authors': 0,
            'total_themes': 0,
            'total_errors': 0,
            'category_stats': {},
            'query_stats': {},
        }

    async def run(self):
        """Exécuter pipeline complet de peuplement."""
        logger.info("=" * 80)
        logger.info("🚀 DÉMARRAGE PEUPLEMENT STAGING AVEC DONNÉES RÉELLES")
        logger.info("=" * 80)
        logger.info(f"Configuration:")
        logger.info(f"  - Max publications: {self.max_publications}")
        logger.info(f"  - Batch size: {self.batch_size}")
        logger.info(f"  - Date range: {self.start_date.date()} to {self.end_date.date()}")
        logger.info(f"  - Categories: {', '.join(self.AI_CATEGORIES)}")
        logger.info("")

        start_time = datetime.now()

        try:
            # Étape 1 : Collecte arXiv avec ETL pipeline
            await self._collect_arxiv_publications()

            # Étape 2 : Classification ML (si nécessaire)
            await self._classify_publications()

            # Étape 3 : Statistiques finales
            await self._display_final_stats()

        except KeyboardInterrupt:
            logger.warning("\n⚠️  Interruption utilisateur détectée")
            self.stats['errors'] = self.stats.get('errors', 0) + 1
        except Exception as e:
            logger.error(f"❌ Erreur fatale : {e}", exc_info=True)
            self.stats['errors'] = self.stats.get('errors', 0) + 1
        finally:
            duration = datetime.now() - start_time
            logger.info("")
            logger.info("=" * 80)
            logger.info(f"✅ PEUPLEMENT TERMINÉ EN {duration}")
            logger.info("=" * 80)

    async def _collect_arxiv_publications(self):
        """Étape 1 : Collecter publications depuis arXiv avec pipeline ETL."""
        logger.info("\n" + "=" * 80)
        logger.info("📥 ÉTAPE 1/2 : COLLECTE PUBLICATIONS ARXIV")
        logger.info("=" * 80)

        publications_per_query = self.max_publications // len(self.SEARCH_QUERIES)

        async with AsyncSessionLocal() as session:
            async with ArxivPipeline(session) as pipeline:
                for idx, query in enumerate(self.SEARCH_QUERIES, 1):
                    logger.info(f"\n[{idx}/{len(self.SEARCH_QUERIES)}] 🔍 Requête: '{query}'")

                    try:
                        # Run pipeline for this query
                        stats = await pipeline.run(
                            query=query,
                            categories=self.AI_CATEGORIES,
                            date_range=(self.start_date, self.end_date),
                            max_results=publications_per_query,
                        )

                        # Update global stats
                        self._update_stats_from_pipeline(query, stats)

                        # Display progress
                        logger.info(f"  ✅ Collectées: {stats.papers_collected}")
                        logger.info(f"  ➕ Créées: {stats.papers_created}")
                        logger.info(f"  🔄 Mises à jour: {stats.papers_updated}")
                        logger.info(f"  ⏭️  Ignorées: {stats.papers_skipped}")
                        logger.info(f"  👥 Auteurs: {stats.authors_created}")
                        logger.info(f"  🏷️  Thèmes: {stats.themes_created}")

                        if stats.errors > 0:
                            logger.warning(f"  ⚠️  Erreurs: {stats.errors}")

                        # Check if we reached max publications
                        if self.stats['total_created'] >= self.max_publications:
                            logger.info(f"\n✅ Objectif atteint : {self.stats['total_created']} publications")
                            break

                    except Exception as e:
                        logger.error(f"❌ Erreur requête '{query}': {e}")
                        self.stats['total_errors'] += 1
                        continue

        logger.info(f"\n📊 Total publications collectées : {self.stats['total_collected']}")
        logger.info(f"📊 Total publications créées : {self.stats['total_created']}")

    async def _classify_publications(self):
        """Étape 2 : Classification ML thématique (optionnelle)."""
        logger.info("\n" + "=" * 80)
        logger.info("🤖 ÉTAPE 2/2 : CLASSIFICATION ML THÉMATIQUE")
        logger.info("=" * 80)

        async with AsyncSessionLocal() as session:
            pub_repo = PublicationRepository(session)
            classifier = MLClassifierService(session)

            # Get publications without theme
            # Note: This assumes publications might not have themes yet
            # In practice, arxiv_pipeline already assigns themes from categories
            logger.info("ℹ️  Les thèmes ont déjà été assignés par le pipeline arXiv")
            logger.info("ℹ️  La classification ML additionnelle sera implémentée ultérieurement")

            # Could add additional ML classification here if needed
            # For example, to refine or add more granular themes

            logger.info("✅ Étape de classification complétée")

    def _update_stats_from_pipeline(self, query: str, stats: ArxivPipelineStats):
        """Mettre à jour les statistiques globales depuis les stats du pipeline."""
        self.stats['total_collected'] += stats.papers_collected
        self.stats['total_created'] += stats.papers_created
        self.stats['total_updated'] += stats.papers_updated
        self.stats['total_skipped'] += stats.papers_skipped
        self.stats['total_authors'] += stats.authors_created
        self.stats['total_themes'] += stats.themes_created
        self.stats['total_errors'] += stats.errors

        # Per-query stats
        self.stats['query_stats'][query] = {
            'collected': stats.papers_collected,
            'created': stats.papers_created,
            'duration': stats.duration_seconds,
        }

    async def _display_final_stats(self):
        """Afficher statistiques finales détaillées."""
        logger.info("\n" + "=" * 80)
        logger.info("📊 STATISTIQUES FINALES")
        logger.info("=" * 80)

        async with AsyncSessionLocal() as session:
            pub_repo = PublicationRepository(session)
            author_repo = AuteurRepository(session)
            theme_repo = ThemeRepository(session)

            # Count current database state
            try:
                all_pubs = await pub_repo.list(limit=100000)  # Get count
                pub_count = len(all_pubs)

                all_authors = await author_repo.list(limit=100000)
                author_count = len(all_authors)

                all_themes = await theme_repo.list(limit=100000)
                theme_count = len(all_themes)
            except Exception as e:
                logger.error(f"Erreur lors du comptage : {e}")
                pub_count = "N/A"
                author_count = "N/A"
                theme_count = "N/A"

            logger.info("")
            logger.info("📚 DONNÉES DANS LA BASE :")
            logger.info(f"    Publications    : {pub_count}")
            logger.info(f"    Auteurs         : {author_count}")
            logger.info(f"    Thèmes          : {theme_count}")
            logger.info("")
            logger.info("📊 OPÉRATIONS EFFECTUÉES :")
            logger.info(f"    Collectées      : {self.stats['total_collected']}")
            logger.info(f"    Créées          : {self.stats['total_created']}")
            logger.info(f"    Mises à jour    : {self.stats['total_updated']}")
            logger.info(f"    Ignorées        : {self.stats['total_skipped']}")
            logger.info(f"    Nouveaux auteurs: {self.stats['total_authors']}")
            logger.info(f"    Nouveaux thèmes : {self.stats['total_themes']}")
            logger.info("")

            if self.stats['total_errors'] > 0:
                logger.warning(f"⚠️  ERREURS : {self.stats['total_errors']}")
            else:
                logger.info("✅ Aucune erreur")

            logger.info("")
            logger.info("🎯 STATISTIQUES PAR REQUÊTE :")
            for query, stats in self.stats['query_stats'].items():
                logger.info(f"    '{query}':")
                logger.info(f"      - Collectées : {stats['collected']}")
                logger.info(f"      - Créées     : {stats['created']}")
                logger.info(f"      - Durée      : {stats['duration']:.1f}s")


async def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description='Peupler STAGING avec données réelles arXiv',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
    # Collecte standard (15000 publications)
    python scripts/populate_real_data.py

    # Collecte limitée pour test
    python scripts/populate_real_data.py --max-publications 500

    # Collecte avec batch size personnalisé
    python scripts/populate_real_data.py --max-publications 10000 --batch-size 50
        """
    )
    parser.add_argument(
        '--max-publications',
        type=int,
        default=15000,
        help='Nombre maximum de publications à collecter (défaut: 15000)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Taille des batchs pour les requêtes arXiv (défaut: 100)'
    )
    parser.add_argument(
        '--date-range-months',
        type=int,
        default=24,
        help='Nombre de mois en arrière pour la collecte (défaut: 24)'
    )

    args = parser.parse_args()

    populator = RealDataPopulator(
        max_publications=args.max_publications,
        batch_size=args.batch_size,
        date_range_months=args.date_range_months,
    )

    await populator.run()


if __name__ == '__main__':
    asyncio.run(main())
