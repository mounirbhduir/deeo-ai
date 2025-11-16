"""
Modèle SQLAlchemy pour la table changement_metadonnees

Historique des changements de métadonnées (audit trail)
"""
from sqlalchemy import Column, String, Text, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB

from .base import Base, UUIDMixin, TimestampMixin


class ChangementMetadonnees(Base, UUIDMixin, TimestampMixin):
    """
    Historique des changements de métadonnées (audit trail).
    
    Permet de tracer qui a modifié quoi et quand.
    
    Attributes:
        entite_type: Type d'entité modifiée (ex: "Publication", "Auteur")
        entite_id: ID de l'entité modifiée
        champ_modifie: Nom du champ modifié
        ancienne_valeur: Ancienne valeur (JSON)
        nouvelle_valeur: Nouvelle valeur (JSON)
        date_changement: Date/heure du changement
        utilisateur: Utilisateur ayant effectué le changement
        raison: Raison du changement (optionnel)
    """
    __tablename__ = "changement_metadonnees"
    
    # Référence à l'entité modifiée
    entite_type = Column(
        String(100),
        nullable=False,
        comment="Type d'entité modifiée (Publication, Auteur, etc.)"
    )
    entite_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        comment="ID de l'entité modifiée"
    )
    
    # Détails du changement
    champ_modifie = Column(
        String(255),
        nullable=False,
        comment="Nom du champ modifié"
    )
    ancienne_valeur = Column(
        JSONB,
        comment="Ancienne valeur (format JSON)"
    )
    nouvelle_valeur = Column(
        JSONB,
        comment="Nouvelle valeur (format JSON)"
    )
    
    # Métadonnées du changement
    date_changement = Column(
        DateTime,
        nullable=False,
        comment="Date et heure du changement"
    )
    utilisateur = Column(
        String(255),
        comment="Utilisateur ayant effectué le changement"
    )
    raison = Column(
        Text,
        comment="Raison du changement (optionnel)"
    )
    
    # Contraintes
    __table_args__ = (
        Index('idx_changement_entite', 'entite_type', 'entite_id'),
        Index('idx_changement_date', 'date_changement', postgresql_ops={'date_changement': 'DESC'}),
        Index('idx_changement_utilisateur', 'utilisateur'),
    )
    
    def __repr__(self):
        return f"<ChangementMetadonnees(id={self.id}, entite='{self.entite_type}', champ='{self.champ_modifie}')>"
