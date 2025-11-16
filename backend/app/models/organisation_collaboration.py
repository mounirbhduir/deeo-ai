"""
Table d'association organisation_collaboration
"""
from sqlalchemy import Column, String, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class OrganisationCollaboration(Base, TimestampMixin):
    """Association entre Organisation et Collaboration (partenaires)."""
    __tablename__ = "organisation_collaboration"
    
    organisation_id = Column(
        UUID(as_uuid=True),
        ForeignKey('organisation.id', ondelete='CASCADE'),
        primary_key=True
    )
    collaboration_id = Column(
        UUID(as_uuid=True),
        ForeignKey('collaboration.id', ondelete='CASCADE'),
        primary_key=True
    )
    
    role = Column(String(100), comment="Rôle de l'organisation dans la collaboration")
    
    __table_args__ = (
        Index('idx_organisation_collaboration_organisation', 'organisation_id'),
        Index('idx_organisation_collaboration_collaboration', 'collaboration_id'),
    )
    
    collaboration = relationship("Collaboration", back_populates="organisations_partenaires", lazy="select")
