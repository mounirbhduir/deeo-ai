"""
Table d'association publication_outil
"""
from sqlalchemy import Column, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class PublicationOutil(Base, TimestampMixin):
    """Association entre Publication et Outil."""
    __tablename__ = "publication_outil"
    
    publication_id = Column(
        UUID(as_uuid=True),
        ForeignKey('publication.id', ondelete='CASCADE'),
        primary_key=True
    )
    outil_id = Column(
        UUID(as_uuid=True),
        ForeignKey('outil.id', ondelete='CASCADE'),
        primary_key=True
    )
    
    __table_args__ = (
        Index('idx_publication_outil_publication', 'publication_id'),
        Index('idx_publication_outil_outil', 'outil_id'),
    )
    
    publication = relationship("Publication", back_populates="outils", lazy="select")
    outil = relationship("Outil", back_populates="publications", lazy="select")
