"""
Quantum mechanical calculations for atomic properties.

This module implements electron configuration generation, valence electron
counting, and orbital properties based on quantum mechanics.
"""

from typing import List, Tuple


# Orbital capacity: s=2, p=6, d=10, f=14, g=18
ORBITAL_CAPACITY = {
    's': 2,
    'p': 6,
    'd': 10,
    'f': 14,
    'g': 18
}

# Noble gas cores for compact notation
NOBLE_GASES = {
    2: 'He',
    10: 'Ne',
    18: 'Ar',
    36: 'Kr',
    54: 'Xe',
    86: 'Rn',
    118: 'Og'
}

# Known exceptions to Madelung rule (half-filled and filled d-orbitals are stabilized)
# Also includes lanthanide/actinide exceptions where d fills before f
# Format: Z → (expected_config_suffix, actual_config_suffix)
MADELUNG_EXCEPTIONS = {
    24: ('3d4 4s2', '3d5 4s1'),  # Cr: half-filled d
    29: ('3d9 4s2', '3d10 4s1'),  # Cu: filled d
    41: ('4d3 5s2', '4d4 5s1'),  # Nb: half-filled d
    42: ('4d4 5s2', '4d5 5s1'),  # Mo: half-filled d
    44: ('4d6 5s2', '4d7 5s1'),  # Ru: half-filled d
    45: ('4d7 5s2', '4d8 5s1'),  # Rh: filled d
    46: ('4d8 5s2', '4d10'),     # Pd: filled d, no s
    47: ('4d9 5s2', '4d10 5s1'), # Ag: filled d
    57: ('4f1 6s2', '5d1 6s2'),  # La: 5d before 4f
    58: ('4f2 6s2', '4f1 5d1 6s2'),  # Ce: mixed f and d
    64: ('4f8 6s2', '4f7 5d1 6s2'),  # Gd: half-filled f + one d
    78: ('5d8 6s2', '5d9 6s1'),  # Pt: filled d
    79: ('5d9 6s2', '5d10 6s1'), # Au: filled d
    89: ('5f1 7s2', '6d1 7s2'),  # Ac: 6d before 5f
    90: ('5f2 7s2', '6d2 7s2'),  # Th: 6d before 5f
    91: ('5f3 7s2', '5f2 6d1 7s2'),  # Pa: mixed f and d
    92: ('5f4 7s2', '5f3 6d1 7s2'),  # U: mixed f and d
    93: ('5f5 7s2', '5f4 6d1 7s2'),  # Np: mixed f and d
    96: ('5f8 7s2', '5f7 6d1 7s2'),  # Cm: half-filled f + one d
    103: ('5f15 7s2', '5f14 6d1 7s2'),  # Lr: 6d before end of 5f
}


def _aufbau_order() -> List[Tuple[int, str]]:
    """
    Generate orbital filling order using Madelung (n+l) rule.

    The Aufbau principle states that orbitals are filled in order of
    increasing n+l, with ties broken by lower n first.

    Ordering: 1s < 2s < 2p < 3s < 3p < 4s < 3d < 4p < 5s < 4d < 5p < 6s < 4f < 5d < ...

    For period 8 (Z>118), g-block (l=4) orbitals appear.

    References:
    - Madelung, E. (1936). Die Mathematischen Hilfsmittel des Physikers
    - Klechkovskii, V.M. (1962). Distribution of Atomic Electrons and the Rule of Successive Filling of (n+l) Groups

    Returns:
        List of (n, orbital) tuples in filling order
    """
    orbitals = []

    # Generate up to n=10, l=4 (g orbitals) for superheavy elements
    for n in range(1, 11):
        for l_symbol in ['s', 'p', 'd', 'f', 'g']:
            l = {'s': 0, 'p': 1, 'd': 2, 'f': 3, 'g': 4}[l_symbol]
            if l < n:  # Only include valid quantum numbers (l < n)
                orbitals.append((n, l_symbol))

    # Sort by n+l, then by n
    orbitals.sort(key=lambda x: (x[0] + {'s': 0, 'p': 1, 'd': 2, 'f': 3, 'g': 4}[x[1]], x[0]))

    return orbitals


