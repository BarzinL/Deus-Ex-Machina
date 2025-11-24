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
        bond_order: Bond order (1=single, 2=double, 3=triple)
        stability_score: Estimated stability (0.0 to 1.0, higher = more stable)
        confidence: Overall prediction confidence (0.0 to 1.0)
        confidence_breakdown: Per-property confidence scores
        reasoning: Human-readable explanation of the prediction
    """
    can_bond: bool
    bond_type: str  # "nonpolar_covalent" | "polar_covalent" | "ionic" | "none"
    bond_order: int  # 1 (single), 2 (double), 3 (triple)
    stability_score: float  # 0.0 to 1.0, higher = more stable
    confidence: float  # Overall prediction confidence (0.0 to 1.0)
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
        bond_symbols = {1: "-", 2: "=", 3: "≡"}
        return (
            f"BondPrediction(can_bond={self.can_bond}, "
            f"order={self.bond_order}{bond_symbols.get(self.bond_order, '')}, "
            f"type='{self.bond_type}', "
            f"stability={self.stability_score:.2f}, "
            f"confidence={self.confidence:.2f})"
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
                bond_order=0,
                stability_score=1.0,  # Noble gas is "stable" as-is
                confidence=1.0,
                confidence_breakdown={"valence": 1.0},
                reasoning=f"{elem_a.symbol} is a noble gas (full valence shell)"
            )

        if BondingRules.is_noble_gas(elem_b):
            return BondPrediction(
                can_bond=False,
                bond_type="none",
                bond_order=0,
                stability_score=1.0,
                confidence=1.0,
                confidence_breakdown={"valence": 1.0},
                reasoning=f"{elem_b.symbol} is a noble gas (full valence shell)"
            )

        # Step 2: Check if electronegativity is available
        if elem_a.electronegativity is None or elem_b.electronegativity is None:
            # Cannot predict without electronegativity
            return BondPrediction(
                can_bond=None,
                bond_type="unknown",
                bond_order=0,
                stability_score=0.0,
                confidence=0.0,
                confidence_breakdown={},
                reasoning="Electronegativity data unavailable"
            )

        # Step 3: Determine most likely bond order
        bond_order = BondingRules.predict_bond_order(elem_a, elem_b)

        # Step 4: Classify bond type
        bond_type = BondingRules.classify_bond_type(elem_a, elem_b)
        delta_en = abs(elem_a.electronegativity - elem_b.electronegativity)

        # Step 5: Check valence compatibility
        can_form_bond = BondingRules.satisfies_octet(elem_a, elem_b)

        # Step 6: Compute stability score
        stability_score = BondingRules.compute_stability_score(
            elem_a, elem_b, bond_order, bond_type
        )

        # Step 7: Compute confidence (minimum rule)
        confidence, breakdown = BondingRules._compute_confidence(elem_a, elem_b)

        # Step 8: Generate reasoning
        bond_symbols = {1: "-", 2: "=", 3: "≡"}
        reasoning = (
            f"{elem_a.symbol}{bond_symbols.get(bond_order, '?')}{elem_b.symbol}: "
            f"ΔEN={delta_en:.2f} → {bond_type}, "
            f"valence: {elem_a.symbol}({elem_a.valence_electrons}) "
            f"{elem_b.symbol}({elem_b.valence_electrons})"
        )

        return BondPrediction(
            can_bond=can_form_bond,
            bond_type=bond_type,
            bond_order=bond_order,
            stability_score=stability_score,
            confidence=confidence,
            confidence_breakdown=breakdown,
            reasoning=reasoning
        )

    @staticmethod
    def predict_all_bond_orders(elem_a: Element, elem_b: Element) -> list[BondPrediction]:
        """
        Generate ALL possible bond orders for two elements (systematic enumeration).

        This is the method to use for building the comprehensive cache.
        It generates all valence-valid bond orders and computes properties for each.

        Args:
            elem_a: First element
            elem_b: Second element

        Returns:
            List of BondPrediction objects, one for each valid bond order

        Physical basis:
            - Single bond (order=1): Share 1 electron pair (σ bond)
            - Double bond (order=2): Share 2 electron pairs (σ + π)
            - Triple bond (order=3): Share 3 electron pairs (σ + 2π)

        Examples:
            >>> gen = ElementGenerator()
            >>> c = gen.generate(6)
            >>> bonds = BondingRules.predict_all_bond_orders(c, c)
            >>> len(bonds)  # C-C, C=C, C≡C
            3
            >>> [b.bond_order for b in bonds]
            [1, 2, 3]
        """
        predictions = []

        # Check for noble gases
        if BondingRules.is_noble_gas(elem_a) or BondingRules.is_noble_gas(elem_b):
            # Noble gases don't bond - return single "no bond" prediction
            return [BondingRules.can_bond(elem_a, elem_b)]

        # Check for electronegativity availability
        if elem_a.electronegativity is None or elem_b.electronegativity is None:
            # Can't predict - return single "unknown" prediction
            return [BondingRules.can_bond(elem_a, elem_b)]

        # Determine maximum possible bond order based on valence
        max_order = min(elem_a.valence_electrons, elem_b.valence_electrons, 3)

        # Special cases: Some atoms can't form multiple bonds
        # H can only form single bonds (no p orbitals for π bonding)
        if elem_a.atomic_number == 1 or elem_b.atomic_number == 1:
            max_order = 1

        # O-O triple bonds don't occur (oxygen prefers having lone pairs)
        if elem_a.atomic_number == 8 and elem_b.atomic_number == 8:
            max_order = min(max_order, 2)

        # Generate predictions for all valid bond orders
        bond_type = BondingRules.classify_bond_type(elem_a, elem_b)
        delta_en = abs(elem_a.electronegativity - elem_b.electronegativity)
        confidence, breakdown = BondingRules._compute_confidence(elem_a, elem_b)

        for bond_order in range(1, max_order + 1):
            # Check if this bond order satisfies valence requirements
            can_form_bond = BondingRules.satisfies_octet_with_order(
                elem_a, elem_b, bond_order
            )

            # Compute stability score for this specific bond order
            stability_score = BondingRules.compute_stability_score(
                elem_a, elem_b, bond_order, bond_type
            )

            # Generate reasoning
            bond_symbols = {1: "-", 2: "=", 3: "≡"}
            reasoning = (
                f"{elem_a.symbol}{bond_symbols.get(bond_order, '?')}{elem_b.symbol}: "
                f"ΔEN={delta_en:.2f} → {bond_type}, "
                f"order={bond_order}, stability={stability_score:.2f}"
            )

            predictions.append(BondPrediction(
                can_bond=can_form_bond,
                bond_type=bond_type,
                bond_order=bond_order,
                stability_score=stability_score,
                confidence=confidence,
                confidence_breakdown=breakdown,
                reasoning=reasoning
            ))

        return predictions

    @staticmethod
    def predict_bond_order(elem_a: Element, elem_b: Element) -> int:
        """
        Predict the MOST LIKELY bond order for two elements.

        This is a simplified method that returns a single bond order.
        For comprehensive enumeration, use predict_all_bond_orders().

        Physical basis:
            - Atoms prefer bond orders that minimize formal charge
            - Common patterns: C-C single, C=C double, C≡C triple, C=O double, etc.

        Args:
            elem_a: First element
            elem_b: Second element

        Returns:
            Most likely bond order (1, 2, or 3)

        Examples:
            >>> gen = ElementGenerator()
            >>> c = gen.generate(6)
            >>> h = gen.generate(1)
            >>> BondingRules.predict_bond_order(c, h)
            1  # C-H single bond
            >>> o = gen.generate(8)
            >>> BondingRules.predict_bond_order(c, o)
            2  # C=O double bond (carbonyl) is most common
        """
        # Default to single bond
        default_order = 1

        # H can only form single bonds
        if elem_a.atomic_number == 1 or elem_b.atomic_number == 1:
            return 1

        # Get all possible bond orders and return the most stable one
        all_bonds = BondingRules.predict_all_bond_orders(elem_a, elem_b)
        if not all_bonds:
            return default_order

        # Return bond order with highest stability score
        most_stable = max(all_bonds, key=lambda b: b.stability_score)
        return most_stable.bond_order

    @staticmethod
    def compute_stability_score(
        elem_a: Element,
        elem_b: Element,
        bond_order: int,
        bond_type: str
    ) -> float:
        """
        Compute stability score for a specific bond configuration.

        Score ranges from 0.0 (very unstable) to 1.0 (very stable).

        Physical basis:
            - Typical bond orders for element pairs get higher scores
            - Unusual bond orders (e.g., C≡O) get lower scores
            - Ionic bonds prefer single bonds
            - Covalent bonds can be single, double, or triple

        Args:
            elem_a: First element
            elem_b: Second element
            bond_order: Bond order (1, 2, or 3)
            bond_type: Bond type ("nonpolar_covalent", "polar_covalent", "ionic")

        Returns:
            Stability score (0.0 to 1.0)

        Examples:
            >>> # C-C single bond: stable
            >>> score = BondingRules.compute_stability_score(C, C, 1, "nonpolar_covalent")
            >>> score > 0.85
            True
            >>> # C=O double bond: very stable (carbonyl)
            >>> score = BondingRules.compute_stability_score(C, O, 2, "polar_covalent")
            >>> score > 0.90
            True
        """
        # Base stability by bond type
        base_stability = {
            "nonpolar_covalent": 0.85,
            "polar_covalent": 0.85,
            "ionic": 0.80,
            "none": 0.0,
            "unknown": 0.0
        }.get(bond_type, 0.5)

        # Ionic bonds strongly prefer single bonds
        if bond_type == "ionic":
            if bond_order == 1:
                return 0.90
            else:
                return 0.20  # Double/triple ionic bonds are rare

        # Element-specific bond order preferences
        # These are empirical patterns from chemistry

        # C-C bonds: all orders are stable, single slightly preferred
        if elem_a.atomic_number == 6 and elem_b.atomic_number == 6:
            return {1: 0.90, 2: 0.88, 3: 0.85}.get(bond_order, 0.5)

        # C-H bonds: only single bonds
        if {elem_a.atomic_number, elem_b.atomic_number} == {1, 6}:
            return 0.92 if bond_order == 1 else 0.10

        # C-O bonds: double bond preferred (carbonyl)
        if {elem_a.atomic_number, elem_b.atomic_number} == {6, 8}:
            return {1: 0.85, 2: 0.95, 3: 0.20}.get(bond_order, 0.5)

        # C-N bonds: all orders reasonably stable
        if {elem_a.atomic_number, elem_b.atomic_number} == {6, 7}:
            return {1: 0.88, 2: 0.86, 3: 0.82}.get(bond_order, 0.5)

        # N-N bonds: triple bond preferred (N₂)
        if elem_a.atomic_number == 7 and elem_b.atomic_number == 7:
            return {1: 0.70, 2: 0.80, 3: 0.95}.get(bond_order, 0.5)

        # O-O bonds: double bond (O₂) very stable, single (peroxide) also stable
        if elem_a.atomic_number == 8 and elem_b.atomic_number == 8:
            return {1: 0.82, 2: 0.92, 3: 0.05}.get(bond_order, 0.5)

        # N-O bonds: double bond common
        if {elem_a.atomic_number, elem_b.atomic_number} == {7, 8}:
            return {1: 0.82, 2: 0.88, 3: 0.60}.get(bond_order, 0.5)

        # Default: single bonds slightly preferred, higher orders possible but less stable
        if bond_order == 1:
            return base_stability
        elif bond_order == 2:
            return base_stability * 0.90
        elif bond_order == 3:
            return base_stability * 0.75
        else:
            return 0.5

    @staticmethod
    def satisfies_octet_with_order(
        elem_a: Element,
        elem_b: Element,
        bond_order: int
    ) -> bool:
        """
        Check if bonding with specific bond order can satisfy octet rule.

        Args:
            elem_a: First element
            elem_b: Second element
            bond_order: Bond order (1, 2, or 3)

        Returns:
            True if both atoms can achieve stable valence with this bond order

        Physical note:
            Higher bond orders mean more electrons shared.
            This affects how many electrons each atom needs.

        Examples:
            >>> # C + O with double bond → C=O (both achieve octet)
            >>> BondingRules.satisfies_octet_with_order(C, O, 2)
            True
            >>> # H + H with single bond → H₂ (both achieve 2 electrons)
            >>> BondingRules.satisfies_octet_with_order(H, H, 1)
            True
        """
        # Determine target electrons (2 for H/He, 8 for others)
        target_a = 2 if elem_a.atomic_number <= 2 else 8
        target_b = 2 if elem_b.atomic_number <= 2 else 8

        # Electrons needed before bonding
        needs_a = target_a - elem_a.valence_electrons
        needs_b = target_b - elem_b.valence_electrons

        # After forming bond of given order:
        # Each atom gains 'bond_order' electrons from sharing
        after_bond_a = elem_a.valence_electrons + bond_order
        after_bond_b = elem_b.valence_electrons + bond_order

        # Check if both atoms reach their targets (or get closer)
        # Allow some flexibility: atoms might not reach exact octet
        return (needs_a > 0 and needs_b > 0 and
                after_bond_a <= target_a + 2 and
                after_bond_b <= target_b + 2)

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
