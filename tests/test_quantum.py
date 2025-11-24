"""
Test electron configuration generator against known elements.
"""

import sys
sys.path.insert(0, '/run/media/Barzin/SyncSpace-ext4/Codebases/Deus Ex Machina')

from src.theory.quantum import madelung_rule, count_valence, orbital_type


def test_element(Z: int, name: str, expected_config: str, expected_valence: int, expected_block: str):
    """Test a single element against expected values."""
    print(f"\n{'='*60}")
    print(f"Testing {name} (Z={Z})")
    print(f"{'='*60}")

    # Generate configuration
    config = madelung_rule(Z, use_noble_gas_core=True)
    print(f"Generated config: {config}")
    print(f"Expected config:  {expected_config}")

    # Check valence electrons
    valence = count_valence(config)
    print(f"\nValence electrons: {valence} (expected: {expected_valence})")

    # Check orbital type
    block = orbital_type(config)
    print(f"Orbital type (block): {block} (expected: {expected_block})")

    # Validate
    config_match = config == expected_config
    valence_match = valence == expected_valence
    block_match = block == expected_block

    print(f"\n✓ Configuration: {'PASS' if config_match else 'FAIL'}")
    print(f"✓ Valence:       {'PASS' if valence_match else 'FAIL'}")
    print(f"✓ Block:         {'PASS' if block_match else 'FAIL'}")

    overall = config_match and valence_match and block_match
    print(f"\nOverall: {'✓ PASS' if overall else '✗ FAIL'}")

    return overall


def main():
    """Run tests for specified elements."""
    print("\n" + "="*60)
    print("ELECTRON CONFIGURATION GENERATOR - TEST SUITE")
    print("="*60)

    results = []

    # Test 1: Hydrogen (simplest)
    results.append(test_element(
        Z=1,
        name="Hydrogen",
        expected_config="1s1",
        expected_valence=1,
        expected_block='s'
    ))

    # Test 2: Carbon (biologically important, p-block)
    results.append(test_element(
        Z=6,
        name="Carbon",
        expected_config="[He] 2s2 2p2",
        expected_valence=4,
        expected_block='p'
    ))

    # Test 3: Gold (d-block, Madelung exception)
    results.append(test_element(
        Z=79,
        name="Gold",
        expected_config="[Xe] 4f14 5d10 6s1",
        expected_valence=1,  # Only 6s1 in valence
        expected_block='s'  # Last electron is in 6s
    ))

    # Test 4: Oganesson (heaviest observed, noble gas)
    results.append(test_element(
        Z=118,
        name="Oganesson",
        expected_config="[Rn] 5f14 6d10 7s2 7p6",
        expected_valence=8,  # 7s2 7p6
        expected_block='p'
    ))

    # Test 5: Element 120 (theoretical, island of stability)
    # Pyykkö (2011) predicts: [Og] 8s2
    results.append(test_element(
        Z=120,
        name="Unbinilium",
        expected_config="[Og] 8s2",
        expected_valence=2,
        expected_block='s'
    ))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total tests: {len(results)}")
    print(f"Passed: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")
    print(f"\nSuccess rate: {100 * sum(results) / len(results):.1f}%")

    if all(results):
        print("\n✓ ALL TESTS PASSED")
    else:
        print("\n✗ SOME TESTS FAILED")


if __name__ == '__main__':
    main()
