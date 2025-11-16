"""
Table d'association publication_technologie
"""
from sqlalchemy import Column, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class PublicationTechnologie(Base, TimestampMixin):
    """Association entre Publication et Technologie."""
    __tablename__ = "publication_technologie"
    
    publication_id = Column(
        UUID(as_uuid=True),
        ForeignKey('publication.id', ondelete='CASCADE'),
        primary_key=True
    )
    technologie_id = Column(
        UUID(as_uuid=True),
        ForeignKey('technologie.id', ondelete='CASCADE'),
        primary_key=True
    )
    
    __table_args__ = (
        Index('idx_publication_technologie_publication', 'publication_id'),
        Index('idx_publication_technologie_technologie', 'technologie_id'),
    )
    
    publication = relationship("Publication", back_populates="technologies", lazy="select")
    technologie = relationship("Technologie", back_populates="publications", lazy="select")
