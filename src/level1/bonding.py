"""
Bonding rules: Level 0 (Elements) → Level 1 (Bonds)

This module implements minimal physics-based rules for predicting bond formation
between two elements. It demonstrates the hierarchical LUT approach:
- Fast: O(1) property lookups from cached Element objects
- Explainable: Physics-based rules (octet, electronegativity)
- Confident: Propagates uncertainty from Level 0 properties

References:
- Pauling, L. (1960). The Nature of the Chemical Bond, 3rd ed.
- Petrucci et al. (2016). General Chemistry: Principles and Modern Applications
"""

from dataclasses import dataclass
from typing import Dict
from src.core.element import Element


@dataclass
class BondPrediction:
    """
    Prediction of bond formation between two elements.

    Attributes:
        can_bond: True if atoms can form a stable bond
        bond_type: Type of bond ("nonpolar_covalent", "polar_covalent", "ionic", "none")
        confidence: Overall prediction confidence (0.0 to 1.0)
        confidence_breakdown: Per-property confidence scores
        reasoning: Human-readable explanation of the prediction
    """
    can_bond: bool
    bond_type: str  # "nonpolar_covalent" | "polar_covalent" | "ionic" | "none"
    confidence: float  # Overall confidence (0.0 to 1.0)
    confidence_breakdown: Dict[str, float]  # Per-property confidence
    reasoning: str  # Human-readable explanation

    def is_reliable(self, threshold: float = 0.5) -> bool:
        """
        Check if prediction confidence exceeds threshold.

        Args:
            threshold: Minimum confidence required (default 0.5)

        Returns:
            True if confidence >= threshold

        Examples:
            >>> pred = BondPrediction(can_bond=True, ..., confidence=0.95)
            >>> pred.is_reliable()
            True
            >>> pred.is_reliable(threshold=0.99)
            False
        """
        return self.confidence >= threshold

    def __repr__(self) -> str:
        return (
            f"BondPrediction(can_bond={self.can_bond}, "
            f"type='{self.bond_type}', confidence={self.confidence:.2f})"
        )