def madelung_rule(Z: int, use_noble_gas_core: bool = True) -> str:
    """
    Generate electron configuration using Madelung (n+l) rule with known exceptions.

    The Madelung rule (also called Aufbau principle or Klechkovskii rule) predicts
    the order in which atomic orbitals are filled based on n+l values.

    Known exceptions due to electron-electron interactions:
    - Half-filled d orbitals (d5, d10) are extra stable
    - Filled d orbitals (d10) are extra stable
    - Lanthanides/Actinides: 5d/6d can fill before 4f/5f

    For Z>118, the standard Madelung rule is used (relativistic corrections
    should be applied via model-specific functions for accuracy).

    Args:
        Z: Atomic number (1-173)
        use_noble_gas_core: If True, use [He], [Ne], etc. notation

    Returns:
        Electron configuration string (e.g., "1s2 2s2 2p6" or "[Ne] 3s2")

    References:
    - Madelung, E. (1936). Die Mathematischen Hilfsmittel des Physikers
    - For Z>118: Pyykkö, P. (2011). Phys. Chem. Chem. Phys. 13, 161
    - Exceptions: Scerri, E.R. (2013). Mendeleev to Oganesson, Oxford University Press

    Examples:
        >>> madelung_rule(1)
        '1s1'
        >>> madelung_rule(6)
        '[He] 2s2 2p2'
        >>> madelung_rule(79)
        '[Xe] 4f14 5d10 6s1'
    """
    if Z < 1 or Z > 173:
        raise ValueError(f"Atomic number must be between 1 and 173, got {Z}")

    # Generate filling order
    aufbau = _aufbau_order()

    # Fill orbitals
    config = []
    electrons_remaining = Z

    for n, orbital in aufbau:
        if electrons_remaining <= 0:
            break

        capacity = ORBITAL_CAPACITY[orbital]
        electrons_in_orbital = min(electrons_remaining, capacity)

        if electrons_in_orbital > 0:
            config.append((n, orbital, electrons_in_orbital))

        electrons_remaining -= electrons_in_orbital

    # Apply known exceptions for Z <= 118
    if Z in MADELUNG_EXCEPTIONS:
        config = _apply_exception(Z, config)

    # Format as string
    if use_noble_gas_core:
        return _format_with_noble_gas_core(Z, config)
    else:
        return _format_config(config)


