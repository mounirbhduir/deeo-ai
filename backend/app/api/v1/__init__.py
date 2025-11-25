'''
API v1 routers.

This package contains all v1 API endpoint routers.
'''

from app.api.v1.publications import router as publications_router
from app.api.v1.auteurs import router as auteurs_router
from app.api.v1.organisations import router as organisations_router
from app.api.v1.themes import router as themes_router
from app.api.v1.datasets import router as datasets_router
from app.api.v1.statistics import router as statistics_router
from app.api.v1.graphs_mock import router as graphs_router

__all__ = [
    'publications_router',
    'auteurs_router',
    'organisations_router',
    'themes_router',
    'datasets_router',
    'statistics_router',
    'graphs_router',
]
