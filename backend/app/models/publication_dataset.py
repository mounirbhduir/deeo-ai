"""
Table d'association publication_dataset
"""
from sqlalchemy import Column, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class PublicationDataset(Base, TimestampMixin):
    """Association entre Publication et Dataset."""
    __tablename__ = "publication_dataset"
    
    publication_id = Column(
        UUID(as_uuid=True),
        ForeignKey('publication.id', ondelete='CASCADE'),
        primary_key=True
    )
    dataset_id = Column(
        UUID(as_uuid=True),
        ForeignKey('dataset.id', ondelete='CASCADE'),
        primary_key=True
    )
    
    __table_args__ = (
        Index('idx_publication_dataset_publication', 'publication_id'),
        Index('idx_publication_dataset_dataset', 'dataset_id'),
    )
    
    publication = relationship("Publication", back_populates="datasets", lazy="select")
    dataset = relationship("Dataset", back_populates="publications", lazy="select")
