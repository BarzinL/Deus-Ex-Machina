# Deus Ex Machina

**Universal framework for accelerating scientific discovery through hierarchical lookup table (LUT) composition.**

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

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

Then: **Orders of magnitude speedup** vs. brute force computation.

---

## Proven Pattern

A private experiment on a machine learning model called NGL-1 used an innovative tokenizer which achieved **95% memory reduction** (1.1M+ UTF-8 codepoints in 4.4MB) through hierarchical LUT strategy, decoupling token embeddings from conceptual space.

**This same principle should generalize across all domains with hierarchical structure.**

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

### Data Strategy

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

## Current Status

### Phase 1: Complete ✅

**Electron configuration generator (Z=1-173)**:
- Madelung rule implementation with 19 known exceptions
- Handles Cr, Cu, Nb, Mo, Pd, Ag, La, Ce, Gd, Pt, Au, Ac, U, etc.
- Noble gas core notation
- Valence electron counting
- 100% test coverage on 29 key elements

**Features**:
- Observed elements (Z=1-118): Experimentally validated
- Island of stability (Z=119-126): Theoretical predictions
- Supercritical regime (Z=127-172): QED corrections
- Beyond QED limit (Z≥173): Physical impossibility flags

### Phase 2: In Progress 🚧

**ElementGenerator + ConfidenceScorer**:
- Model orchestration (Pyykkö, Fricke, Nefedov)
- Confidence scoring for theoretical predictions
- Element status classification
- Cache generation for Layer 1

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
# Basic tests (H, C, Au, Og, 120)
python tests/test_quantum.py

# Comprehensive validation (29 key elements)
python tests/validate_comprehensive.py
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

**AGPLv3** - "f*** the system, blow the whole thing up"; this software is very copyleft, it's very free, and you're very disallowed from forking it to make money off of it. If you don't like it go code your own better proprietary version from scratch, but since you didn't think of creating this and you weren't going to pay me to make it anyway you can get lost.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, via version 3 of the License.

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