def _apply_exception(Z: int, config: List[Tuple[int, str, int]]) -> List[Tuple[int, str, int]]:
    """
    Apply known exceptions to Madelung rule.

    This handles cases where electron-electron repulsion or exchange energy
    stabilizes non-aufbau configurations (e.g., Cr: 3d5 4s1 vs. 3d4 4s2).

    Args:
        Z: Atomic number
        config: List of (n, orbital, count) tuples

    Returns:
        Modified configuration with exception applied
    """
    # Hardcoded configurations for exception elements
    # Format: full electron configuration as tuples

    EXCEPTION_CONFIGS = {
        24: [(1, 's', 2), (2, 's', 2), (2, 'p', 6), (3, 's', 2), (3, 'p', 6), (3, 'd', 5), (4, 's', 1)],  # Cr
        29: [(1, 's', 2), (2, 's', 2), (2, 'p', 6), (3, 's', 2), (3, 'p', 6), (3, 'd', 10), (4, 's', 1)],  # Cu
        41: [(1, 's', 2), (2, 's', 2), (2, 'p', 6), (3, 's', 2), (3, 'p', 6), (3, 'd', 10), (4, 's', 2), (4, 'p', 6), (4, 'd', 4), (5, 's', 1)],  # Nb
        42: [(1, 's', 2), (2, 's', 2), (2, 'p', 6), (3, 's', 2), (3, 'p', 6), (3, 'd', 10), (4, 's', 2), (4, 'p', 6), (4, 'd', 5), (5, 's', 1)],  # Mo
        44: [(1, 's', 2), (2, 's', 2), (2, 'p', 6), (3, 's', 2), (3, 'p', 6), (3, 'd', 10), (4, 's', 2), (4, 'p', 6), (4, 'd', 7), (5, 's', 1)],  # Ru
        45: [(1, 's', 2), (2, 's', 2), (2, 'p', 6), (3, 's', 2), (3, 'p', 6), (3, 'd', 10), (4, 's', 2), (4, 'p', 6), (4, 'd', 8), (5, 's', 1)],  # Rh
        46: [(1, 's', 2), (2, 's', 2), (2, 'p', 6), (3, 's', 2), (3, 'p', 6), (3, 'd', 10), (4, 's', 2), (4, 'p', 6), (4, 'd', 10)],  # Pd
        47: [(1, 's', 2), (2, 's', 2), (2, 'p', 6), (3, 's', 2), (3, 'p', 6), (3, 'd', 10), (4, 's', 2), (4, 'p', 6), (4, 'd', 10), (5, 's', 1)],  # Ag
        57: [(1, 's', 2), (2, 's', 2), (2, 'p', 6), (3, 's', 2), (3, 'p', 6), (3, 'd', 10), (4, 's', 2), (4, 'p', 6), (4, 'd', 10), (5, 's', 2), (5, 'p', 6), (5, 'd', 1), (6, 's', 2)],  # La
        58: [(1, 's', 2), (2, 's', 2), (2, 'p', 6), (3, 's', 2), (3, 'p', 6), (3, 'd', 10), (4, 's', 2), (4, 'p', 6), (4, 'd', 10), (5, 's', 2), (5, 'p', 6), (4, 'f', 1), (5, 'd', 1), (6, 's', 2)],  # Ce
        64: [(1, 's', 2), (2, 's', 2), (2, 'p', 6), (3, 's', 2), (3, 'p', 6), (3, 'd', 10), (4, 's', 2), (4, 'p', 6), (4, 'd', 10), (5, 's', 2), (5, 'p', 6), (4, 'f', 7), (5, 'd', 1), (6, 's', 2)],  # Gd
        78: [(1, 's', 2), (2, 's', 2), (2, 'p', 6), (3, 's', 2), (3, 'p', 6), (3, 'd', 10), (4, 's', 2), (4, 'p', 6), (4, 'd', 10), (5, 's', 2), (5, 'p', 6), (4, 'f', 14), (5, 'd', 9), (6, 's', 1)],  # Pt
        79: [(1, 's', 2), (2, 's', 2), (2, 'p', 6), (3, 's', 2), (3, 'p', 6), (3, 'd', 10), (4, 's', 2), (4, 'p', 6), (4, 'd', 10), (5, 's', 2), (5, 'p', 6), (4, 'f', 14), (5, 'd', 10), (6, 's', 1)],  # Au
        89: [(1, 's', 2), (2, 's', 2), (2, 'p', 6), (3, 's', 2), (3, 'p', 6), (3, 'd', 10), (4, 's', 2), (4, 'p', 6), (4, 'd', 10), (5, 's', 2), (5, 'p', 6), (4, 'f', 14), (5, 'd', 10), (6, 's', 2), (6, 'p', 6), (6, 'd', 1), (7, 's', 2)],  # Ac
        90: [(1, 's', 2), (2, 's', 2), (2, 'p', 6), (3, 's', 2), (3, 'p', 6), (3, 'd', 10), (4, 's', 2), (4, 'p', 6), (4, 'd', 10), (5, 's', 2), (5, 'p', 6), (4, 'f', 14), (5, 'd', 10), (6, 's', 2), (6, 'p', 6), (6, 'd', 2), (7, 's', 2)],  # Th
        91: [(1, 's', 2), (2, 's', 2), (2, 'p', 6), (3, 's', 2), (3, 'p', 6), (3, 'd', 10), (4, 's', 2), (4, 'p', 6), (4, 'd', 10), (5, 's', 2), (5, 'p', 6), (4, 'f', 14), (5, 'd', 10), (6, 's', 2), (6, 'p', 6), (5, 'f', 2), (6, 'd', 1), (7, 's', 2)],  # Pa
        92: [(1, 's', 2), (2, 's', 2), (2, 'p', 6), (3, 's', 2), (3, 'p', 6), (3, 'd', 10), (4, 's', 2), (4, 'p', 6), (4, 'd', 10), (5, 's', 2), (5, 'p', 6), (4, 'f', 14), (5, 'd', 10), (6, 's', 2), (6, 'p', 6), (5, 'f', 3), (6, 'd', 1), (7, 's', 2)],  # U
        93: [(1, 's', 2), (2, 's', 2), (2, 'p', 6), (3, 's', 2), (3, 'p', 6), (3, 'd', 10), (4, 's', 2), (4, 'p', 6), (4, 'd', 10), (5, 's', 2), (5, 'p', 6), (4, 'f', 14), (5, 'd', 10), (6, 's', 2), (6, 'p', 6), (5, 'f', 4), (6, 'd', 1), (7, 's', 2)],  # Np
        96: [(1, 's', 2), (2, 's', 2), (2, 'p', 6), (3, 's', 2), (3, 'p', 6), (3, 'd', 10), (4, 's', 2), (4, 'p', 6), (4, 'd', 10), (5, 's', 2), (5, 'p', 6), (4, 'f', 14), (5, 'd', 10), (6, 's', 2), (6, 'p', 6), (5, 'f', 7), (6, 'd', 1), (7, 's', 2)],  # Cm
        103: [(1, 's', 2), (2, 's', 2), (2, 'p', 6), (3, 's', 2), (3, 'p', 6), (3, 'd', 10), (4, 's', 2), (4, 'p', 6), (4, 'd', 10), (5, 's', 2), (5, 'p', 6), (4, 'f', 14), (5, 'd', 10), (6, 's', 2), (6, 'p', 6), (5, 'f', 14), (6, 'd', 1), (7, 's', 2)],  # Lr
    }

    return EXCEPTION_CONFIGS.get(Z, config)


