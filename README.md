# Deus Ex Machina

**Research framework exploring hierarchical lookup table (LUT) composition for scientific discovery, and where it breaks down.**

[![License: Dual (AGPLv3/Commercial)](https://img.shields.io/badge/License-Dual%20(AGPLv3%2FCommercial)-blue.svg)](#license)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![DOI/Zenodo](https://zenodo.org/badge/DOI/10.5281/zenodo.17746013.svg)](https://doi.org/10.5281/zenodo.17746013)
---

## Vision

Reality has natural hierarchical structure:
- **Physics**: particles → atoms → molecules → materials
- **Biology**: amino acids → proteins → cells → tissues
- **Engineering**: components → circuits → systems

**Core Hypothesis**: If we:
1. Identify hierarchical levels in a domain
2. Cache primitives at each level as LUTs
3. Define composition rules between levels
4. Search at appropriate abstraction

Then: the search space shrinks, because candidates are built from cached, pre-validated parts instead of simulated from scratch.

How much it shrinks is **not yet measured** here. It depends on how many candidates the composition rules exclude, and on how often the additive assumption holds in the domain (see [Scope and limits](#scope-and-limits)).

### The Architectural Pattern

By identifying "compositional boundaries" (points where a system behaves as a stable unit), complex structures can be cached as primitives and reused at the next level up. Lookup replaces recomputation for anything already in a table. Composing primitives into *new* candidates is still a combinatorial search; it is smaller than a search over raw components, but not eliminated.

Key component: **The Crystallization Detector**. It compares a naive additive prediction against a measured or computed value and reports the residual (the "additivity violation"). A large residual means the structure should be cached as a unit, not decomposed.

The detector is **retrospective**: it needs the true value as input, so it can only classify structures that have already been measured or computed. Predicting where additivity will fail *before* measuring is the open problem this project is aimed at; it is not solved here.

### Explained accessibly:

The basic idea is that reality has a natural hierarchy that can be represented in a sparse way.

For example: the periodic table of atomic elements has distinct properties. The standard model of elementary particles is made of discrete units. Molecular compounds are made of distinct subunits. So too are organisms made of organ systems, organs made of tissues, tissues of cells which are made of organelles, and so on. Even computer systems are made of components, subcomponents, and raw materials. This is an exploitable pattern.

At every scale, from the planck scale to the macro scale, stable systems "crystallize" into composable parts. When you identify these boundaries (where things like feedback loops or constraints create stability) and then cache them into lookup tables, that can empower you to transform search problems.

Rather than simulating every atom's interaction, we compose pre-validated, stable primitives, and only traverse physically/chemically valid branches of the tree. That tames the combinatorial explosion somewhat. It does not remove it: combining primitives is still a search, and every place where the parts interact non-additively needs a correction or a new cached unit.

Paired with a smart querying program hooked into an LLM using it for tool-calling, you can create an inverse design funnel for whatever, where you just say *"find me a PCB design that has better heat dissipation than conventional FR-4 fiberglass PCBs"* and it will flip through its materials lookup table and find things with better heat dissipation, and then chain those candidates into its manufacturing lookup table to find how to build it.

The ideal is to use this to transform search problems into inverse design funnels for any domain, from materials science to engineering. The hope is to push this into biology for disease treatment.

---

## Motivating Example

A private experiment on a machine learning model called NGL-1 used a hierarchical LUT tokenizer that stored 1.1M+ UTF-8 codepoints in 4.4MB, decoupling token embeddings from conceptual space. This motivated the project; it is unpublished and is not evidence that the approach generalizes to physical or biological systems.

---

## Scope and Limits

**Hierarchy does not imply additivity.** Everything above assumes a whole can be predicted from its parts plus a small number of corrections. Hierarchical structure is common; small corrections are not guaranteed.

- **Where additivity mostly holds:** gas-phase thermochemistry of organic molecules. Group additivity methods predict heats of formation from cached group values plus ring and aromaticity corrections.
- **Where it often fails:** interacting parts whose effect depends on context. Examples include epistasis between mutations in a protein, drug synergy and antagonism, binding affinity, and tissue-level effects of combined interventions. Here the "correction" terms can be as large as the additive terms, and a lookup table of parts predicts little.

The detector's job is to measure which regime a system is in. It does not make a non-additive domain additive.

**Prior art.** The core pattern (cache parts, compose, correct where composition fails) is established:
- Benson group additivity for thermochemistry (Benson & Buss, *J. Chem. Phys.* 1958, 29:546)
- Automatic discovery of context-dependent group contributions, e.g. [CARGO](https://pub.uni-bielefeld.de/record/2987396)
- Δ-learning: ML models trained to predict the residual of a cheap baseline (Ramakrishnan et al., *J. Chem. Theory Comput.* 2015, 11:2087)
- Active learning for synergistic drug combinations ([guide, bioRxiv 2024](https://www.biorxiv.org/content/10.1101/2024.09.13.612819.full.pdf))
- Predicting lifespan effects of combined interventions from single-intervention survival curves in *C. elegans* ([bioRxiv 2020](https://dx.doi.org/10.1101/2020.04.22.054767))

What this project can add is covered in `docs/Claude-Reasoning/021-scope-and-novelty.md`.

---

### Validation Status

Early results on a 9-molecule benchmark (mean-bond-enthalpy baseline, atomization energies from NIST heats of formation):
- **Aromaticity:** Benzene shows a +203 kJ/mol violation (3.7% of total bond energy). At the current 5% threshold the detector classifies it as "uncertain", not "must cache"; only cyclobutadiene (−237 kJ/mol) crosses the threshold.
- **Control case:** Ethylene shows ~0 violation (−1 kJ/mol).
- **Known limitation:** Mean bond enthalpies ignore hybridization, so acyclic conjugated molecules (butadiene +38, hexatriene +74) and even non-aromatic cyclooctatetraene (+84) show positive violations that are partly baseline error. A homodesmotic or group-additivity baseline is needed before interpreting ratios between molecules.
- **Correction (2026-09-30):** An earlier "diminishing returns in fused rings" result for naphthalene came from a bug in the naive model (invalid Kekulé structure). See `docs/Claude-Reasoning/020-baseline-and-kekule-corrections.md`.

---

## Architecture

### 3-Layer Hierarchy

```
Layer -1: Standard Model (Fundamental Physics)
├─ Elementary particles, forces, conservation laws
├─ QED corrections, nuclear shell model
└─ Composition rules → Level 0

Level 0: Periodic Table (Elements)
├─ 118 observed + 55 theoretical elements (Z=1-173)
├─ Electron configurations, atomic properties
├─ Stability classification (OBSERVED | PREDICTED | SUPERCRITICAL | IMPOSSIBLE)
└─ Composition rules → Level 1

Level 1: Chemical Bonds & Functional Groups
├─ Bond types (covalent, ionic, metallic, hydrogen)
├─ Functional groups (~500-1000 patterns)
├─ Small molecules (<10 atoms)
└─ Composition rules → Level 2

Level 2: Molecular Compounds
├─ Known compounds (~200M in databases)
├─ Properties computed via composition from Level 1
├─ Reaction pathways
└─ Composition rules → Level 3+

Level 3+: Domain-Specific Extensions
├─ Materials (crystals, polymers, composites)
├─ Biological molecules (proteins, DNA, metabolites)
└─ Devices (semiconductors, sensors, actuators)
```

### Current Data Strategy

**Layer 0 (Theory)**: Pure Python functions - generative physics from first principles
- `src/theory/quantum.py` - Electron configurations, valence electrons
- `src/theory/nuclear.py` - Nuclear stability, half-lives (planned)
- `src/theory/qed.py` - QED limits for superheavy elements (planned)

**Layer 1 (Computed Cache)**: JSON snapshots - pre-generated from Layer 0
- `data/computed/{model}/elements.json` - Cached element properties
- `data/computed/{model}/metadata.json` - Confidence scores, model info
- Multiple model support (Pyykkö 2011, Fricke 1971, etc.)

**Layer 2 (Experimental)**: Curated NIST/IUPAC data - ground truth
- `data/experimental/nist_2024.json` - Measured atomic properties
- Always overrides Layer 1 when available

**Query path**: Layer 2 → Layer 1 → Layer 0 (fallback)

---

## Installation

```bash
# Clone repository
git clone https://github.com/BarzinL/Deus-Ex-Machina.git
cd Deus-Ex-Machina

# Create virtual environment with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .
```

---

## Usage

### Generate Electron Configuration

```python
from src.theory.quantum import madelung_rule, count_valence

# Hydrogen
config = madelung_rule(1)  # → "1s1"
valence = count_valence(config)  # → 1

# Carbon
config = madelung_rule(6)  # → "[He] 2s2 2p2"
valence = count_valence(config)  # → 4

# Gold (Madelung exception)
config = madelung_rule(79)  # → "[Xe] 4f14 5d10 6s1"
valence = count_valence(config)  # → 1

# Oganesson (heaviest observed)
config = madelung_rule(118)  # → "[Rn] 5f14 6d10 7s2 7p6"
valence = count_valence(config)  # → 8

# Unbinilium (theoretical, island of stability)
config = madelung_rule(120)  # → "[Og] 8s2"
valence = count_valence(config)  # → 2
```

### Run Tests

```bash
# Full test suite
python -m pytest

# Verbose reports, run as scripts from the repo root
PYTHONPATH=. python tests/validate_comprehensive.py   # 29 key elements
PYTHONPATH=. python tests/test_dataset_analysis.py    # molecule violation table
```

---

## Target Domains

### 1. Materials Science
**Organic semiconductors for desktop fabrication**
- Start: Periodic table → functional groups → molecules → materials
- Constraints: Air-stable, <200°C processing, semiconducting
- Goal: Discover novel materials for low-cost device fabrication

### 2. Drug Discovery
**Senolytics for longevity research**
- Start: Atoms → fragments → drug-like molecules → targets
- Constraints: Selectively toxic to senescent cells
- Goal: Accelerate discovery of anti-aging compounds

---

## Physics References

- **Madelung, E.** (1936). Die Mathematischen Hilfsmittel des Physikers
- **Klechkovskii, V.M.** (1962). Distribution of Atomic Electrons
- **Pyykkö, P.** (2011). A suggested periodic table up to Z≤172. *Phys. Chem. Chem. Phys.* 13, 161
- **Scerri, E.R.** (2013). *Mendeleev to Oganesson*. Oxford University Press
- **Pauling, L.** (1960). *The Nature of the Chemical Bond*, 3rd ed.

---

## License

**Dual License: AGPLv3 or Commercial**

This software is available under a dual-licensing model:

### Open Source License (AGPLv3)
Free for any use, including commercial, as long as you comply with AGPLv3. This software is very copyleft and very free. Derivative works (including modified versions served over a network) must also be open-sourced under AGPLv3.

### Commercial License
Want to use this in proprietary software or keep your modifications closed-source? That requires a commercial license. If you're making money off this work without giving your source back, I deserve a cut.

**Commercial licensing contact:**
- Email: barzin@duck.com
- Web: https://sanctus.ca

### Special Exemptions (60% joke, 40% serious)

The following groups get a free pass because they're either too broke, too cool, or both:

- **Arch Linux users** who compile from source and use i3/sway (bonus points for maintaining AUR packages)
- **Non-binary catgirl hackers** with anime pfps and thigh-highs (you're valid and based)
- **Starving artist INTPs** who chose existential crisis over a stable career (MBTI is cringe but so is capitalism)
- **ThinkPad users** with coffee stains and based stickers

All other filthy normies, corps, and people who unironically use Windows for development: **pay up or face the wrath of strongly-worded AGPLv3 compliance notices.**

*(If you genuinely can't afford a commercial license but need one, email me. I'm not EA.)*

See [LICENSE](LICENSE) for full details.

---

## Contributing

This is a research project. Contributions are welcome, especially:
- Additional theory models (nuclear stability, QED corrections)
- Experimental data curation (NIST, IUPAC, PubChem)
- Domain extensions (materials, drugs, proteins)
- Validation and testing

---

## Contact

**Project**: Deus Ex Machina
**Author**: Barzin L.
**Repository**: https://github.com/BarzinL/Deus-Ex-Machina

---

**"From the machine, scientific discovery."**
