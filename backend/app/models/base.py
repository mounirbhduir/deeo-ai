"""
Classes de base pour tous les modèles SQLAlchemy de DEEO.AI

Ce module définit :
- Base : Classe déclarative de base pour tous les modèles
- TimestampMixin : Ajoute created_at et updated_at automatiques
- UUIDMixin : Ajoute clé primaire UUID auto-générée
"""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Classe de base pour tous les modèles SQLAlchemy.
    
    Tous les modèles doivent hériter de cette classe pour bénéficier
    des fonctionnalités communes de SQLAlchemy 2.0.
    """
    pass


class TimestampMixin:
    """
    Mixin pour ajouter automatiquement les timestamps created_at et updated_at.
    
    - created_at : Date de création (automatique à l'INSERT)
    - updated_at : Date de dernière modification (automatique à l'UPDATE via trigger)
    
    Usage:
        class MyModel(Base, TimestampMixin):
            ...
    """
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Date de création de l'enregistrement"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Date de dernière modification"
    )


class UUIDMixin:
    """
    Mixin pour ajouter une clé primaire UUID auto-générée.
    
    Utilise uuid4() pour générer des UUID aléatoires et uniques.
    Avantages :
    - Génération distribuée sans collision
    - Sécurité (pas de séquentialité)
    - Compatible microservices
    
    Usage:
        class MyModel(Base, UUIDMixin, TimestampMixin):
            ...
    """
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False,
        comment="Identifiant unique UUID"
    )