def _format_config(config: List[Tuple[int, str, int]]) -> str:
    """
    Format configuration as string: '1s2 2s2 2p6'.

    Orbitals are sorted by n first, then by l within the same n.
    This follows standard notation convention (not filling order).
    """
    # Sort by (n, l_value) where l_value = {s:0, p:1, d:2, f:3, g:4}
    l_order = {'s': 0, 'p': 1, 'd': 2, 'f': 3, 'g': 4}
    sorted_config = sorted(config, key=lambda x: (x[0], l_order.get(x[1], 5)))

    return ' '.join(f"{n}{orb}{count}" for n, orb, count in sorted_config)


def _format_with_noble_gas_core(Z: int, config: List[Tuple[int, str, int]]) -> str:
    """
    Format configuration using noble gas core notation.

    Examples:
        Carbon (Z=6): [He] 2s2 2p2
        Gold (Z=79): [Xe] 4f14 5d10 6s1
    """
    # Find the largest noble gas core less than Z
    core_Z = max([ng_Z for ng_Z in NOBLE_GASES.keys() if ng_Z < Z], default=0)

    if core_Z == 0:
        # No noble gas core (H, He)
        return _format_config(config)

    # Count electrons in core
    core_electrons = core_Z

    # Filter out core orbitals
    valence_config = []
    electron_count = 0

    for n, orb, count in config:
        electron_count += count
        if electron_count > core_electrons:
            # This orbital is partially or fully in valence
            if electron_count - count < core_electrons:
                # Orbital straddles core/valence boundary (shouldn't happen with proper noble gas cores)
                valence_config.append((n, orb, count))
            else:
                # Orbital is fully in valence
                valence_config.append((n, orb, count))

    core_symbol = NOBLE_GASES[core_Z]
    valence_str = _format_config(valence_config)

    if valence_str:
        return f"[{core_symbol}] {valence_str}"
    else:
        return f"[{core_symbol}]"


