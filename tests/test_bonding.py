"""
Test bonding rules (Level 0 → Level 1 composition).
"""

import sys
sys.path.insert(0, '/run/media/Barzin/SyncSpace-ext4/Codebases/Deus Ex Machina')

import time
from src.theory.generator import ElementGenerator
from src.level1.bonding import BondingRules


def test_specific_bonds():
    """Test specific bonds requested: C-H, C-C, C-O, Na-Cl, He-He"""
    print("\n" + "="*60)
    print("TEST: Specific Bond Predictions")
    print("="*60)

    gen = ElementGenerator()

    # Generate elements
    h = gen.generate(1)   # Hydrogen
    he = gen.generate(2)  # Helium
    c = gen.generate(6)   # Carbon
    o = gen.generate(8)   # Oxygen
    na = gen.generate(11) # Sodium
    cl = gen.generate(17) # Chlorine

    # Test cases: (elem_a, elem_b, expected_bond, expected_type, description)
    test_cases = [
        (c, h, True, "nonpolar_covalent", "C-H (methane backbone, ΔEN=0.35 < 0.5)"),
        (c, c, True, "nonpolar_covalent", "C-C (diamond, organic chains)"),
        (c, o, True, "polar_covalent", "C-O (alcohols, ethers)"),
        (na, cl, True, "ionic", "Na-Cl (table salt)"),
        (he, he, False, "none", "He-He (noble gas, no bond)"),
    ]

    print("\nBond predictions:\n")
    all_pass = True

    for elem_a, elem_b, expected_bond, expected_type, description in test_cases:
        bond = BondingRules.can_bond(elem_a, elem_b)

        # Check predictions
        bond_match = bond.can_bond == expected_bond
        type_match = bond.bond_type == expected_type

        status = "✓" if (bond_match and type_match) else "✗"

        print(f"{status} {description}")
        print(f"  {elem_a.symbol}-{elem_b.symbol}: "
              f"can_bond={bond.can_bond} (expected {expected_bond}), "
              f"type={bond.bond_type} (expected {expected_type})")
        print(f"  Confidence: {bond.confidence:.2f}")
        print(f"  Reasoning: {bond.reasoning}")
        print()

        if not (bond_match and type_match):
            all_pass = False

    if all_pass:
        print("✓ All specific bond tests PASSED\n")
    else:
        print("✗ Some tests FAILED\n")

    return all_pass


def test_confidence_propagation():
    """Test confidence propagation from Level 0 to Level 1"""
    print("="*60)
    print("TEST: Confidence Propagation")
    print("="*60)

    gen = ElementGenerator()

    # Test with elements of different confidence levels
    c = gen.generate(6)     # Z=6, confidence ~1.0
    elem_120 = gen.generate(120)  # Z=120, confidence ~0.85

    bond_observed = BondingRules.can_bond(c, c)
    bond_mixed = BondingRules.can_bond(c, elem_120)
    bond_theoretical = BondingRules.can_bond(elem_120, elem_120)

    print(f"\nC-C bond (both observed):")
    print(f"  Confidence: {bond_observed.confidence:.2f}")
    print(f"  Breakdown: {bond_observed.confidence_breakdown}")

    print(f"\nC-Ubn bond (mixed):")
    print(f"  Confidence: {bond_mixed.confidence:.2f}")
    print(f"  Breakdown: {bond_mixed.confidence_breakdown}")

    print(f"\nUbn-Ubn bond (both theoretical):")
    print(f"  Confidence: {bond_theoretical.confidence:.2f}")
    print(f"  Breakdown: {bond_theoretical.confidence_breakdown}")

    # Test is_reliable() method
    print(f"\nReliability checks (threshold=0.5):")
    print(f"  C-C reliable: {bond_observed.is_reliable(0.5)}")
    print(f"  C-Ubn reliable: {bond_mixed.is_reliable(0.5)}")
    print(f"  Ubn-Ubn reliable: {bond_theoretical.is_reliable(0.5)}")

    print(f"\nReliability checks (threshold=0.95):")
    print(f"  C-C reliable: {bond_observed.is_reliable(0.95)}")
    print(f"  C-Ubn reliable: {bond_mixed.is_reliable(0.95)}")
    print(f"  Ubn-Ubn reliable: {bond_theoretical.is_reliable(0.95)}")

    print("\n✓ Confidence propagation test complete\n")


