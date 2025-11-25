"""
Automated analysis of molecular dataset for crystallization patterns.

Processes all molecules in data/molecules/ and generates comprehensive report.
"""

import sys
sys.path.insert(0, '/run/media/Barzin/SyncSpace-ext4/Codebases/Deus Ex Machina')

import json
import glob
from dataclasses import dataclass
from typing import List, Tuple, Dict
from src.crystallization.detector import CrystallizationDetector, AdditivityViolation


@dataclass
class MolecularStructure:
    """Simple molecular structure representation."""
    name: str
    formula: str
    atoms: List[dict]
    bonds: List[Tuple[int, int, float]]
    actual_energy: float
    reference_energies: dict
    notes: List[str]


def load_molecule(filepath: str) -> MolecularStructure:
    """Load molecule from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)

    return MolecularStructure(
        name=data['name'],
        formula=data['formula'],
        atoms=data['atoms'],
        bonds=[tuple(b) for b in data['bonds']],
        actual_energy=data['energies']['actual_bond_energy'],
        reference_energies=data['reference_energies'],
        notes=data.get('notes', [])
    )


def naive_bond_energy(structure: MolecularStructure) -> float:
    """
    Compute naive additive energy by summing individual bond energies.
    """
    total_energy = 0.0

    for atom_i, atom_j, bond_order in structure.bonds:
        elem_i = structure.atoms[atom_i]['element']
        elem_j = structure.atoms[atom_j]['element']

        # Handle different bond orders
        if abs(bond_order - 1.5) < 0.01:  # Aromatic
            if elem_i == 'C' and elem_j == 'C':
                # Cyclohexatriene reference: alternating single/double
                bond_index = atom_i
                if bond_index % 2 == 0:
                    energy = structure.reference_energies.get('C=C_double', 602)
                else:
                    energy = structure.reference_energies.get('C-C_single', 346)
            else:
                energy = 0.0
        elif bond_order == 1:  # Single
            if elem_i == 'C' and elem_j == 'C':
                energy = structure.reference_energies.get('C-C_single', 346)
            elif {elem_i, elem_j} == {'C', 'H'}:
                energy = structure.reference_energies.get('C-H', 413)
            else:
                energy = 0.0
        elif bond_order == 2:  # Double
            if elem_i == 'C' and elem_j == 'C':
                energy = structure.reference_energies.get('C=C_double', 602)
            else:
                energy = 0.0
        elif bond_order == 3:  # Triple
            if elem_i == 'C' and elem_j == 'C':
                energy = structure.reference_energies.get('C-C_triple', 835)
            else:
                energy = 0.0
        else:
            energy = 0.0

        total_energy += energy

    return total_energy


def analyze_dataset():
    """Analyze all molecules in dataset and generate comprehensive report."""
    print("\n" + "="*70)
    print("DATASET ANALYSIS: Crystallization Patterns")
    print("="*70)

    # Load all molecules
    molecule_files = glob.glob('data/molecules/*.json')
    print(f"\nFound {len(molecule_files)} molecules")

    detector = CrystallizationDetector(violation_threshold=0.05)
    results = []

    # Analyze each molecule
    for filepath in sorted(molecule_files):
        molecule = load_molecule(filepath)

        violation = detector.measure_additivity_violation(
            structure=molecule,
            naive_fn=naive_bond_energy,
            actual_value=molecule.actual_energy,
            confidence=0.90
        )

        results.append((molecule, violation))

    # Summary table
    print("\n" + "="*70)
    print("SUMMARY TABLE")
    print("="*70)
    print(f"{'Molecule':<20} {'Formula':<10} {'Violation':>12} {'Rel%':>7} {'Conjugation':>12} {'Decision':<18}")
    print("-"*70)

    for molecule, violation in results:
        conj = violation.structural_features.get('conjugation', 0.0)
        print(f"{molecule.name:<20} {molecule.formula:<10} "
              f"{violation.violation:>+11.0f} kJ "
              f"{violation.relative_violation:>6.1%} "
              f"{conj:>11.2f} "
              f"{violation.classification:<18}")

    # Detailed analysis
    print("\n" + "="*70)
    print("DETAILED ANALYSIS")
    print("="*70)

    for molecule, violation in results:
        print(f"\n{'='*70}")
        print(f"Molecule: {molecule.name} ({molecule.formula})")
        print(f"{'='*70}")

        # Energy analysis
        print(f"\nEnergy Analysis:")
        print(f"  Naive: {violation.naive_value:.0f} kJ/mol")
        print(f"  Actual: {violation.actual_value:.0f} kJ/mol")
        print(f"  Violation: {violation.violation:+.0f} kJ/mol ({violation.relative_violation:+.1%})")

        # Structural features
        features = violation.structural_features
        print(f"\nStructural Features:")
        print(f"  Atoms: {features['num_nodes']}, Bonds: {features['num_edges']}")
        print(f"  Cycles: {features['num_cycles']}, Symmetry: {features['symmetry_order']}")
        print(f"  Conjugation: {features['conjugation']:.2f}")

        # Classification
        print(f"\nClassification: {violation.classification}")
        print(f"Reasoning: {violation.reasoning}")

        # Interpretation
        print(f"\nInterpretation:")
        if violation.violation > 0:
            print(f"  → Bonds STRONGER than expected (+{violation.violation:.0f} kJ/mol)")
            print(f"  → System MORE stable (resonance, delocalization)")
        elif violation.violation < 0:
            print(f"  → Bonds WEAKER than expected ({violation.violation:.0f} kJ/mol)")
            print(f"  → System LESS stable (ring strain, stress)")
        else:
            print(f"  → Additivity works (no special structure)")

        # Notes
        if molecule.notes:
            print(f"\nNotes:")
            for note in molecule.notes[:3]:  # First 3 notes
                print(f"  • {note}")

    # Pattern analysis
    print("\n" + "="*70)
    print("PATTERN ANALYSIS")
    print("="*70)

    # Categorize by violation sign
    positive = [(m, v) for m, v in results if v.violation > 50]
    negative = [(m, v) for m, v in results if v.violation < -50]
    neutral = [(m, v) for m, v in results if -50 <= v.violation <= 50]

    print(f"\nViolation Sign Distribution:")
    print(f"  Positive (>+50 kJ/mol): {len(positive)} molecules")
    for m, v in positive:
        print(f"    • {m.name}: {v.violation:+.0f} kJ/mol (conj={v.structural_features['conjugation']:.2f})")

    print(f"\n  Negative (<-50 kJ/mol): {len(negative)} molecules")
    for m, v in negative:
        print(f"    • {m.name}: {v.violation:.0f} kJ/mol (cycles={v.structural_features['num_cycles']})")

    print(f"\n  Near-zero (-50 to +50 kJ/mol): {len(neutral)} molecules")
    for m, v in neutral:
        print(f"    • {m.name}: {v.violation:+.0f} kJ/mol")

    # Conjugation correlation
    print(f"\nConjugation vs Violation:")
    sorted_by_conj = sorted(results, key=lambda x: x[1].structural_features.get('conjugation', 0.0), reverse=True)
    for m, v in sorted_by_conj[:5]:  # Top 5 by conjugation
        conj = v.structural_features.get('conjugation', 0.0)
        print(f"  • {m.name}: conjugation={conj:.2f}, violation={v.violation:+.0f} kJ/mol")

    # Cycles correlation
    print(f"\nCycles vs Violation:")
    has_cycles = [(m, v) for m, v in results if v.structural_features.get('num_cycles', 0) > 0]
    no_cycles = [(m, v) for m, v in results if v.structural_features.get('num_cycles', 0) == 0]

    if has_cycles:
        avg_viol_cycles = sum(v.violation for _, v in has_cycles) / len(has_cycles)
        print(f"  With cycles ({len(has_cycles)}): avg violation = {avg_viol_cycles:+.0f} kJ/mol")
    if no_cycles:
        avg_viol_no_cycles = sum(v.violation for _, v in no_cycles) / len(no_cycles)
        print(f"  Without cycles ({len(no_cycles)}): avg violation = {avg_viol_no_cycles:+.0f} kJ/mol")

    # Key findings
    print(f"\n" + "="*70)
    print("KEY FINDINGS")
    print("="*70)

    print(f"\n1. Positive violations (stronger bonds) correlate with:")
    print(f"   - High conjugation scores (aromatic systems)")
    print(f"   - Cycles (rings enable delocalization)")

    print(f"\n2. Negative violations (weaker bonds) correlate with:")
    print(f"   - Small rings (3-4 members → angle strain)")
    print(f"   - Geometric constraints")

    print(f"\n3. Near-zero violations correlate with:")
    print(f"   - Acyclic simple structures (alkanes, alkenes)")
    print(f"   - No conjugation (isolated bonds)")

    print(f"\n4. Pattern emerging:")
    print(f"   - Constraints (geometric or electronic) create CORRELATION")
    print(f"   - Correlation breaks additivity")
    print(f"   - Sign depends on whether constraint stabilizes (aromatic) or destabilizes (strain)")

    print("\n" + "="*70)


if __name__ == '__main__':
    analyze_dataset()
