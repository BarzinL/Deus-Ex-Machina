"""
Test crystallization detection on benzene and other molecules.

This tests the fundamental question: Can we detect when a system should be
cached as a unit rather than decomposed?
"""

import json
from dataclasses import dataclass
from typing import List, Tuple
from src.crystallization.detector import CrystallizationDetector
from src.crystallization.naive import naive_bond_energy as _naive_bond_energy


@dataclass
class MolecularStructure:
    """Simple molecular structure representation."""
    name: str
    atoms: List[dict]
    bonds: List[Tuple[int, int, float]]  # (atom_i, atom_j, bond_order)
    actual_energy: float  # Experimental or QM value
    reference_energies: dict  # Bond energy lookup table


def load_molecule(filepath: str) -> MolecularStructure:
    """Load molecule from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)

    return MolecularStructure(
        name=data['name'],
        atoms=data['atoms'],
        bonds=[tuple(b) for b in data['bonds']],
        actual_energy=data['energies']['actual_bond_energy'],
        reference_energies=data['reference_energies']
    )


def naive_bond_energy(structure: MolecularStructure) -> float:
    """Naive additive energy: mean bond enthalpies over a valid Kekulé structure."""
    return _naive_bond_energy(structure.atoms, structure.bonds, structure.reference_energies)


def test_benzene_violation():
    """Test benzene - the canonical example of additivity violation."""
    print("\n" + "="*60)
    print("TEST: Benzene Additivity Violation")
    print("="*60)

    # Load benzene
    benzene = load_molecule('data/molecules/benzene.json')

    # Initialize detector
    detector = CrystallizationDetector(violation_threshold=0.05)

    # Measure violation
    violation = detector.measure_additivity_violation(
        structure=benzene,
        naive_fn=naive_bond_energy,
        actual_value=benzene.actual_energy,
        confidence=0.95  # High confidence - experimental data
    )

    print(f"\nMolecule: {benzene.name} ({len(benzene.atoms)} atoms)")
    print(f"\nEnergy Analysis:")
    print(f"  Naive additive energy: {violation.naive_value:.1f} kJ/mol")
    print(f"  Actual experimental energy: {violation.actual_value:.1f} kJ/mol")
    print(f"  Additivity violation: {violation.violation:.1f} kJ/mol")
    print(f"  Relative violation: {violation.relative_violation:.1%}")

    print(f"\nStructural Features:")
    features = violation.structural_features
    print(f"  Atoms: {features['num_nodes']}")
    print(f"  Bonds: {features['num_edges']}")
    print(f"  Cycles: {features['num_cycles']}")
    print(f"  Symmetry order: {features['symmetry_order']}")
    print(f"  Conjugation: {features['conjugation']:.2f}")
    print(f"  Has resonance: {features['conjugation'] > 0.5}")

    print(f"\nClassification: {violation.classification}")
    print(f"Reasoning: {violation.reasoning}")

    print(f"\nInterpretation (bond energy convention):")
    if violation.violation > 0:
        print(f"  → Bonds are STRONGER than naive prediction")
        print(f"  → Extra bond strength: {violation.violation:.1f} kJ/mol")
        print(f"  → System is MORE stable (aromatic resonance energy!)")
    elif violation.violation < 0:
        print(f"  → Bonds are WEAKER than naive prediction")
        print(f"  → Bond weakening: {abs(violation.violation):.1f} kJ/mol")
        print(f"  → System is LESS stable (e.g., ring strain)")
    else:
        print(f"  → Naive prediction is accurate")

    if violation.classification == "must_cache":
        print(f"\n✓ DECISION: Cache benzene as a unit (don't decompose)")
        print(f"  Additivity breaks down significantly due to resonance")
    elif violation.classification == "decomposes_cleanly":
        print(f"\n  DECISION: Can decompose into bonds")
    else:
        print(f"\n? DECISION: Uncertain - borderline case")

    # Check if significant
    print(f"\nSignificance test:")
    print(f"  Is significant (>5% threshold): {violation.is_significant()}")

    return violation


def test_hypothetical_ethane():
    """Test ethane (C2H6) - should decompose cleanly (no special structure)."""
    print("\n" + "="*60)
    print("TEST: Hypothetical Ethane (should decompose cleanly)")
    print("="*60)

    # Create simple ethane structure
    # C-C single bond + 6 C-H bonds
    @dataclass
    class SimpleStructure:
        name: str
        atoms: List[dict]
        bonds: List[Tuple[int, int, float]]

    ethane = SimpleStructure(
        name="Ethane",
        atoms=[
            {"index": 0, "element": "C"},
            {"index": 1, "element": "C"},
            {"index": 2, "element": "H"},
            {"index": 3, "element": "H"},
            {"index": 4, "element": "H"},
            {"index": 5, "element": "H"},
            {"index": 6, "element": "H"},
            {"index": 7, "element": "H"},
        ],
        bonds=[
            (0, 1, 1),  # C-C single
            (0, 2, 1), (0, 3, 1), (0, 4, 1),  # C-H on first carbon
            (1, 5, 1), (1, 6, 1), (1, 7, 1),  # C-H on second carbon
        ]
    )

    # Naive energy: 1×C-C + 6×C-H = 346 + 6×413 = 2824 kJ/mol
    naive_energy = 346 + 6 * 413  # = 2824 kJ/mol

    # Actual energy: very close to naive (ethane has no special structure)
    # Let's say 2835 kJ/mol (small ~0.4% deviation due to measurement uncertainty)
    actual_energy = 2835

    detector = CrystallizationDetector(violation_threshold=0.05)

    violation = detector.measure_additivity_violation(
        structure=ethane,
        naive_fn=lambda s: naive_energy,
        actual_value=actual_energy,
        confidence=0.90
    )

    print(f"\nMolecule: {ethane.name} ({len(ethane.atoms)} atoms)")
    print(f"\nEnergy Analysis:")
    print(f"  Naive additive energy: {violation.naive_value:.1f} kJ/mol")
    print(f"  Actual energy: {violation.actual_value:.1f} kJ/mol")
    print(f"  Additivity violation: {violation.violation:.1f} kJ/mol")
    print(f"  Relative violation: {violation.relative_violation:.1%}")

    print(f"\nStructural Features:")
    features = violation.structural_features
    print(f"  Atoms: {features['num_nodes']}")
    print(f"  Bonds: {features['num_edges']}")
    print(f"  Cycles: {features['num_cycles']}")
    print(f"  Symmetry order: {features['symmetry_order']}")
    print(f"  Conjugation: {features['conjugation']:.2f}")

    print(f"\nClassification: {violation.classification}")
    print(f"Reasoning: {violation.reasoning}")

    if violation.classification == "decomposes_cleanly":
        print(f"\n✓ DECISION: Ethane decomposes cleanly into bonds")
        print(f"  No need to cache as special unit")
    elif violation.classification == "must_cache":
        print(f"\n  DECISION: Should cache (unexpected!)")
    else:
        print(f"\n? DECISION: Uncertain")

    return violation


def main():
    """Run crystallization detection tests."""
    print("\n" + "="*60)
    print("CRYSTALLIZATION DETECTION TEST SUITE")
    print("Question: When should systems be cached vs decomposed?")
    print("="*60)

    # Test 1: Benzene (must cache)
    benzene_violation = test_benzene_violation()

    # Test 2: Ethane (decomposes cleanly)
    ethane_violation = test_hypothetical_ethane()

    # Summary
    print("\n" + "="*60)
    print("SUMMARY: Crystallization Detection")
    print("="*60)

    print(f"\nBenzene:")
    print(f"  Violation: {benzene_violation.relative_violation:.1%}")
    print(f"  Decision: {benzene_violation.classification}")
    print(f"  → Resonance creates compositional boundary")

    print(f"\nEthane:")
    print(f"  Violation: {ethane_violation.relative_violation:.1%}")
    print(f"  Decision: {ethane_violation.classification}")
    print(f"  → No special structure, additivity works")

    print(f"\nKey Insight:")
    print(f"  Large additivity violations signal compositional boundaries.")
    print(f"  Benzene MUST be cached as a unit (resonance).")
    print(f"  Ethane CAN be decomposed into bonds (no collective effects).")

    print(f"\nNext Steps:")
    print(f"  1. Test on 50+ molecules to find patterns")
    print(f"  2. Correlate violations with structural features")
    print(f"  3. Extract general principle of crystallization")
    print(f"  4. Apply to QCD (Karyon search space pruning)")

    print("="*60)


if __name__ == '__main__':
    main()
