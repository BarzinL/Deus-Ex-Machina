"""
Naive additive bond-energy model (mean bond enthalpies).

Aromatic bonds (order 1.5) are localized into a valid Kekulé structure before
summing, giving the "cyclohexatriene"-style reference against which
resonance energy is measured.

Limitation: mean bond enthalpies ignore hybridization (e.g. an sp2-sp2 C-C
single bond is stronger than the average C-C value), so violations computed
against this baseline include that reference error, not only conjugation or
strain. See docs/Claude-Reasoning/020-baseline-and-kekule-corrections.md.
"""

from typing import Dict, List, Optional, Sequence, Tuple

Bond = Tuple[int, int, float]


def _is_aromatic(order: float) -> bool:
    return abs(order - 1.5) < 0.01


def kekule_assignment(bonds: Sequence[Bond]) -> Dict[int, float]:
    """
    Assign each aromatic bond an order of 1 or 2 so that every aromatic atom
    takes part in exactly one double bond (a perfect matching of the aromatic
    subgraph).

    Args:
        bonds: (atom_i, atom_j, order) tuples

    Returns:
        Mapping of bond index -> localized order (1 or 2) for aromatic bonds

    Raises:
        ValueError: if no valid Kekulé structure exists
    """
    aromatic = [k for k, (_, _, order) in enumerate(bonds) if _is_aromatic(order)]
    atoms = sorted({a for k in aromatic for a in bonds[k][:2]})
    incident: Dict[int, List[int]] = {a: [] for a in atoms}
    for k in aromatic:
        i, j, _ = bonds[k]
        incident[i].append(k)
        incident[j].append(k)

    matched: Dict[int, int] = {}  # atom -> bond index of its double bond

    def solve() -> bool:
        free = next((a for a in atoms if a not in matched), None)
        if free is None:
            return True
        for k in incident[free]:
            i, j, _ = bonds[k]
            other = j if i == free else i
            if other in matched:
                continue
            matched[free] = matched[other] = k
            if solve():
                return True
            del matched[free], matched[other]
        return False

    if not solve():
        raise ValueError("No valid Kekulé structure for aromatic bonds")

    doubles = set(matched.values())
    return {k: (2.0 if k in doubles else 1.0) for k in aromatic}


def naive_bond_energy(
    atoms: List[dict],
    bonds: Sequence[Bond],
    reference_energies: Dict[str, float],
    kekule: Optional[Dict[int, float]] = None,
) -> float:
    """
    Sum mean bond enthalpies over all bonds (kJ/mol).

    Only C-C, C=C, C#C and C-H are supported; any other bond raises, rather
    than silently contributing zero.
    """
    if kekule is None:
        kekule = kekule_assignment(bonds)

    keys = {
        ('C', 'C', 1.0): 'C-C_single',
        ('C', 'C', 2.0): 'C=C_double',
        ('C', 'C', 3.0): 'C-C_triple',
        ('C', 'H', 1.0): 'C-H',
    }

    total = 0.0
    for k, (i, j, order) in enumerate(bonds):
        order = kekule.get(k, float(order))
        elems = tuple(sorted((atoms[i]['element'], atoms[j]['element'])))
        key = keys.get((*elems, order))
        if key is None or key not in reference_energies:
            raise KeyError(f"No reference energy for {elems[0]}-{elems[1]} order {order}")
        total += reference_energies[key]
    return total