def count_valence(config: str) -> int:
    """
    Count valence electrons from electron configuration string.

    Valence electrons are those in the outermost shell (highest n).
    For main group elements, this is simply ns + np electrons.
    For transition metals, only the outermost ns electrons are counted as valence
    (though d electrons participate in bonding, they are not typically counted
    as valence for group classification purposes).

    Physical significance: Valence electrons determine group number and
    primary chemical behavior. Elements in the same group have the same
    valence electron count.

    Args:
        config: Electron configuration string (e.g., "[He] 2s2 2p2" or "1s2 2s2 2p6")

    Returns:
        Number of valence electrons (outermost shell only)

    References:
    - Pauling, L. (1960). The Nature of the Chemical Bond, 3rd ed.
    - Petrucci et al. (2016). General Chemistry: Principles and Modern Applications
    - IUPAC Gold Book: Definition of valence electrons

    Examples:
        >>> count_valence("[He] 2s2 2p2")  # Carbon
        4
        >>> count_valence("[Xe] 4f14 5d10 6s1")  # Gold
        1
        >>> count_valence("[Ar] 3d10 4s2")  # Zinc
        2
    """
    # Remove noble gas core notation
    if '[' in config:
        config = config.split(']')[1].strip()

    # Parse orbital occupations
    import re
    pattern = r'(\d+)([spdfg])(\d+)'
    matches = re.findall(pattern, config)

    if not matches:
        return 0

    # Find highest n (principal quantum number)
    max_n = max(int(match[0]) for match in matches)

    # Count electrons in highest n shell only (ns + np)
    # This follows the standard definition used for group classification
    valence = 0
    has_s_electrons = False

    for n_str, orbital, count_str in matches:
        n = int(n_str)
        count = int(count_str)
        orbital_type = orbital

        if n == max_n:
            valence += count
            if orbital_type == 's':
                has_s_electrons = True

    # Special case: If highest n has only d/f electrons (no s), valence = 0
    # This handles elements like Pd ([Kr] 4d10) where d is the highest orbital
    # but chemically it behaves as having 0 valence electrons for group purposes
    if not has_s_electrons and max_n > 0:
        # Check if there are s or p electrons at all in highest shell
        has_sp_in_max_n = any(
            int(n_str) == max_n and orbital in ['s', 'p']
            for n_str, orbital, _ in matches
        )
        if not has_sp_in_max_n:
            return 0

    return valence


def orbital_type(config: str) -> str:
    """
    Determine the highest occupied orbital type (s, p, d, f, g).

    This determines the element's block in the periodic table:
    - s-block: Groups 1-2 (alkali and alkaline earth metals)
    - p-block: Groups 13-18 (post-transition metals, metalloids, nonmetals, noble gases)
    - d-block: Groups 3-12 (transition metals)
    - f-block: Lanthanides and actinides
    - g-block: Period 8 superheavy elements (Z>118, theoretical)

    Args:
        config: Electron configuration string

    Returns:
        Orbital type: 's', 'p', 'd', 'f', or 'g'

    Examples:
        >>> orbital_type("[He] 2s2 2p2")  # Carbon
        'p'
        >>> orbital_type("[Xe] 4f14 5d10 6s1")  # Gold
        's'
        >>> orbital_type("[Ar] 3d5 4s2")  # Manganese
        'd'
    """
    # Remove noble gas core
    if '[' in config:
        config = config.split(']')[1].strip()

    # Find last occupied orbital
    import re
    pattern = r'(\d+)([spdfg])(\d+)'
    matches = re.findall(pattern, config)

    if not matches:
        return 's'  # Default for noble gases

    # Return the orbital type of the last occupied orbital
    return matches[-1][1]
