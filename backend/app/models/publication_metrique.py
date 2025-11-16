"""
Table d'association publication_metrique
"""
from sqlalchemy import Column, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class PublicationMetrique(Base, TimestampMixin):
    """Association entre Publication et MetriqueEngagement."""
    __tablename__ = "publication_metrique"
    
    publication_id = Column(
        UUID(as_uuid=True),
        ForeignKey('publication.id', ondelete='CASCADE'),
        primary_key=True
    )
    metrique_id = Column(
        UUID(as_uuid=True),
        ForeignKey('metrique_engagement.id', ondelete='CASCADE'),
        primary_key=True
    )
    
    __table_args__ = (
        Index('idx_publication_metrique_publication', 'publication_id'),
        Index('idx_publication_metrique_metrique', 'metrique_id'),
    )
    
    publication = relationship("Publication", back_populates="metriques", lazy="select")
    metrique = relationship("MetriqueEngagement", back_populates="publications", lazy="select")
