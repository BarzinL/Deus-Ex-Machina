"""
CrystallizationDetector: Measures when compositional boundaries should form.

The core insight: When the "naive additive" prediction breaks down significantly,
that signals a compositional boundary - the system should be cached as a unit
rather than decomposed.

This detector is domain-agnostic. It works on any system where:
1. You have a substrate representation (atoms, quarks, components, etc.)
2. You can define a naive composition function (sum bond energies, etc.)
3. You have actual ground truth (experiment, expensive calculation, etc.)
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any, Callable
import math


@dataclass
class AdditivityViolation:
    """
    Result of measuring how much actual properties deviate from naive composition.

    Attributes:
        naive_value: Predicted value from naive composition (e.g., sum of bond energies)
        actual_value: Ground truth value (experiment or expensive calculation)
        violation: Absolute difference (actual - naive)
        relative_violation: Violation as fraction of actual value
        confidence: Uncertainty in the measurement (0.0 to 1.0)
        classification: Type of violation ("decomposes_cleanly", "must_cache", "uncertain")
        structural_features: Features extracted from the structure
        reasoning: Human-readable explanation
    """
    naive_value: float
    actual_value: float
    violation: float  # actual - naive
    relative_violation: float  # violation / abs(actual)
    confidence: float  # 0.0 to 1.0
    classification: str  # "decomposes_cleanly" | "must_cache" | "uncertain"
    structural_features: Dict[str, Any]
    reasoning: str

    def is_significant(self, threshold: float = 0.05) -> bool:
        """
        Check if violation is large enough to matter.

        Args:
            threshold: Relative violation threshold (default 5%)

        Returns:
            True if violation exceeds threshold
        """
        return abs(self.relative_violation) > threshold

    def __repr__(self) -> str:
        return (
            f"AdditivityViolation(violation={self.violation:.1f}, "
            f"relative={self.relative_violation:.1%}, "
            f"classification='{self.classification}')"
        )


@dataclass
class StructuralFeatures:
    """
    Graph-theoretic and topological features of a structure.

    These features help predict where additivity breaks down.

    Attributes:
        num_nodes: Number of nodes (atoms, particles, components)
        num_edges: Number of edges (bonds, interactions)
        num_cycles: Number of cycles in the graph
        max_cycle_size: Size of largest cycle
        symmetry_order: Order of symmetry group (1 = no symmetry)
        planarity: Whether graph is planar (True/False)
        conjugation: Degree of conjugation/delocalization (0.0 to 1.0)
        density: Edge density = edges / max_possible_edges
        clustering: Average clustering coefficient
        custom: Domain-specific features (dict)
    """
    num_nodes: int
    num_edges: int
    num_cycles: int
    max_cycle_size: int
    symmetry_order: int
    planarity: bool
    conjugation: float  # 0.0 to 1.0
    density: float
    clustering: float
    custom: Dict[str, Any]

    def has_resonance(self) -> bool:
        """Check if structure likely has resonance/delocalization."""
        return self.conjugation > 0.5 or (self.num_cycles > 0 and self.max_cycle_size >= 5)

    def is_symmetric(self) -> bool:
        """Check if structure has significant symmetry."""
        return self.symmetry_order > 1

    def __repr__(self) -> str:
        return (
            f"StructuralFeatures(nodes={self.num_nodes}, edges={self.num_edges}, "
            f"cycles={self.num_cycles}, symmetry={self.symmetry_order})"
        )


class CrystallizationDetector:
    """
    Detects when compositional boundaries should form by measuring additivity violations.

    The detector compares "naive composition" (additive prediction from lower level)
    against actual ground truth. Large violations signal that the system should be
    cached as a unit rather than decomposed.

    Usage:
        >>> detector = CrystallizationDetector()
        >>>
        >>> # Define naive composition function (e.g., sum bond energies)
        >>> def naive_fn(structure):
        ...     return sum(bond.energy for bond in structure.bonds)
        >>>
        >>> # Actual value from experiment or expensive calculation
        >>> actual_energy = -1234.5  # kJ/mol from experiment
        >>>
        >>> # Measure violation
        >>> violation = detector.measure_additivity_violation(
        ...     structure=benzene,
        ...     naive_fn=naive_fn,
        ...     actual_value=actual_energy
        ... )
        >>>
        >>> if violation.is_significant():
        ...     print(f"Cache this! Violation: {violation.relative_violation:.1%}")
    """

    def __init__(self, violation_threshold: float = 0.05):
        """
        Initialize detector.

        Args:
            violation_threshold: Relative violation threshold for "must_cache"
                                (default 5%)
        """
        self.violation_threshold = violation_threshold

    def measure_additivity_violation(
        self,
        structure: Any,
        naive_fn: Callable[[Any], float],
        actual_value: float,
        confidence: float = 1.0
    ) -> AdditivityViolation:
        """
        Measure how much actual properties deviate from naive additive prediction.

        This is the core measurement. Large violations indicate compositional boundaries.

        Args:
            structure: The structure to analyze (domain-specific representation)
            naive_fn: Function that computes naive additive value from structure
            actual_value: Ground truth value (experiment or expensive calculation)
            confidence: Uncertainty in actual_value (0.0 to 1.0)

        Returns:
            AdditivityViolation object with measurement results

        Physical interpretation:
            - violation > 0: System is MORE stable than naive prediction (benzene)
            - violation < 0: System is LESS stable than naive prediction (strained rings)
            - violation ≈ 0: Additivity works fine, decomposition is valid

        Examples:
            >>> # Benzene: aromatic stabilization
            >>> violation = detector.measure_additivity_violation(
            ...     structure=benzene,
            ...     naive_fn=sum_bond_energies,
            ...     actual_value=-5536  # kJ/mol from experiment
            ... )
            >>> violation.violation
            -150.0  # ~150 kJ/mol stabilization (resonance energy)

            >>> # Cyclopropane: ring strain
            >>> violation = detector.measure_additivity_violation(
            ...     structure=cyclopropane,
            ...     naive_fn=sum_bond_energies,
            ...     actual_value=-2091  # kJ/mol
            ... )
            >>> violation.violation
            +115.0  # ~115 kJ/mol destabilization (angle strain)
        """
        # Compute naive additive prediction
        naive_value = naive_fn(structure)

        # Compute violation
        violation = actual_value - naive_value
        relative_violation = violation / abs(actual_value) if actual_value != 0 else 0.0

        # Extract structural features
        features = self.extract_structural_features(structure)

        # Classify the violation
        classification = self.classify_violation(
            violation=violation,
            relative_violation=relative_violation,
            features=features
        )

        # Generate reasoning
        reasoning = self._generate_reasoning(
            violation=violation,
            relative_violation=relative_violation,
            classification=classification,
            features=features
        )

        return AdditivityViolation(
            naive_value=naive_value,
            actual_value=actual_value,
            violation=violation,
            relative_violation=relative_violation,
            confidence=confidence,
            classification=classification,
            structural_features=features.__dict__,
            reasoning=reasoning
        )

    def extract_structural_features(self, structure: Any) -> StructuralFeatures:
        """
        Extract graph-theoretic and topological features from structure.

        These features help predict where additivity will break down.

        Args:
            structure: The structure to analyze

        Returns:
            StructuralFeatures object

        Notes:
            - Override this method for domain-specific feature extraction
            - Default implementation works for molecular graphs
        """
        # Extract basic graph properties
        # Structure is expected to have: atoms (list), bonds (list of tuples)

        if hasattr(structure, 'atoms') and hasattr(structure, 'bonds'):
            num_nodes = len(structure.atoms)
            num_edges = len(structure.bonds)

            # Detect cycles using simple depth-first search
            num_cycles, max_cycle_size = self._detect_cycles(structure)

            # Estimate symmetry order (simple heuristic for now)
            symmetry_order = self._estimate_symmetry(structure)

            # Check planarity (heuristic: cycles > 0 and small)
            planarity = (num_cycles == 0) or (max_cycle_size <= 6)

            # Estimate conjugation (alternating double bonds in cycles)
            conjugation = self._estimate_conjugation(structure)

            # Compute graph density
            max_edges = num_nodes * (num_nodes - 1) / 2 if num_nodes > 1 else 1
            density = num_edges / max_edges if max_edges > 0 else 0.0

            # Clustering coefficient (simplified)
            clustering = self._compute_clustering(structure)

            return StructuralFeatures(
                num_nodes=num_nodes,
                num_edges=num_edges,
                num_cycles=num_cycles,
                max_cycle_size=max_cycle_size,
                symmetry_order=symmetry_order,
                planarity=planarity,
                conjugation=conjugation,
                density=density,
                clustering=clustering,
                custom={}
            )
        else:
            # Generic structure without atoms/bonds - return default features
            return StructuralFeatures(
                num_nodes=0,
                num_edges=0,
                num_cycles=0,
                max_cycle_size=0,
                symmetry_order=1,
                planarity=True,
                conjugation=0.0,
                density=0.0,
                clustering=0.0,
                custom={}
            )

    def classify_violation(
        self,
        violation: float,
        relative_violation: float,
        features: StructuralFeatures
    ) -> str:
        """
        Classify the violation: should this be cached as a unit or decomposed?

        Args:
            violation: Absolute violation (actual - naive)
            relative_violation: Relative violation (violation / actual)
            features: Structural features

        Returns:
            Classification: "decomposes_cleanly" | "must_cache" | "uncertain"

        Decision logic:
            - Small violation + no special structure → "decomposes_cleanly"
            - Large violation + resonance/symmetry → "must_cache"
            - Borderline cases → "uncertain"
        """
        abs_relative = abs(relative_violation)

        # Large violation → must cache
        if abs_relative > self.violation_threshold * 2:  # 10% threshold
            return "must_cache"

        # Small violation + simple structure → decomposes cleanly
        if abs_relative < self.violation_threshold:  # 5% threshold
            if not features.has_resonance() and not features.is_symmetric():
                return "decomposes_cleanly"

        # Moderate violation + special structure → must cache
        if abs_relative > self.violation_threshold:
            if features.has_resonance() or features.is_symmetric():
                return "must_cache"

        # Borderline → uncertain
        return "uncertain"

    def _generate_reasoning(
        self,
        violation: float,
        relative_violation: float,
        classification: str,
        features: StructuralFeatures
    ) -> str:
        """Generate human-readable explanation of the violation."""
        abs_rel = abs(relative_violation)

        direction = "stabilization" if violation < 0 else "destabilization"
        magnitude = "large" if abs_rel > 0.10 else "moderate" if abs_rel > 0.05 else "small"

        reasoning_parts = [
            f"{magnitude.capitalize()} {direction} ({abs_rel:.1%})",
        ]

        if features.has_resonance():
            reasoning_parts.append("resonance/delocalization detected")

        if features.is_symmetric():
            reasoning_parts.append(f"symmetry order {features.symmetry_order}")

        if features.num_cycles > 0:
            reasoning_parts.append(f"{features.num_cycles} cycle(s)")

        reasoning_parts.append(f"→ {classification}")

        return ", ".join(reasoning_parts)

    def _detect_cycles(self, structure: Any) -> Tuple[int, int]:
        """
        Detect cycles in the graph structure.

        Returns:
            (num_cycles, max_cycle_size)
        """
        # Simplified cycle detection
        # For now, just count if there are more edges than nodes-1 (tree condition)
        num_nodes = len(structure.atoms)
        num_edges = len(structure.bonds)

        # Tree has n-1 edges, cycles add extra edges
        if num_edges >= num_nodes:
            # Heuristic: number of "extra" edges estimates cycle count
            num_cycles = num_edges - num_nodes + 1

            # Heuristic for max cycle size based on graph size
            max_cycle_size = min(num_nodes, 6)  # Assume typical rings are size 3-6

            return (num_cycles, max_cycle_size)
        else:
            return (0, 0)

    def _estimate_symmetry(self, structure: Any) -> int:
        """
        Estimate symmetry order (number of symmetry operations).

        Returns:
            Symmetry order (1 = no symmetry)
        """
        # Simplified heuristic based on structure size and regularity
        num_nodes = len(structure.atoms)
        num_edges = len(structure.bonds)

        # Perfect regularity heuristic: if all atoms have same degree
        if num_nodes > 0 and num_edges > 0:
            # Count degree of each atom
            degrees = [0] * num_nodes
            for i, j, _ in structure.bonds:
                degrees[i] += 1
                degrees[j] += 1

            # If all degrees are equal, structure might be symmetric
            if len(set(degrees)) == 1:
                # Benzene-like: 6 atoms, order 6 symmetry
                if num_nodes == 6 and degrees[0] == 2:
                    return 6
                # Triangle: 3 atoms, order 3
                if num_nodes == 3 and degrees[0] == 2:
                    return 3
                # Other regular structures
                return num_nodes

        return 1  # No symmetry detected

    def _estimate_conjugation(self, structure: Any) -> float:
        """
        Estimate degree of conjugation/delocalization.

        Returns:
            Conjugation score (0.0 to 1.0)
        """
        # Heuristic: alternating single/double bonds in cycles suggests conjugation
        # Also: fractional bond orders (like 1.5 in benzene) indicate delocalization
        if not hasattr(structure, 'bonds'):
            return 0.0

        # Count double bonds and aromatic bonds (fractional order)
        double_bonds = 0
        aromatic_bonds = 0
        for _, _, order in structure.bonds:
            if order == 2:
                double_bonds += 1
            elif 1 < order < 2:  # Fractional order (aromatic/delocalized)
                aromatic_bonds += 1

        total_bonds = len(structure.bonds)

        if total_bonds == 0:
            return 0.0

        # High ratio of double/aromatic bonds + cycles → high conjugation
        conjugated_bonds = double_bonds + aromatic_bonds
        conjugated_ratio = conjugated_bonds / total_bonds
        num_cycles, _ = self._detect_cycles(structure)

        # Aromatic bonds in cycles = strong conjugation signal
        if num_cycles > 0 and aromatic_bonds > 0:
            return min(1.0, 0.8 + conjugated_ratio * 0.2)  # High conjugation score
        elif num_cycles > 0 and conjugated_ratio > 0.3:
            return min(1.0, conjugated_ratio + 0.3)  # Boost if cycles present
        else:
            return conjugated_ratio

    def _compute_clustering(self, structure: Any) -> float:
        """
        Compute average clustering coefficient.

        Returns:
            Clustering coefficient (0.0 to 1.0)
        """
        # Simplified version: fraction of nodes in triangles
        if not hasattr(structure, 'bonds'):
            return 0.0

        num_nodes = len(structure.atoms)
        if num_nodes < 3:
            return 0.0

        # Build adjacency
        adj = [set() for _ in range(num_nodes)]
        for i, j, _ in structure.bonds:
            adj[i].add(j)
            adj[j].add(i)

        # Count triangles
        triangles = 0
        for i in range(num_nodes):
            for j in adj[i]:
                if j > i:  # Avoid double counting
                    common = adj[i] & adj[j]
                    triangles += len(common)

        # Normalize by possible triangles
        max_triangles = num_nodes * (num_nodes - 1) * (num_nodes - 2) / 6

        return triangles / max_triangles if max_triangles > 0 else 0.0