class BondingRules:
    """
    Stateless bonding prediction using Level 0 element properties.

    This class implements composition rules: Level 0 → Level 1

    Algorithm:
    1. Check if both elements want to bond (not noble gases)
    2. Classify bond type based on electronegativity difference
    3. Check valence compatibility (octet rule)
    4. Propagate confidence from element properties

    Physical basis:
    - Octet rule: Atoms bond to achieve 8 valence electrons (or 2 for H/He)
    - Electronegativity difference determines bond character:
        - ΔEN < 0.5: Nonpolar covalent (equal sharing)
        - 0.5 ≤ ΔEN < 1.7: Polar covalent (unequal sharing)
        - ΔEN ≥ 1.7: Ionic (electron transfer)

    Limitations:
    - Does not predict bond order (single/double/triple)
    - Does not handle coordinate covalent bonds
    - Does not predict molecular geometry
    - Does not handle metallic bonding
    - Transition metals may deviate from octet rule

    Usage:
        >>> from src.theory.generator import ElementGenerator
        >>> gen = ElementGenerator()
        >>> c = gen.generate(6)  # Carbon
        >>> h = gen.generate(1)  # Hydrogen
        >>>
        >>> bond = BondingRules.can_bond(c, h)
        >>> print(bond.can_bond)
        True
        >>> print(bond.bond_type)
        'polar_covalent'
        >>> print(bond.confidence)
        0.95
    """

    @staticmethod
    def can_bond(elem_a: Element, elem_b: Element) -> BondPrediction:
        """
        Predict if two elements can form a stable bond.

        Algorithm:
        1. Check if both elements can bond (not noble gases)
        2. Calculate electronegativity difference
        3. Classify bond type (covalent vs ionic)
        4. Check valence compatibility (octet rule)
        5. Compute confidence (minimum of input confidences)

        Args:
            elem_a: First element (from ElementGenerator)
            elem_b: Second element (from ElementGenerator)

        Returns:
            BondPrediction with confidence score

        Examples:
            >>> gen = ElementGenerator()
            >>> c = gen.generate(6)  # Carbon
            >>> h = gen.generate(1)  # Hydrogen
            >>> bond = BondingRules.can_bond(c, h)
            >>> bond.can_bond
            True
            >>> bond.bond_type
            'polar_covalent'

            >>> he = gen.generate(2)  # Helium
            >>> ne = gen.generate(10)  # Neon
            >>> bond = BondingRules.can_bond(he, ne)
            >>> bond.can_bond
            False
            >>> bond.bond_type
            'none'
        """
        # Step 1: Check if noble gases (don't bond)
        if BondingRules.is_noble_gas(elem_a):
            return BondPrediction(
                can_bond=False,
                bond_type="none",
                confidence=1.0,  # High confidence in "no bond"
                confidence_breakdown={"valence": 1.0},
                reasoning=f"{elem_a.symbol} is a noble gas (full valence shell)"
            )

        if BondingRules.is_noble_gas(elem_b):
            return BondPrediction(
                can_bond=False,
                bond_type="none",
                confidence=1.0,
                confidence_breakdown={"valence": 1.0},
                reasoning=f"{elem_b.symbol} is a noble gas (full valence shell)"
            )

        # Step 2: Check if electronegativity is available
        if elem_a.electronegativity is None or elem_b.electronegativity is None:
            # Cannot predict without electronegativity
            return BondPrediction(
                can_bond=None,  # Unknown
                bond_type="unknown",
                confidence=0.0,
                confidence_breakdown={},
                reasoning="Electronegativity data unavailable"
            )

        # Step 3: Classify bond type
        bond_type = BondingRules.classify_bond_type(elem_a, elem_b)
        delta_en = abs(elem_a.electronegativity - elem_b.electronegativity)

        # Step 4: Check valence compatibility
        can_form_bond = BondingRules.satisfies_octet(elem_a, elem_b)

        # Step 5: Compute confidence (minimum rule)
        confidence, breakdown = BondingRules._compute_confidence(elem_a, elem_b)

        # Step 6: Generate reasoning
        reasoning = (
            f"ΔEN={delta_en:.2f} → {bond_type}, "
            f"valence: {elem_a.symbol}({elem_a.valence_electrons}) + "
            f"{elem_b.symbol}({elem_b.valence_electrons})"
        )

        return BondPrediction(
            can_bond=can_form_bond,
            bond_type=bond_type,
            confidence=confidence,
            confidence_breakdown=breakdown,
            reasoning=reasoning
        )

    @staticmethod
    def is_noble_gas(elem: Element) -> bool:
        """
        Check if element is a noble gas (full valence shell).

        Noble gases have complete valence shells:
        - He: 2 electrons (1s²)
        - Ne, Ar, Kr, Xe, Rn, Og: 8 electrons (ns² np⁶)

        These elements are chemically inert and rarely form bonds.

        Args:
            elem: Element to check

        Returns:
            True if element is a noble gas

        Examples:
            >>> gen = ElementGenerator()
            >>> he = gen.generate(2)
            >>> BondingRules.is_noble_gas(he)
            True
            >>> c = gen.generate(6)
            >>> BondingRules.is_noble_gas(c)
            False
        """
        # Noble gases: 2 valence (He) or 8 valence (others)
        return (elem.valence_electrons == 2 and elem.atomic_number <= 2) or \
               (elem.valence_electrons == 8)

    @staticmethod
    def classify_bond_type(elem_a: Element, elem_b: Element) -> str:
        """
        Classify bond type based on electronegativity difference.

        Uses Pauling scale thresholds:
        - ΔEN < 0.5: Nonpolar covalent (equal electron sharing)
        - 0.5 ≤ ΔEN < 1.7: Polar covalent (unequal sharing)
        - ΔEN ≥ 1.7: Ionic (electron transfer)

        Args:
            elem_a: First element
            elem_b: Second element

        Returns:
            Bond type: "nonpolar_covalent", "polar_covalent", or "ionic"

        Physical note:
            Thresholds are approximate. Real bonds exist on a continuum
            from purely covalent to purely ionic.

        References:
            Pauling, L. (1960). The Nature of the Chemical Bond, 3rd ed.

        Examples:
            >>> # C-C bond
            >>> c = gen.generate(6)
            >>> BondingRules.classify_bond_type(c, c)
            'nonpolar_covalent'

            >>> # C-O bond
            >>> o = gen.generate(8)
            >>> BondingRules.classify_bond_type(c, o)
            'polar_covalent'

            >>> # Na-Cl bond
            >>> na = gen.generate(11)
            >>> cl = gen.generate(17)
            >>> BondingRules.classify_bond_type(na, cl)
            'ionic'
        """
        delta_en = abs(elem_a.electronegativity - elem_b.electronegativity)

        if delta_en < 0.5:
            return "nonpolar_covalent"
        elif delta_en < 1.7:
            return "polar_covalent"
        else:
            return "ionic"

    @staticmethod
    def satisfies_octet(elem_a: Element, elem_b: Element) -> bool:
        """
        Check if bonding can satisfy octet rule for both atoms.

        Octet rule: Atoms bond to achieve 8 valence electrons (or 2 for H/He).
        This is satisfied if both atoms have "room" in their valence shells.

        Args:
            elem_a: First element
            elem_b: Second element

        Returns:
            True if both atoms can fill their valence shells by bonding

        Physical note:
            This is a simplified check. Real molecules may violate the octet
            rule (e.g., SF₆ has 12 electrons around S).

        Examples:
            >>> # H + H → H₂ (both achieve 2 electrons)
            >>> h = gen.generate(1)
            >>> BondingRules.satisfies_octet(h, h)
            True

            >>> # C + O → CO (both can share electrons)
            >>> c = gen.generate(6)
            >>> o = gen.generate(8)
            >>> BondingRules.satisfies_octet(c, o)
            True

            >>> # He + He (both already full)
            >>> he = gen.generate(2)
            >>> BondingRules.satisfies_octet(he, he)
            False
        """
        # Determine target electrons (2 for H/He, 8 for others)
        target_a = 2 if elem_a.atomic_number <= 2 else 8
        target_b = 2 if elem_b.atomic_number <= 2 else 8

        # How many electrons does each need?
        needs_a = target_a - elem_a.valence_electrons
        needs_b = target_b - elem_b.valence_electrons

        # Both atoms should have room (positive need)
        # If either is already satisfied (need ≤ 0), bonding unlikely
        return needs_a > 0 and needs_b > 0

    @staticmethod
    def _compute_confidence(elem_a: Element, elem_b: Element) -> tuple[float, Dict[str, float]]:
        """
        Compute bond prediction confidence using minimum rule.

        Confidence = min(confidence of all properties used)

        Properties used:
        - electron_configuration (for valence electron count)
        - electronegativity (for bond type classification)

        Args:
            elem_a: First element
            elem_b: Second element

        Returns:
            Tuple of (overall_confidence, confidence_breakdown)

        Physical note:
            The minimum rule is conservative: a bond prediction is only as
            reliable as the least reliable input property.

        Examples:
            >>> # Both elements well-known (Z≤118)
            >>> c = gen.generate(6)  # confidence ~1.0
            >>> h = gen.generate(1)  # confidence ~1.0
            >>> conf, breakdown = BondingRules._compute_confidence(c, h)
            >>> conf
            1.0

            >>> # One element theoretical (Z>118)
            >>> elem_120 = gen.generate(120)  # confidence ~0.85
            >>> conf, breakdown = BondingRules._compute_confidence(c, elem_120)
            >>> conf
            0.85
        """
        properties_used = ["electron_configuration", "electronegativity"]

        breakdown = {}
        for prop in properties_used:
            conf_a = elem_a.confidence.get(prop, 0.0)
            conf_b = elem_b.confidence.get(prop, 0.0)
            # For each property, take minimum of (A, B)
            breakdown[prop] = min(conf_a, conf_b)

        # Overall confidence is minimum across all properties
        overall = min(breakdown.values())

        return overall, breakdown
