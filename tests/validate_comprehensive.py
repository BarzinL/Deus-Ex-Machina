"""
Comprehensive validation of electron configuration generator.
Tests key elements across all periods and blocks.
"""

import sys
sys.path.insert(0, '/run/media/Barzin/SyncSpace-ext4/Codebases/Deus Ex Machina')

from src.theory.quantum import madelung_rule, count_valence, orbital_type


# Reference data: (Z, symbol, name, expected_config, valence, block)
REFERENCE_ELEMENTS = [
    # Period 1
    (1, 'H', 'Hydrogen', '1s1', 1, 's'),
    (2, 'He', 'Helium', '1s2', 2, 's'),

    # Period 2
    (3, 'Li', 'Lithium', '[He] 2s1', 1, 's'),
    (6, 'C', 'Carbon', '[He] 2s2 2p2', 4, 'p'),
    (8, 'O', 'Oxygen', '[He] 2s2 2p4', 6, 'p'),
    (10, 'Ne', 'Neon', '[He] 2s2 2p6', 8, 'p'),

    # Period 3
    (11, 'Na', 'Sodium', '[Ne] 3s1', 1, 's'),
    (17, 'Cl', 'Chlorine', '[Ne] 3s2 3p5', 7, 'p'),

    # Period 4 - including Madelung exceptions
    (19, 'K', 'Potassium', '[Ar] 4s1', 1, 's'),
    (24, 'Cr', 'Chromium', '[Ar] 3d5 4s1', 1, 's'),  # Exception: half-filled d
    (26, 'Fe', 'Iron', '[Ar] 3d6 4s2', 2, 's'),
    (29, 'Cu', 'Copper', '[Ar] 3d10 4s1', 1, 's'),  # Exception: filled d
    (30, 'Zn', 'Zinc', '[Ar] 3d10 4s2', 2, 's'),

    # Period 5 - more exceptions
    (41, 'Nb', 'Niobium', '[Kr] 4d4 5s1', 1, 's'),  # Exception
    (42, 'Mo', 'Molybdenum', '[Kr] 4d5 5s1', 1, 's'),  # Exception
    (44, 'Ru', 'Ruthenium', '[Kr] 4d7 5s1', 1, 's'),  # Exception
    (46, 'Pd', 'Palladium', '[Kr] 4d10', 0, 'd'),  # Exception: no s
    (47, 'Ag', 'Silver', '[Kr] 4d10 5s1', 1, 's'),  # Exception

    # Period 6 - f-block lanthanides
    (57, 'La', 'Lanthanum', '[Xe] 5d1 6s2', 2, 's'),
    (58, 'Ce', 'Cerium', '[Xe] 4f1 5d1 6s2', 2, 's'),
    (64, 'Gd', 'Gadolinium', '[Xe] 4f7 5d1 6s2', 2, 's'),  # Half-filled f
    (78, 'Pt', 'Platinum', '[Xe] 4f14 5d9 6s1', 1, 's'),  # Exception
    (79, 'Au', 'Gold', '[Xe] 4f14 5d10 6s1', 1, 's'),  # Exception
    (80, 'Hg', 'Mercury', '[Xe] 4f14 5d10 6s2', 2, 's'),

    # Period 7 - f-block actinides
    (89, 'Ac', 'Actinium', '[Rn] 6d1 7s2', 2, 's'),
    (92, 'U', 'Uranium', '[Rn] 5f3 6d1 7s2', 2, 's'),

    # Superheavy elements
    (118, 'Og', 'Oganesson', '[Rn] 5f14 6d10 7s2 7p6', 8, 'p'),

    # Period 8 - theoretical
    (119, 'Uue', 'Ununennium', '[Og] 8s1', 1, 's'),
    (120, 'Ubn', 'Unbinilium', '[Og] 8s2', 2, 's'),
]


def validate_element(Z: int, symbol: str, name: str, expected_config: str,
                     expected_valence: int, expected_block: str, verbose: bool = False) -> bool:
    """Validate a single element."""
    config = madelung_rule(Z, use_noble_gas_core=True)
    valence = count_valence(config)
    block = orbital_type(config)

    config_match = config == expected_config
    valence_match = valence == expected_valence
    block_match = block == expected_block

    if verbose or not (config_match and valence_match and block_match):
        print(f"\n{symbol} (Z={Z}, {name}):")
        if not config_match:
            print(f"  Config:  {config} (expected: {expected_config}) ✗")
        else:
            print(f"  Config:  {config} ✓")

        if not valence_match:
            print(f"  Valence: {valence} (expected: {expected_valence}) ✗")
        else:
            print(f"  Valence: {valence} ✓")

        if not block_match:
            print(f"  Block:   {block} (expected: {expected_block}) ✗")
        else:
            print(f"  Block:   {block} ✓")

    return config_match and valence_match and block_match


def main():
    """Run comprehensive validation."""
    print("="*60)
    print("COMPREHENSIVE VALIDATION: Z=1-120 KEY ELEMENTS")
    print("="*60)

    results = []
    failures = []

    for Z, symbol, name, config, valence, block in REFERENCE_ELEMENTS:
        result = validate_element(Z, symbol, name, config, valence, block, verbose=False)
        results.append(result)
        if not result:
            failures.append((Z, symbol, name))

    # Summary
    print(f"\nTotal elements tested: {len(results)}")
    print(f"Passed: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")
    print(f"\nSuccess rate: {100 * sum(results) / len(results):.1f}%")

    if failures:
        print(f"\nFailed elements:")
        for Z, symbol, name in failures:
            # Re-run with verbose to show details
            expected = next((e for e in REFERENCE_ELEMENTS if e[0] == Z), None)
            if expected:
                validate_element(*expected, verbose=True)
    else:
        print("\n✓ ALL TESTS PASSED")

    # Test a few additional elements for spot checking
    print("\n" + "="*60)
    print("SPOT CHECK: Additional elements")
    print("="*60)

    spot_check = [
        (13, 'Al', 'Aluminum'),
        (20, 'Ca', 'Calcium'),
        (33, 'As', 'Arsenic'),
        (50, 'Sn', 'Tin'),
        (82, 'Pb', 'Lead'),
    ]

    for Z, symbol, name in spot_check:
        config = madelung_rule(Z, use_noble_gas_core=True)
        valence = count_valence(config)
        block = orbital_type(config)
        print(f"{symbol:3s} (Z={Z:3d}): {config:30s} | valence={valence} | block={block}")


if __name__ == '__main__':
    main()
