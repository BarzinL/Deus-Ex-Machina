# Baseline Consistency and Kekulé Corrections

**Date**: 2026-09-30
**Status**: Corrections applied; feedback-loop hypothesis downgraded pending a better baseline

---

## Summary

The 019 verification pass declared all 9 molecules verified. A later review found two errors it missed, one in the data and one in the code:

1. **Benzene used a different method from every other molecule.** Its `actual_bond_energy` (5470) was back-computed as naive sum + 148 kJ/mol resonance energy, not derived from a measured heat of formation.
2. **The naive model gave naphthalene an invalid Kekulé structure.** The `atom_i % 2` heuristic assigned 6 C=C bonds to a 10-carbon system that can only have 5. This produced the "+115 kJ/mol, diminishing returns" result.

Both errors passed review because each value looked plausible and carried a citation. The benzene citation (Kistiakowsky 1936) is real, but it measures a different quantity against a different reference.

---

## 1. Benzene

**Method used for the other molecules**: BDE = Σ atomic ΔHf − ΔHf(molecule), with C(g) = 716.68 and H(g) = 218.0 kJ/mol.

**Benzene, same method**:
```
ΔfH°(gas) = 82.9 ± 0.9 kJ/mol   (NIST Chemistry WebBook)
BDE = 6(716.68) + 6(218.0) − 82.9 = 5525.2 kJ/mol
Naive Kekulé (3 C=C, 3 C−C, 6 C−H) = 5322 kJ/mol
Violation = +203 kJ/mol
```

**Source caveat**: NIST WebBook and ATcT were blocked by the network in the verification environment. The 82.9 ± 0.9 value was corroborated through secondary search results only. Per Claude.md, it still needs to be checked against the WebBook entry.

**Why 148 ≠ 203**: the ~150 kJ/mol hydrogenation resonance energy uses cyclohexene (3 × its hydrogenation enthalpy) as the reference. The dataset's violation uses mean bond enthalpies. These are different baselines, and the old entry mixed them.

---

## 2. Naphthalene

| | Old | Corrected |
|---|---|---|
| Naive C=C count | 6 (invalid) | 5 |
| Naive sum | 8646 | 8390 |
| Violation | +115 | **+371 ± 10** |
| Ratio to benzene | 0.78× (vs 148) | 1.83× (vs 203), ~0.91× per ring |

**Fix**: `src/crystallization/naive.py` now finds a Kekulé structure as a perfect matching on the aromatic subgraph. It raises an error when no structure exists, and raises on unknown bond types instead of silently adding 0. `tests/test_naive.py` asserts validity. Both test files that had copies of the old heuristic now use the shared function.

The "diminishing returns with ring fusion" finding in 016/018/019 is **retracted**. It was a code artifact.

---

## 3. Revised Ratios

| Comparison | Old (019) | Corrected |
|---|---|---|
| Benzene / Hexatriene | 2.0× | 2.7× |
| Benzene / Butadiene | 3.9× | 5.3× |
| \|Cyclobutadiene\| / Benzene | 1.6× | 1.2× |
| Benzene / Cyclohexane | 21× | 28× |
| Naphthalene / Benzene | 0.78× | 1.83× |

---

## 4. Open Issue: The Baseline Itself

Adversarial check (Claude.md) on the reference model:

- Mean bond enthalpies ignore hybridization. An sp²–sp² C−C single bond is stronger than the average C−C value. So every conjugated molecule gets a positive violation even without any delocalization effect.
- **Evidence this matters**: cyclooctatetraene is non-aromatic (tub-shaped, localized π bonds), yet it shows +84 kJ/mol. That is about the same size as hexatriene's +74, which the hypothesis treats as the acyclic conjugation signal.
- Ethylene ≈ 0 is partly circular, because the 602 kJ/mol C=C value is itself fitted to ethylene-type data.
- **Consequence**: ratios between molecules (row 1–2 above) mix the effect being measured with reference error of unknown size. They should not be used as evidence for or against "cycles amplify correlation" yet.

**Next step**: re-derive violations against a baseline that cancels hybridization and bond-type effects. Options are homodesmotic reactions or Benson group additivity. Each needs additional sourced ΔfH° values for the reference species (e.g. ethane, propene, trans-2-butene), which must be verified before use.

Also still open:
- **Cyclopropane** `actual_bond_energy` (3401) is "calculated from experimental ring strain energy". That is the same back-computation pattern that broke benzene. It needs a sourced ΔfH°.

---

## Lesson

A citation on a value does not show that the value was derived the same way as its neighbours. The new `test_actual_energy_matches_heat_of_formation` test enforces consistency mechanically for every entry that records ΔfH°. Entries without ΔfH° (currently cyclopropane) are skipped, which marks them as unverified.
