"""
Table d'association auteur_metrique
"""
from sqlalchemy import Column, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class AuteurMetrique(Base, TimestampMixin):
    """Association entre Auteur et MetriqueEngagement."""
    __tablename__ = "auteur_metrique"
    
    auteur_id = Column(
        UUID(as_uuid=True),
        ForeignKey('auteur.id', ondelete='CASCADE'),
        primary_key=True
    )
    metrique_id = Column(
        UUID(as_uuid=True),
        ForeignKey('metrique_engagement.id', ondelete='CASCADE'),
        primary_key=True
    )
    
    __table_args__ = (
        Index('idx_auteur_metrique_auteur', 'auteur_id'),
        Index('idx_auteur_metrique_metrique', 'metrique_id'),
    )
    
    metrique = relationship("MetriqueEngagement", back_populates="auteurs", lazy="select")
