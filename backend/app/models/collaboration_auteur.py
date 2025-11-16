"""
Table d'association collaboration_auteur
"""
from sqlalchemy import Column, String, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class CollaborationAuteur(Base, TimestampMixin):
    """Association entre Collaboration et Auteur."""
    __tablename__ = "collaboration_auteur"
    
    collaboration_id = Column(
        UUID(as_uuid=True),
        ForeignKey('collaboration.id', ondelete='CASCADE'),
        primary_key=True
    )
    auteur_id = Column(
        UUID(as_uuid=True),
        ForeignKey('auteur.id', ondelete='CASCADE'),
        primary_key=True
    )
    
    role = Column(String(100), comment="Rôle dans la collaboration")
    
    __table_args__ = (
        Index('idx_collaboration_auteur_collaboration', 'collaboration_id'),
        Index('idx_collaboration_auteur_auteur', 'auteur_id'),
    )
    
    collaboration = relationship("Collaboration", back_populates="auteurs", lazy="select")
    auteur = relationship("Auteur", back_populates="collaborations", lazy="select")
