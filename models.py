from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class RequirementNature(str, Enum):
    """
    Nature d'une exigence réglementaire.
    """
    ABSOLUE = "ABSOLUE"
    CONDITIONNELLE = "CONDITIONNELLE"

class FindingSeverity(str, Enum):
    """
    Niveau de criticité d'un constat d'audit.
    """
    BLOQUANT = "BLOQUANT"
    MAJEUR = "MAJEUR"
    AMBIGU = "AMBIGU"
    CONFORME = "CONFORME"
    NON_APPLICABLE = "NON_APPLICABLE"

@dataclass
class Requirement:
    """
    Représente une exigence extraite de la directive.
    """
    article_id: str
    title: str
    short_text: str
    category: str
    nature: RequirementNature
    source_text: str
    condition: Optional[str] = None

@dataclass
class ProductInfos:
    """
    Représente la fiche produit une fois parsée et normalisée.
    On garde à la fois :
    - les métadonnées générales,
    - les infos documentaires,
    - les infos sécurité / conformité / notice,
    - les notes administratives.
    """
    manufacturer: Optional[str] = None
    address: Optional[str] = None
    signatory: Optional[str] = None
    reference: Optional[str] = None
    destination: Optional[str] = None
    target_markets: list[str] = field(default_factory=list)

    documentation: dict[str, str] = field(default_factory=dict)
    safety: dict[str, str] = field(default_factory=dict)
    conformity: dict[str, str] = field(default_factory=dict)
    user_docs: dict[str, str] = field(default_factory=dict)
    admin_notes: dict[str, str] = field(default_factory=dict)

@dataclass
class AuditFinding:
    """
    Constat produit par le comparateur.
    """
    article_id: str
    title: str
    severity: FindingSeverity
    description: str
    justification: str

@dataclass
class AuditResult:
    """
    Résultat complet de l'audit.
    """
    reference: str
    findings: list[AuditFinding]

    @property
    def blocking_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == FindingSeverity.BLOQUANT)

    @property
    def major_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == FindingSeverity.MAJEUR)

    @property
    def ambiguous_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == FindingSeverity.AMBIGU)

    @property
    def conform_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == FindingSeverity.CONFORME)

    @property
    def non_applicable_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == FindingSeverity.NON_APPLICABLE)

    @property
    def final_status(self) -> str:
        """
        Ici on va appliquer une règle simple :
        - s'il y a au moins un BLOQUANT ou MAJEUR ou AMBIGU -> NON CONFORME
        - sinon -> CONFORME
        """
        if self.blocking_count or self.major_count or self.ambiguous_count:
            return "NON CONFORME"
        return "CONFORME"