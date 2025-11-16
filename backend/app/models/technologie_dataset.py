"""
Table d'association technologie_dataset
"""
from sqlalchemy import Column, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class TechnologieDataset(Base, TimestampMixin):
    """Association entre Technologie et Dataset."""
    __tablename__ = "technologie_dataset"
    
    technologie_id = Column(
        UUID(as_uuid=True),
        ForeignKey('technologie.id', ondelete='CASCADE'),
        primary_key=True
    )
    dataset_id = Column(
        UUID(as_uuid=True),
        ForeignKey('dataset.id', ondelete='CASCADE'),
        primary_key=True
    )
    
    __table_args__ = (
        Index('idx_technologie_dataset_technologie', 'technologie_id'),
        Index('idx_technologie_dataset_dataset', 'dataset_id'),
    )
    
    technologie = relationship("Technologie", back_populates="datasets_associes", lazy="select")
    dataset = relationship("Dataset", back_populates="technologies_associees", lazy="select")
