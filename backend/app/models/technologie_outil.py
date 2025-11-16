"""
Table d'association technologie_outil
"""
from sqlalchemy import Column, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class TechnologieOutil(Base, TimestampMixin):
    """Association entre Technologie et Outil."""
    __tablename__ = "technologie_outil"
    
    technologie_id = Column(
        UUID(as_uuid=True),
        ForeignKey('technologie.id', ondelete='CASCADE'),
        primary_key=True
    )
    outil_id = Column(
        UUID(as_uuid=True),
        ForeignKey('outil.id', ondelete='CASCADE'),
        primary_key=True
    )
    
    __table_args__ = (
        Index('idx_technologie_outil_technologie', 'technologie_id'),
        Index('idx_technologie_outil_outil', 'outil_id'),
    )
    
    technologie = relationship("Technologie", back_populates="outils_associes", lazy="select")
    outil = relationship("Outil", back_populates="technologies_associees", lazy="select")
