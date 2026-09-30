"""Checks on the naive additive baseline, including Kekulé localization."""

import glob
import json
from collections import Counter

import pytest

from src.crystallization.naive import kekule_assignment, naive_bond_energy


def load(name):
    with open(f"data/molecules/{name}.json") as f:
        data = json.load(f)
    return data["atoms"], [tuple(b) for b in data["bonds"]], data["reference_energies"]


@pytest.mark.parametrize("name,expected_doubles", [("benzene", 3), ("naphthalene", 5)])
def test_kekule_is_valid(name, expected_doubles):
    _, bonds, _ = load(name)
    kekule = kekule_assignment(bonds)
    doubles = [k for k, order in kekule.items() if order == 2.0]
    assert len(doubles) == expected_doubles

    # Every aromatic carbon is in exactly one double bond
    counts = Counter(a for k in doubles for a in bonds[k][:2])
    aromatic_atoms = {a for k in kekule for a in bonds[k][:2]}
    assert set(counts) == aromatic_atoms
    assert set(counts.values()) == {1}


def test_no_kekule_structure_raises():
    # Three-membered aromatic ring has an odd number of atoms: no perfect matching
    with pytest.raises(ValueError):
        kekule_assignment([(0, 1, 1.5), (1, 2, 1.5), (2, 0, 1.5)])


@pytest.mark.parametrize("name,expected", [
    ("benzene", 3 * 602 + 3 * 346 + 6 * 413),
    ("naphthalene", 5 * 602 + 6 * 346 + 8 * 413),
    ("ethylene", 602 + 4 * 413),
])
def test_naive_energy(name, expected):
    atoms, bonds, refs = load(name)
    assert naive_bond_energy(atoms, bonds, refs) == expected


@pytest.mark.parametrize("path", sorted(glob.glob("data/molecules/*.json")))
def test_actual_energy_matches_heat_of_formation(path):
    """Where ΔHf is recorded, actual_bond_energy must be its atomization energy."""
    with open(path) as f:
        data = json.load(f)
    energies = data["energies"]
    if "heat_of_formation" not in energies:
        pytest.skip("no ΔHf recorded")
    n = Counter(a["element"] for a in data["atoms"])
    atomization = n["C"] * 716.68 + n["H"] * 218.0 - energies["heat_of_formation"]
    assert abs(energies["actual_bond_energy"] - atomization) < 1.0
