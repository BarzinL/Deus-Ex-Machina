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

You are graded purely on honesty, conservatism, and error-catching. Elegant grand narratives with weak epistemic grounding count as failure. Boring, deflationary answers with clear limits count as success.

Furthermore, to ensure our discoveries are genuine rather than artifacts of training data patterns, we apply these standards:

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

## Interpretation & Novelty Protocol

For **any** qualitative claim, pattern, or hypothesis derived from verified data, apply this checklist **before** writing conclusions, summaries, or abstractions.

### Pre-Generation Adversarial Check

Before proposing any interpretation, first generate:
- Three ways this pattern could be a restatement of known science
- Two alternative mechanisms that could produce the same data pattern
- One way your reference model choice could be creating an artifact

Only after completing this adversarial step may you proceed to interpretation.

### Required Fields for Any Interpretive Claim

#### 1. Claim Type Classification

Classify every claim using exactly one of these categories:

| Type | Definition | Default Language |
|------|------------|------------------|
| `textbook_rederivation` | Recovering known results using our framework | "Our framework successfully recovers..." |
| `reframing` | Same phenomenon, different vocabulary/perspective | "This is consistent with [X] and can be understood as..." |
| `parameter_estimate` | Quantifying something within known theory | "Within [reference model], we estimate..." |
| `novel_prediction` | Genuinely new, falsifiable claim | "We predict [X], which differs from existing theory in that..." |
| `speculative_metaphor` | Interpretive lens without empirical commitment | "One way to conceptualize this is..." |

**Default to the most conservative type.** Upgrading requires explicit justification.

#### 2. Prior Art Search

Before finalizing any interpretation:
```yaml
prior_art:
  search_terms_used: ["aromaticity", "resonance energy", "Hückel", "..."]
  closest_matches:
    - term: "[known concept]"
      sources: ["[specific textbook/paper]"]
      relationship: "identical" | "substantially_overlapping" | "partially_related" | "distinct"
  if_overlapping: |
    [Explicit statement of how your framing differs, if at all]
```

If `relationship` is "identical" or "substantially_overlapping," you **must** use `textbook_rederivation` or `reframing` as your claim type.

#### 3. Mechanism Decomposition

For any metric or measurement used to support claims:
```yaml
mechanism_decomposition:
  metric_name: "[e.g., bond_additivity_violation]"
  contributing_mechanisms:
    - name: "[mechanism 1]"
      contribution: "known" | "possible" | "unlikely"
      separable: true | false
    - name: "[mechanism 2]"
      # ...
  aggregation_warning: |
    [Required if multiple mechanisms contribute and are not separable]
    "This metric conflates [X, Y, Z]. Single-mechanism interpretations 
    (e.g., 'correlation feedback') are over-attributions without 
    additional analysis to isolate contributions."
```

**You may not attribute a single mechanism to an aggregate metric.**

#### 4. Reference Model Dependence
```yaml
reference_model:
  name: "[e.g., bond-additivity with values X, Y, Z]"
  alternatives_considered: ["isodesmic", "homodesmotic", "BLW", "..."]
  dependence_statement: |
    "The [N×] factor is specific to this reference choice. 
    Under [alternative], the factor would be [different/unknown/similar]."
  invariant_claims: |
    "[Only list claims that survive reference model changes, if any]"
```

**Never describe a quantitative factor as universal without checking alternative references.**

#### 5. Novelty Calibration Statement

Every abstraction must end with an honest novelty summary:
```yaml
novelty_summary:
  claim_type: "[from classification above]"
  what_was_shown: |
    "[Factual statement of what the data demonstrate]"
  relationship_to_known_science: |
    "[How this relates to existing knowledge]"
  what_would_constitute_genuine_novelty: |
    "[What additional evidence would be needed to upgrade claim type]"
```

### Prohibited Patterns

- ❌ Describing pattern recovery as "discovery" without explicit novelty justification
- ❌ Using terms like "amplification," "feedback," "unifying" for reframings of known concepts
- ❌ Attributing aggregate metrics to single mechanisms
- ❌ Presenting reference-model-dependent factors as universal constants
- ❌ Skipping the pre-generation adversarial check

### Enforcement

If any required field is missing or contains placeholder text, the abstraction is **incomplete** and must not be presented as a conclusion.

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