def test_all_pairs_benchmark():
    """Benchmark all-pairs bonding table (118×118 elements)"""
    print("="*60)
    print("BENCHMARK: All-Pairs Bonding Table (118×118)")
    print("="*60)

    gen = ElementGenerator()

    # Generate all elements once (pre-computation)
    print("\nGenerating all 118 elements...")
    start_gen = time.time()
    elements = [gen.generate(Z) for Z in range(1, 119)]
    gen_time = time.time() - start_gen
    print(f"Generation time: {gen_time:.3f}s")

    # Compute all pairwise bonds
    print("\nComputing all pairwise bonds (118×118 = 13,924 pairs)...")
    start_bond = time.time()

    bond_count = 0
    can_bond_count = 0
    bond_types = {"nonpolar_covalent": 0, "polar_covalent": 0, "ionic": 0, "none": 0}

    for i, elem_a in enumerate(elements):
        for j, elem_b in enumerate(elements):
            bond = BondingRules.can_bond(elem_a, elem_b)
            bond_count += 1

            if bond.can_bond:
                can_bond_count += 1

            bond_types[bond.bond_type] = bond_types.get(bond.bond_type, 0) + 1

    bond_time = time.time() - start_bond

    # Results
    print(f"\nResults:")
    print(f"  Total pairs: {bond_count}")
    print(f"  Pairs that can bond: {can_bond_count} ({100*can_bond_count/bond_count:.1f}%)")
    print(f"  Nonpolar covalent: {bond_types.get('nonpolar_covalent', 0)}")
    print(f"  Polar covalent: {bond_types.get('polar_covalent', 0)}")
    print(f"  Ionic: {bond_types.get('ionic', 0)}")
    print(f"  No bond: {bond_types.get('none', 0)}")

    print(f"\nPerformance:")
    print(f"  Element generation: {gen_time:.3f}s ({gen_time*1000/118:.2f}ms per element)")
    print(f"  Bond computation: {bond_time:.3f}s ({bond_time*1000/bond_count:.2f}ms per bond)")
    print(f"  Total time: {gen_time + bond_time:.3f}s")

    # Check performance target
    target_time = 1.0  # Target: < 1 second
    if bond_time < target_time:
        print(f"\n✓ PERFORMANCE TARGET MET: {bond_time:.3f}s < {target_time}s")
        print(f"  Speedup vs target: {target_time/bond_time:.1f}x faster than required")
    else:
        print(f"\n✗ PERFORMANCE TARGET MISSED: {bond_time:.3f}s > {target_time}s")
        print(f"  Slowdown: {bond_time/target_time:.1f}x slower than required")

    # Compare to brute force quantum chemistry
    qc_time_per_bond = 60.0  # Assume 60 seconds per bond with DFT
    qc_total_time = qc_time_per_bond * bond_count
    speedup = qc_total_time / bond_time

    print(f"\nComparison to brute force (DFT @ ~60s/bond):")
    print(f"  DFT total time: {qc_total_time/3600:.1f} hours")
    print(f"  LUT total time: {bond_time:.3f}s")
    print(f"  Speedup: {speedup:.0f}x faster")
    print(f"  Orders of magnitude: ~10^{int(speedup/1000):d}")

    print("\n✓ Benchmark complete\n")

    return bond_time < target_time


def test_bond_classification():
    """Test electronegativity-based bond classification"""
    print("="*60)
    print("TEST: Bond Type Classification")
    print("="*60)

    gen = ElementGenerator()

    # Test various ΔEN ranges
    test_cases = [
        (1, 1, "nonpolar_covalent", "H-H (ΔEN=0.0)"),
        (6, 6, "nonpolar_covalent", "C-C (ΔEN=0.0)"),
        (6, 1, "nonpolar_covalent", "C-H (ΔEN=0.35 < 0.5)"),
        (6, 8, "polar_covalent", "C-O (ΔEN=0.89)"),
        (8, 1, "polar_covalent", "O-H (ΔEN=1.24)"),
        (11, 17, "ionic", "Na-Cl (ΔEN=2.23)"),
        (12, 8, "ionic", "Mg-O (ΔEN=2.13)"),
    ]

    print("\nBond type classifications:\n")
    all_pass = True

    for z_a, z_b, expected_type, description in test_cases:
        elem_a = gen.generate(z_a)
        elem_b = gen.generate(z_b)

        bond = BondingRules.can_bond(elem_a, elem_b)
        delta_en = abs(elem_a.electronegativity - elem_b.electronegativity)

        type_match = bond.bond_type == expected_type
        status = "✓" if type_match else "✗"

        print(f"{status} {description}")
        print(f"  Type: {bond.bond_type} (expected {expected_type})")
        print(f"  ΔEN: {delta_en:.2f}")
        print()

        if not type_match:
            all_pass = False

    if all_pass:
        print("✓ All bond classification tests PASSED\n")
    else:
        print("✗ Some tests FAILED\n")

    return all_pass


def main():
    """Run all bonding tests"""
    print("\n" + "="*60)
    print("BONDING RULES TEST SUITE (Level 0 → Level 1)")
    print("="*60)

    results = []

    # Test specific bonds
    results.append(("Specific bonds", test_specific_bonds()))

    # Test confidence propagation
    test_confidence_propagation()

    # Test bond classification
    results.append(("Bond classification", test_bond_classification()))

    # Benchmark performance
    results.append(("Performance benchmark", test_all_pairs_benchmark()))

    # Summary
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {name:30s}: {status}")

    all_pass = all(passed for _, passed in results)
    print()
    if all_pass:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("="*60)


if __name__ == '__main__':
    main()
