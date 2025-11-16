"""
Table d'association publication_impact
"""
from sqlalchemy import Column, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class PublicationImpact(Base, TimestampMixin):
    """Association entre Publication et ImpactSocietal."""
    __tablename__ = "publication_impact"
    
    publication_id = Column(
        UUID(as_uuid=True),
        ForeignKey('publication.id', ondelete='CASCADE'),
        primary_key=True
    )
    impact_id = Column(
        UUID(as_uuid=True),
        ForeignKey('impact_societal.id', ondelete='CASCADE'),
        primary_key=True
    )
    
    __table_args__ = (
        Index('idx_publication_impact_publication', 'publication_id'),
        Index('idx_publication_impact_impact', 'impact_id'),
    )
    
    publication = relationship("Publication", back_populates="impacts", lazy="select")
    impact = relationship("ImpactSocietal", back_populates="publications", lazy="select")
