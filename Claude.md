# Deus Ex Machina

## Environment Setup
- Python: use `uv venv` for virtual environments
- Other languages: use appropriate virtual environments
- Avoid Node when possible; use `npx` if necessary

---

## Vision

Universal framework for accelerating scientific discovery through hierarchical lookup table (LUT) composition across domains with hierarchical structure.

This codebase also serves as a platform for generating verified abstractions — discoveries that are grounded in primary sources and tested against empirical data.

---

## Core Hypothesis

Reality has natural hierarchical structure:
- Physics: particles → atoms → molecules → materials
- Biology: amino acids → proteins → cells → tissues
- Engineering: components → circuits → systems

If we:
1. Identify hierarchical levels in a domain
2. Cache primitives at each level as LUTs
3. Define composition rules between levels
4. Search at appropriate abstraction

Then: Orders of magnitude speedup vs. brute force computation.

The boundaries between hierarchical levels correspond to compositional boundaries — points where correlation between components creates stable primitives. Understanding what makes these boundaries real is central to the research.

---

## Epistemic Standards

To ensure our discoveries are genuine rather than artifacts of training data patterns, we apply these standards:

### Source Requirements

Every empirical claim needs:
- **Source**: Primary literature, database (NIST, IUPAC), or flagged as "training data inference"
- **Uncertainty**: Experimental error bounds or computational confidence
- **Type**: Experimental measurement vs. computational result

Source hierarchy (prefer higher):
1. Primary literature with experimental methodology
2. Authoritative databases with citations (NIST, IUPAC, ATcT)
3. Secondary literature (textbooks, reviews)
4. Training data inference (flag explicitly)

### Verification Approach

When investigating a phenomenon:
1. Derive expectations from first principles before looking up data
2. Document predictions separately from lookups
3. When possible, make predictions before checking answers
4. Identify what would falsify the pattern
5. Seek edge cases that could break the pattern

### Abstraction Documentation

When a discovery emerges, document it:

```yaml
abstraction:
  name: "Pattern name"
  derived_from:
    - principle: "First principle"
      source: "Source"
  statement: "Clear statement"
  predictions:
    - case: "Test case"
      prediction: "Expected result"
      made_before_lookup: true/false
      actual_value: "Result"
      source: "Primary source"
      uncertainty: "±X"
  falsifiers:
    - "What would prove this wrong"
  status: "hypothesis / validated / refuted"
```

### Numerical Values Protocol

**For any quantitative claim (energies, temperatures, distances, rates, etc.):**

1. **NEVER generate a numerical value from pattern-matching.** If you don't have a verified source, write `[VALUE NEEDED - source required]` instead of a plausible-sounding number.

2. **Before writing ANY number**, ask:
   - Do I have a specific citation for this exact value?
   - Can I link to the primary source (NIST, journal article, database)?
   - If not, this value must be marked as `[UNVERIFIED]` or left blank.

3. **Plausible ≠ Verified.** The fact that a number "sounds right" or "matches expectations" is not evidence. LLMs are optimized to generate plausible-sounding content.

4. **Control cases first.** Before analyzing complex molecules, verify simple cases where the answer is theoretically known (e.g., ethylene should have ~0 violation). If control cases fail, stop and investigate.

---

## Related Project: NGL-1

DEM connects to NGL-1, a research project on AI architecture. Key points:

- NGL-1 investigates computational primitives required for robust reasoning
- It addresses limitations in current architectures: single-store memory, lack of causal modeling, implicit goal systems
- Verified abstractions from DEM could serve as structured knowledge for systems like NGL-1

Additional context is available in `docs/Claude-Reasoning/NGL-1_Context/` if needed. Ask if anything is unclear.

---

## How to Work

When encountering a design decision:
1. Analyse from first principles
2. Consider multiple approaches
3. Apply epistemic standards (source verification, falsifiability)
4. Ask clarifying questions when needed:
   - Domain expertise
   - Architectural decisions
   - Data sources
   - Context about NGL-1 or broader research goals
5. Document reasoning in `docs/Claude-Reasoning/`
6. Iterate incrementally

If uncertain about something — a source, a claim, the research direction — ask.

---

## Target Domains

1. **Materials science**: Periodic table → functional groups → molecules → materials
   - Constraints: Air-stable, <200°C processing, semiconducting

2. **Drug discovery**: Atoms → fragments → drug-like molecules → targets
   - Constraints: Selectively toxic to senescent cells

3. **Abstraction verification**: Using domains above as test cases to validate the epistemic approach

---

## Physics-First Approach

```
Level -1: Standard Model
├─ Elementary particles (quarks, leptons, bosons)
├─ Fundamental forces (strong, weak, EM, gravity)
├─ Conservation laws
└─ Interaction rules

Level 0: Periodic Table (Atomic)
├─ 118 elements
├─ Electronic structure
├─ Atomic properties
└─ Bonding rules

Level 1: Chemical Bonds & Functional Groups
├─ Bond types (covalent, ionic, metallic, hydrogen)
├─ Common functional groups
├─ Small molecules (<10 atoms)
└─ Composition rules from Level 0

Level 2: Molecular Compounds
├─ Known compounds
├─ Properties computed via composition
├─ Reaction pathways
└─ Thermodynamic data

Level 3+: Domain-Specific Extensions
├─ Materials, biological molecules, devices
└─ New domains as needed
```

---

## Current Research Focus

Investigating what makes molecular configurations "crystallise" into stable compositional primitives.

Working hypothesis: Cycles amplify correlation through feedback loops. Topology matters as much as electron count.

Test cases:
- Benzene (aromatic) — strong positive feedback
- Cyclobutadiene (antiaromatic) — strong negative feedback
- Hexatriene (acyclic conjugated) — weak feedback
- Cyclohexane (cyclic saturated) — geometric feedback only

**Note**: The cyclobutadiene data point (-198 kJ/mol) needs source verification before we proceed. This is the immediate priority.

---

## Data Sources

- Periodic table: NIST, IUPAC
- Compounds: PubChem, ZINC, ChEMBL
- Thermochemistry: NIST Chemistry WebBook, ATcT
- Materials: Materials Project, NOMAD
- Proteins: UniProt, PDB

Always document source, uncertainty, and whether values are experimental or computed.

---

## Success Criteria

- Sub-second search of billions of candidates
- Novel compound discovery through composition
- Generalises to new domains with minimal modification
- 90%+ accuracy vs. full computation
- Abstractions pass verification standards

---

## License

Dual-licensed under AGPLv3 with commercial licenses negotiated separately.

---

## Working Principles

- Iterate incrementally
- Validate early and often
- Document discoveries using the abstraction format
- Ask questions when uncertain
- Verify sources before building on claims
- Prefer simplicity over premature optimisation