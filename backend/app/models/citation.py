"""
Table d'association citation (auto-référence Publication)
"""
from sqlalchemy import Column, Text, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class Citation(Base, TimestampMixin):
    """
    Citation entre deux publications (auto-référence).
    
    Attributes:
        publication_source_id: Publication qui cite
        publication_cible_id: Publication citée
        contexte: Contexte de la citation (extrait du texte)
    """
    __tablename__ = "citation"
    
    publication_source_id = Column(
        UUID(as_uuid=True),
        ForeignKey('publication.id', ondelete='CASCADE'),
        primary_key=True,
        comment="Publication qui cite"
    )
    publication_cible_id = Column(
        UUID(as_uuid=True),
        ForeignKey('publication.id', ondelete='CASCADE'),
        primary_key=True,
        comment="Publication citée"
    )
    
    contexte = Column(
        Text,
        comment="Contexte de la citation (extrait du texte)"
    )
    
    __table_args__ = (
        CheckConstraint('publication_source_id != publication_cible_id',
                       name='check_citation_no_self_citation'),
        Index('idx_citation_source', 'publication_source_id'),
        Index('idx_citation_cible', 'publication_cible_id'),
    )
    
    publication_source = relationship(
        "Publication",
        foreign_keys=[publication_source_id],
        back_populates="citations_sources",
        lazy="select"
    )
    publication_cible = relationship(
        "Publication",
        foreign_keys=[publication_cible_id],
        back_populates="citations_cibles",
        lazy="select"
    )
