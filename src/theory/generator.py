"""
Element property generator - orchestrates theory functions and confidence scoring.

This module implements the ElementGenerator class which:
1. Calls pure theory functions (Layer 0) to compute properties
2. Calls ConfidenceScorer to assess reliability
3. Returns Element objects with properties + confidence scores

The generator is the bridge between physics (theory functions) and
data structures (Element objects).
"""

from typing import Optional, Dict
from pathlib import Path
import json

from src.theory.quantum import madelung_rule, count_valence, orbital_type
from src.theory.confidence import ConfidenceScorer
from src.core.element import Element, ElementStatus


# IUPAC systematic naming for Z>118
# Format: 0=nil, 1=un, 2=bi, 3=tri, 4=quad, 5=pent, 6=hex, 7=sept, 8=oct, 9=enn
IUPAC_DIGIT_NAMES = {
    '0': 'nil', '1': 'un', '2': 'bi', '3': 'tri', '4': 'quad',
    '5': 'pent', '6': 'hex', '7': 'sept', '8': 'oct', '9': 'enn'
}


def _iupac_systematic_name(Z: int) -> tuple[str, str]:
    """
    Generate IUPAC systematic name and symbol for element Z.

    For Z>118, IUPAC uses systematic names based on digits:
    - 119 = ununennium (Uue): 1-1-9 → un-un-enn-ium
    - 120 = unbinilium (Ubn): 1-2-0 → un-bi-nil-ium

    Args:
        Z: Atomic number

    Returns:
        Tuple of (symbol, name)

    References:
        IUPAC (2016). Naming of New Elements. Pure Appl. Chem. 88, 401

    Examples:
        >>> _iupac_systematic_name(119)
        ('Uue', 'Ununennium')
        >>> _iupac_systematic_name(120)
        ('Ubn', 'Unbinilium')
    """
    digits = str(Z)

    # Build name from digits
    parts = [IUPAC_DIGIT_NAMES[d] for d in digits]
    name = ''.join(parts) + 'ium'

    # Build symbol: first letter of each digit name, capitalized first
    symbol_parts = [IUPAC_DIGIT_NAMES[d][0] for d in digits]
    symbol = symbol_parts[0].upper() + ''.join(symbol_parts[1:])

    # Capitalize first letter of name
    name = name.capitalize()

    return (symbol, name)


class ElementGenerator:
    """
    Generates element properties from first principles with confidence scoring.

    This class orchestrates:
    - Theory functions (quantum.py, nuclear.py, qed.py)
    - Confidence assessment (confidence.py)
    - Data structure creation (Element objects)

    The generator supports multiple theoretical models (Pyykkö, Fricke, etc.)
    for superheavy element predictions (Z>118).

    Usage:
        >>> gen = ElementGenerator(model='pyykkö_2011', confidence_profile='default')
        >>> carbon = gen.generate(6)
        >>> print(carbon.electron_configuration)
        '[He] 2s2 2p2'
        >>> print(carbon.confidence['electron_configuration'])
        1.0

        >>> element_120 = gen.generate(120)
        >>> print(element_120.electron_configuration)
        '[Og] 8s2'
        >>> print(element_120.confidence['electron_configuration'])
        0.85
    """

    def __init__(
        self,
        model: str = "pyykkö_2011",
        confidence_profile: str = "default"
    ):
        """
        Initialize element generator with specified model and confidence profile.

        Args:
            model: Theoretical model for superheavy elements
                   ("pyykkö_2011", "fricke_1971", "nefedov_2006")
            confidence_profile: Confidence scoring profile
                               ("default", "conservative", "optimistic")
        """
        self.model = model
        self.confidence_scorer = ConfidenceScorer(profile=confidence_profile)

        # Load element names database
        project_root = Path(__file__).parent.parent.parent
        names_path = project_root / "data" / "experimental" / "element_names.json"
        self._element_names: Dict[int, Dict[str, str]] = {}

        if names_path.exists():
            with open(names_path, 'r') as f:
                names_data = json.load(f)
                # Convert string keys to integers
                self._element_names = {
                    int(z): data for z, data in names_data["elements"].items()
                }

    def _classify_element(self, Z: int) -> ElementStatus:
        """
        Classify element based on Z and current experimental status.

        Args:
            Z: Atomic number

        Returns:
            ElementStatus classification

        Physical basis:
            - Z ≤ 118: All have been synthesized and confirmed
            - Z = 119-120: Active synthesis attempts (2025-2028)
            - Z = 121-137: Theoretical predictions only
            - Z = 138-172: Supercritical (1s electron velocity → c)
            - Z ≥ 173: Spontaneous pair creation, not viable
        """
        if Z <= 118:
            return ElementStatus.OBSERVED
        elif Z <= 120:
            return ElementStatus.SYNTHESIS_PLANNED
        elif Z <= 137:
            return ElementStatus.PREDICTED
        elif Z <= 172:
            return ElementStatus.SUPERCRITICAL
        else:
            return ElementStatus.IMPOSSIBLE

    def generate(self, Z: int) -> Element:
        """
        Generate element with all computed properties and confidence scores.

        This is the main entry point for element generation. It:
        1. Validates Z is in valid range (1-200)
        2. Computes electron configuration
        3. Derives valence electrons and block
        4. Generates systematic name (if Z>118)
        5. Classifies element status
        6. Computes confidence scores
        7. Returns Element object

        Args:
            Z: Atomic number (1-200)

        Returns:
            Element object with properties and confidence scores

        Raises:
            ValueError: If Z is out of range

        Examples:
            >>> gen = ElementGenerator()
            >>> h = gen.generate(1)
            >>> h.symbol
            'H'
            >>> h.electron_configuration
            '1s1'
            >>> h.valence_electrons
            1

            >>> ubn = gen.generate(120)
            >>> ubn.symbol
            'Ubn'
            >>> ubn.name
            'Unbinilium'
            >>> ubn.status
            <ElementStatus.SYNTHESIS_PLANNED: 'synthesis_planned'>
        """
        if Z < 1 or Z > 200:
            raise ValueError(f"Atomic number must be between 1 and 200, got {Z}")

        # Compute electron configuration (Layer 0: Theory)
        config = madelung_rule(Z, use_noble_gas_core=True)
        valence = count_valence(config)
        block = orbital_type(config)

        # Determine symbol and name
        if Z <= 118:
            # Use standard names (would load from database in production)
            # For now, use IUPAC systematic naming as placeholder
            symbol, name = self._get_standard_name(Z)
        else:
            # Z > 118: Use IUPAC systematic naming
            symbol, name = _iupac_systematic_name(Z)

        # Classify element status
        status = self._classify_element(Z)

        # Compute confidence scores
        confidence = self.confidence_scorer.get_all_confidences(Z)

        # Create Element object
        element = Element(
            atomic_number=Z,
            symbol=symbol,
            name=name,
            electron_configuration=config,
            valence_electrons=valence,
            block=block,
            status=status,
            confidence=confidence
        )

        return element

    def _get_standard_name(self, Z: int) -> tuple[str, str]:
        """
        Get standard symbol and name for observed elements (Z≤118).

        Loads from element_names.json if available, otherwise falls back
        to IUPAC systematic naming.

        Args:
            Z: Atomic number (1-118)

        Returns:
            Tuple of (symbol, name)
        """
        if Z in self._element_names:
            data = self._element_names[Z]
            return (data["symbol"], data["name"])
        else:
            # Fallback to systematic naming if name not in database
            return _iupac_systematic_name(Z)

    def __repr__(self) -> str:
        return f"ElementGenerator(model='{self.model}', scorer={self.confidence_scorer})"
