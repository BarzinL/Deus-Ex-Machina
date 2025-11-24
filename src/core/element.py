"""
Element data structure with properties and confidence scores.
"""

from dataclasses import dataclass
from typing import Optional, Dict
from enum import Enum


class ElementStatus(Enum):
    """
    Classification of element based on experimental observation and theoretical viability.
    """
    OBSERVED = "observed"  # Z=1-118, experimentally confirmed
    SYNTHESIS_PLANNED = "synthesis_planned"  # Z=119-120, active attempts
    PREDICTED = "predicted"  # Z=121-137, theoretical predictions
    SUPERCRITICAL = "supercritical"  # Z=138-172, QED unstable
    IMPOSSIBLE = "impossible"  # Z≥173, spontaneous pair creation


@dataclass
class Element:
    """
    Element with computed properties and confidence scores.

    This dataclass stores both the computed property values (from theory)
    and their associated confidence scores (from ConfidenceScorer).

    Attributes:
        atomic_number: Nuclear proton count (Z)
        symbol: Chemical symbol (e.g., "C", "Au", "Ubn")
        name: Element name (e.g., "Carbon", "Gold", "Unbinilium")
        electron_configuration: Ground-state electron config (e.g., "[He] 2s2 2p2")
        valence_electrons: Number of valence electrons
        block: Periodic table block ('s', 'p', 'd', 'f', or 'g')
        status: Observation/prediction status
        confidence: Dict mapping property names to confidence scores (0.0-1.0)
    """

    # Core identification
    atomic_number: int
    symbol: str
    name: str

    # Electronic structure
    electron_configuration: str
    valence_electrons: int
    block: str  # 's', 'p', 'd', 'f', 'g'

    # Classification
    status: ElementStatus

    # Confidence scores for each property
    confidence: Dict[str, float]

    # Chemical properties (Phase 2.5+)
    electronegativity: Optional[float] = None  # Pauling scale

    # Optional properties (to be added in future phases)
    group: Optional[int] = None
    period: Optional[int] = None
    atomic_radius: Optional[float] = None
    ionization_energy: Optional[float] = None
    oxidation_states: Optional[list] = None
    half_life: Optional[float] = None
    most_stable_isotope: Optional[int] = None

    def __repr__(self) -> str:
        return (
            f"Element(Z={self.atomic_number}, symbol='{self.symbol}', "
            f"config='{self.electron_configuration}', status={self.status.value})"
        )

    def __str__(self) -> str:
        return f"{self.name} ({self.symbol}, Z={self.atomic_number})"
