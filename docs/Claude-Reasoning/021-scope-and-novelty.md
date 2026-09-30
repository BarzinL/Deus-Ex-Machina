# Scope and Novelty: What the Framework Can and Cannot Claim

**Date**: 2026-09-30
**Status**: Position document. The novelty claims in section 4 are **unverified**; they rest on two quick literature searches, not a review.

---

## 1. The Complexity Claim

**Old claim**: LUT composition turns O(N^k) search into O(N×k) lookup.

**Why it doesn't hold as stated**:
- Lookup is O(1) only for things already in a table.
- Discovery means building candidates that are *not* in the table. Choosing k primitives from a table of size N is still a combinatorial search. It is smaller than a search over raw components, because the table only holds valid primitives, but it is not linear.
- Every non-additive interaction between primitives needs either a correction term or a new cached unit. The table grows with the number of such interactions.

**Supportable claim**: composition from validated primitives shrinks the search space. The size of the reduction depends on (a) how many candidates the composition rules exclude and (b) how often additivity holds. Neither has been measured in this repo.

---

## 2. Retrospective vs Prospective Boundary Detection

`CrystallizationDetector.measure_additivity_violation(structure, naive_fn, actual_value)` takes the true value as an argument. The violation is `actual − naive`.

**Consequence**: to flag benzene as a boundary, you need benzene's measured heat of formation. For an unmeasured molecule, the detector has nothing to compare against and says nothing.

Chemists found aromaticity and ring strain the same way: measure, compare with an additive estimate, notice the residual. The detector automates the *noticing*, not the *predicting*.

The structural features (`has_resonance`, cycle count, conjugation score) are hand-written and only feed the explanation text. They don't predict the violation's size.

**What a prospective detector would need**:
- A model `f(structure) → predicted residual`, trained on measured cases.
- Evaluation on **held-out** structures, including sign and size of the residual.
- Comparison with existing baselines that already predict residuals: group additivity with ring/aromatic corrections, and Δ-learning (Ramakrishnan et al., *J. Chem. Theory Comput.* 2015, 11:2087, PMID 26574412).

This slot is crowded in chemistry. Automatic discovery of context-dependent group contributions (CARGO, Bielefeld) and ML-corrected group additivity already exist.

---

## 3. Hierarchy Does Not Imply Additivity

**Hierarchy** means a whole is made of parts. **Additivity** means the whole's property ≈ Σ parts' properties + small corrections. The first is almost always true. The second is an empirical question for each property and domain.

| Domain | Parts | Is the additive estimate close? |
|---|---|---|
| Gas-phase thermochemistry | Bonds / groups | Yes: residuals are a few % (benzene +203 of 5525 kJ/mol, 3.7%) |
| Protein function | Residues / mutations | Often no: epistasis. Two individually neutral mutations can together abolish function |
| Drug–target binding | Fragments | Partial: fragment contributions interact through conformation and solvation |
| Drug combinations | Single drugs | Mostly yes: synergy is reported in only ~1.5–3.6% of screened pairs (ALMANAC / O'Neil, per a 2024 bioRxiv active-learning guide). The rare exceptions are what matter |
| Combined longevity interventions | Single interventions | Open: superposition models predicting combined survival curves from single ones have been tested in *C. elegans* (bioRxiv 2020) |

**Implication**: a lookup table of parts is useful exactly where the right-hand column says "yes". The detector's value is measuring which regime a system is in. In a regime dominated by interactions, a table of parts predicts little, and the table of *interactions* is the combinatorial object you were trying to avoid.

The drug-combination row cuts the other way from what one might expect. Mostly additive, with rare, high-value exceptions, is the regime where "assume additive, measure only where it probably fails" pays off most.

---

## 4. Where Novelty Could Be (Unverified)

Ranked by likely impact against how crowded the field is.

### 4.1 Hierarchical experiment design for combinations of interventions (most promising)

**Setting**: interventions (drugs, genetic perturbations, senolytics) whose combinations are too many to test exhaustively. Examples: pairs, triples and beyond, measured by lifespan, senescent-cell clearance, or cell viability.

**What exists** (from the searches): active learning over drug *pairs* for synergy, and predicting *pair* outcomes from single-intervention survival curves.

**What this framework would add**:
1. Treat additive (or Bliss/superposition) prediction as the naive model.
2. Use a learned residual predictor to choose which combinations to measure (prospective, section 2).
3. **Promote** confirmed non-additive combinations to cached units, and use them as primitives at the next level. Triples are built from validated pairs, not from singles.
4. Recurse.

Step 3 is the LUT hierarchy applied to experiment selection. I have not seen it stated as such in the pieces found, but two searches are not a literature review. This must be checked before any claim of novelty.

**Falsifiable test**: on a public combinatorial dataset (e.g. DrugComb, or the *C. elegans* four-intervention lifespan data), compare hierarchical promotion with flat active learning. Measure how many experiments each needs to recover the top-k higher-order combinations. If hierarchical promotion does no better, the LUT idea adds nothing in this setting.

### 4.2 Verified-abstraction discipline for LLM research agents

The repo already contains a documented case study: fabricated values, their detection (017–019), and an error the verification pass missed (020). A method and benchmark for catching this class of error could be useful, and it is what the project's recent direction points at. Research on evaluating AI-scientist agents is active, so novelty here also needs checking.

### 4.3 Prospective residual prediction in chemistry (least promising as novelty)

This is useful as a testbed, because ground truth is cheap and trustworthy. It is unlikely to be novel given group additivity, CARGO and Δ-learning.

### 4.4 "Universal framework" (not a contribution on its own)

The general pattern is established. Claiming it without a domain-specific result that beats existing methods will not hold up in review.

---

## Sources

- Benson, S.W. & Buss, J.H., *J. Chem. Phys.* 1958, 29:546 (group additivity; cited from memory, not re-fetched)
- Ramakrishnan, R. et al., *J. Chem. Theory Comput.* 2015, 11:2087, PMID 26574412 (Δ-learning)
- Generic Context-Aware Group Contributions (CARGO): https://pub.uni-bielefeld.de/record/2987396
- A Guide for Active Learning in Synergistic Drug Discovery, bioRxiv 2024: https://www.biorxiv.org/content/10.1101/2024.09.13.612819
- Superposition of lifespan interventions in *C. elegans*, bioRxiv 2020: https://dx.doi.org/10.1101/2020.04.22.054767
