# Bonding Rules Architecture: Level 0 → Level 1

**Date**: 2025-11-23
**Goal**: Design minimal interface for bond formation prediction from atomic properties
**Question**: Can the hierarchical LUT approach deliver fast chemical discovery?

---

## The Core Challenge

**Level 0** gives us individual atoms with properties (valence, electronegativity, radius).
**Level 1** needs to predict: Can atoms A and B form a stable bond? What type? How strong?

This is the **composition rule** that connects hierarchies:
- Input: Two Element objects from Level 0
- Output: Bond prediction with confidence
- Constraint: Must be fast (O(1) property lookups, no expensive calculations)

---

## Question 1: What Properties Are Needed for Bonding?

### From First Principles: Why Do Atoms Bond?

Atoms bond to achieve **lower energy states**, typically by:
1. **Filling valence shells** (octet rule: 8 electrons, or duet for H/He)
2. **Balancing charge** (electronegativity differences drive electron sharing/transfer)
3. **Minimizing repulsion** (atomic radii determine orbital overlap)

### Required Properties from Element Dataclass

Currently available:
- ✅ `valence_electrons` - Determines bonding capacity
- ❌ `electronegativity` - Determines bond polarity (MISSING - need to add)
- ❌ `atomic_radius` - Affects bond strength (MISSING - need to add)
- ❌ `oxidation_states` - Common oxidation states (MISSING - need to add)

**Critical gap**: We have electron configuration but lack derived chemical properties!

### Properties We Need to Add (Phase 2.5)

1. **Electronegativity (Pauling scale)**
   - Purpose: Determine if bond is covalent (ΔEN < 0.5), polar covalent (0.5-1.7), or ionic (>1.7)
   - Source: NIST/Pauling values for Z≤118, extrapolation for Z>118
   - Confidence: High for observed, decreasing for theoretical

2. **Covalent Radius**
   - Purpose: Estimate bond length (R_AB = r_A + r_B)
   - Source: Pyykkö covalent radii database
   - Confidence: High for measured, medium for extrapolated

3. **Oxidation States**
   - Purpose: Predict common bonding configurations
   - Source: Inferred from valence + periodic table position
   - Confidence: High for common states, medium for unusual states

### Property Priority for Minimal Implementation

**Phase 2.5 (minimal bonding)**:
- Valence electrons (already have)
- Electronegativity (add)

**Phase 3 (enhanced bonding)**:
- Covalent radius (add)
- Oxidation states (add)
- Ionization energy (add)

---

## Question 2: Simplest Bonding Rules

### Rule-Based Approach (vs. ML)

For a **minimal viable interface**, use physics-based rules (not ML):
- ✅ Explainable: "Bond forms because ΔEN=0.9 suggests polar covalent"
- ✅ Fast: O(1) property lookups, simple arithmetic
- ✅ Trustable: Confidence propagates from input properties
- ✅ No training data needed

### Rule 1: Octet Rule (Valence Matching)

**Principle**: Atoms bond to achieve full valence shells (8 electrons, or 2 for H/He)

```python
def satisfies_octet(elem_a: Element, elem_b: Element) -> bool:
    """
    Check if atoms can share electrons to satisfy octet rule.

    Examples:
        C (4 valence) + O (6 valence) → can share 4 electrons → satisfies
        H (1 valence) + H (1 valence) → can share 2 electrons → satisfies
        He (2 valence) + Ne (8 valence) → both satisfied → no bonding needed
    """
    target_a = 2 if elem_a.atomic_number <= 2 else 8
    target_b = 2 if elem_b.atomic_number <= 2 else 8

    available_a = target_a - elem_a.valence_electrons
    available_b = target_b - elem_b.valence_electrons

    # Can they share electrons to fill both?
    return available_a > 0 and available_b > 0
```

**Limitations**:
- Doesn't handle transition metals well (d-orbital bonding)
- Doesn't predict bond order (single vs. double vs. triple)
- Doesn't account for electronegativity

### Rule 2: Electronegativity Difference

**Principle**: ΔEN determines bond character

| ΔEN Range | Bond Type | Example |
|-----------|-----------|---------|
| 0.0 - 0.4 | Nonpolar covalent | H-H, C-C |
| 0.5 - 1.6 | Polar covalent | C-O, C-N |
| 1.7+ | Ionic | Na-Cl, Mg-O |

```python
def classify_bond_type(elem_a: Element, elem_b: Element) -> str:
    """
    Classify bond as covalent, polar covalent, or ionic.

    Uses Pauling electronegativity scale.
    """
    delta_en = abs(elem_a.electronegativity - elem_b.electronegativity)

    if delta_en < 0.5:
        return "nonpolar_covalent"
    elif delta_en < 1.7:
        return "polar_covalent"
    else:
        return "ionic"
```

### Rule 3: Chemical Intuition (Heuristics)

**Noble gases don't bond** (valence shell full):
- He, Ne, Ar, Kr, Xe, Rn, Og → valence = 8 (or 2 for He)

**Metals + Nonmetals → Ionic**:
- Na (metal) + Cl (nonmetal) → NaCl (ionic)

**Nonmetals + Nonmetals → Covalent**:
- C + H → CH₄ (covalent)
- N + O → NO₂ (covalent)

### Combined Minimal Bonding Algorithm

```python
def can_bond(elem_a: Element, elem_b: Element) -> BondPrediction:
    """
    Minimal bonding prediction using valence and electronegativity.

    Steps:
    1. Check if both elements want to bond (not noble gases)
    2. Check electronegativity difference for bond type
    3. Check valence compatibility for bond formation
    4. Return prediction with confidence
    """
    # Step 1: Noble gas check
    if is_noble_gas(elem_a) or is_noble_gas(elem_b):
        return BondPrediction(
            can_bond=False,
            bond_type="none",
            reasoning="Noble gas with full valence shell"
        )

    # Step 2: Electronegativity-based classification
    bond_type = classify_bond_type(elem_a, elem_b)

    # Step 3: Valence compatibility
    can_form_bond = satisfies_octet(elem_a, elem_b)

    # Step 4: Confidence propagation (see Question 3)
    confidence = compute_bond_confidence(elem_a, elem_b, bond_type)

    return BondPrediction(
        can_bond=can_form_bond,
        bond_type=bond_type,
        confidence=confidence,
        reasoning=f"ΔEN={abs(elem_a.electronegativity - elem_b.electronegativity):.2f}"
    )
```

**What This Doesn't Handle (Future Work)**:
- Bond order (single vs. double vs. triple)
- Coordinate covalent bonds (Lewis acids/bases)
- Metallic bonding
- Hydrogen bonding
- Van der Waals forces
- Resonance structures
- Molecular geometry (VSEPR)

**Why This Is Sufficient for Minimal Demo**:
- Predicts C-H, C-C, C-O, C-N bonds (organic chemistry backbone)
- Predicts Na-Cl, Mg-O ionic bonds
- Rejects He-He, Ne-Ne (noble gases)
- Fast: O(1) property lookups

---

## Question 3: Confidence Propagation from Level 0 → Level 1

### The Confidence Propagation Problem

Given:
- Element A with confidence scores: `{config: 1.0, electronegativity: 0.95}`
- Element B with confidence scores: `{config: 1.0, electronegativity: 0.90}`

What is the confidence in the **bond** A-B?

### Option 1: Minimum Confidence (Conservative)

**Logic**: A bond is only as reliable as the LEAST reliable property used to predict it.

```python
def bond_confidence_min(elem_a: Element, elem_b: Element, properties_used: List[str]) -> float:
    """
    Conservative: Take minimum confidence across all properties.

    Example:
        Properties used: ["electronegativity", "valence_electrons"]

        Confidences:
            elem_a.conf["electronegativity"] = 0.95
            elem_b.conf["electronegativity"] = 0.90
            elem_a.conf["electron_configuration"] = 1.0
            elem_b.conf["electron_configuration"] = 1.0

        Per-property confidence:
            electronegativity: min(0.95, 0.90) = 0.90
            valence (from config): min(1.0, 1.0) = 1.0

        Overall bond confidence: min(0.90, 1.0) = 0.90
    """
    confidences = []
    for prop in properties_used:
        conf_a = elem_a.confidence.get(prop, 0.0)
        conf_b = elem_b.confidence.get(prop, 0.0)
        confidences.append(min(conf_a, conf_b))

    return min(confidences)
```

**Pros**:
- ✅ Conservative (safe for critical applications)
- ✅ Simple to implement
- ✅ Interpretable: "Bond confidence limited by least reliable input"

**Cons**:
- ❌ May be overly pessimistic
- ❌ One bad property tanks entire prediction

---

### Option 2: Product Confidence (Probabilistic)

**Logic**: If properties are independent, confidence multiplies.

```python
def bond_confidence_product(elem_a: Element, elem_b: Element, properties_used: List[str]) -> float:
    """
    Probabilistic: Multiply confidences assuming independence.

    Example:
        Same as above, but:

        Overall = 0.90 × 1.0 = 0.90
    """
    confidence = 1.0
    for prop in properties_used:
        conf_a = elem_a.confidence.get(prop, 0.0)
        conf_b = elem_b.confidence.get(prop, 0.0)
        # For each property, take min of (A, B), then multiply
        confidence *= min(conf_a, conf_b)

    return confidence
```

**Pros**:
- ✅ Statistically principled (if properties are independent)
- ✅ Degrades gracefully with more uncertain properties

**Cons**:
- ❌ Assumes independence (may not hold - e.g., valence and electronegativity are correlated)
- ❌ Confidence drops quickly with many properties

---

### Option 3: Weighted Average (Balanced)

**Logic**: Some properties matter more than others for bonding.

```python
def bond_confidence_weighted(elem_a: Element, elem_b: Element, weights: Dict[str, float]) -> float:
    """
    Weighted average based on property importance.

    Example:
        weights = {
            "electronegativity": 0.7,  # Very important for bond type
            "valence_electrons": 0.3    # Less critical if EN is known
        }

        Overall = 0.7 × 0.90 + 0.3 × 1.0 = 0.63 + 0.3 = 0.93
    """
    total_weight = sum(weights.values())
    weighted_conf = 0.0

    for prop, weight in weights.items():
        conf_a = elem_a.confidence.get(prop, 0.0)
        conf_b = elem_b.confidence.get(prop, 0.0)
        prop_conf = min(conf_a, conf_b)
        weighted_conf += (weight / total_weight) * prop_conf

    return weighted_conf
```

**Pros**:
- ✅ Flexible (can tune weights based on chemistry knowledge)
- ✅ Less pessimistic than minimum
- ✅ Captures relative importance

**Cons**:
- ❌ Requires domain knowledge to set weights
- ❌ More complex to explain

---

### Recommendation: **Minimum Confidence (Option 1)**

**Rationale**:
1. **Simplicity**: Easy to implement and explain
2. **Safety**: Conservative is appropriate for scientific predictions
3. **Consistency**: Matches how we think about reliability (weakest link)
4. **Interpretability**: Users can see exactly which property limits confidence

**Implementation**:

```python
class BondPrediction:
    can_bond: bool
    bond_type: str  # "nonpolar_covalent", "polar_covalent", "ionic", "none"
    confidence: float  # Overall prediction confidence
    confidence_breakdown: Dict[str, float]  # Per-property confidence
    reasoning: str

def compute_bond_confidence(elem_a: Element, elem_b: Element, bond_type: str) -> tuple[float, Dict]:
    """
    Compute bond prediction confidence using minimum rule.

    Returns:
        (overall_confidence, confidence_breakdown)
    """
    # Properties used depend on bond type
    if bond_type == "none":
        # No bond, only used valence check
        properties_used = ["electron_configuration"]
    else:
        # Bonding prediction uses both valence and electronegativity
        properties_used = ["electron_configuration", "electronegativity"]

    breakdown = {}
    for prop in properties_used:
        conf_a = elem_a.confidence.get(prop, 0.0)
        conf_b = elem_b.confidence.get(prop, 0.0)
        breakdown[prop] = min(conf_a, conf_b)

    overall = min(breakdown.values())

    return overall, breakdown
```

**Confidence interpretation**:

| Confidence | Interpretation | Use Case |
|------------|---------------|----------|
| 1.0 | Experimental data for both elements | Production chemistry |
| 0.8-1.0 | High confidence, well-understood | Research predictions |
| 0.5-0.8 | Medium confidence, theoretical | Exploratory screening |
| < 0.5 | Low confidence, speculative | Hypothesis generation only |

---

## Architecture Design

### Data Flow

```
Level 0 (Elements)
    ↓
    Element A (properties + confidence)
    Element B (properties + confidence)
    ↓
Level 1 (Bonding Rules)
    ↓
    can_bond(A, B) → BondPrediction
    ↓
    {
        can_bond: true,
        bond_type: "polar_covalent",
        confidence: 0.95,
        confidence_breakdown: {
            "electron_configuration": 1.0,
            "electronegativity": 0.95
        }
    }
    ↓
Level 2 (Molecules)
    [Future: Use bonds to build molecular structures]
```

### API Design

```python
# Level 1 bonding module: src/level1/bonding.py

from src.core.element import Element
from dataclasses import dataclass
from typing import Dict

@dataclass
class BondPrediction:
    """Prediction of bond formation between two elements."""
    can_bond: bool
    bond_type: str  # "nonpolar_covalent" | "polar_covalent" | "ionic" | "none"
    confidence: float  # Overall confidence (0.0 to 1.0)
    confidence_breakdown: Dict[str, float]  # Per-property confidence
    reasoning: str  # Human-readable explanation

    # Optional (for future):
    bond_order: int = 1  # 1=single, 2=double, 3=triple
    bond_length_estimate: float = None  # Estimated bond length in pm
    bond_energy_estimate: float = None  # Estimated bond energy in kJ/mol


class BondingRules:
    """
    Stateless bonding prediction using Level 0 element properties.

    This class implements composition rules: Level 0 → Level 1
    """

    @staticmethod
    def can_bond(elem_a: Element, elem_b: Element) -> BondPrediction:
        """
        Predict if two elements can form a stable bond.

        Args:
            elem_a: First element (from ElementGenerator)
            elem_b: Second element (from ElementGenerator)

        Returns:
            BondPrediction with confidence score

        Examples:
            >>> from src.theory.generator import ElementGenerator
            >>> gen = ElementGenerator()
            >>> c = gen.generate(6)  # Carbon
            >>> h = gen.generate(1)  # Hydrogen
            >>>
            >>> bond = BondingRules.can_bond(c, h)
            >>> bond.can_bond
            True
            >>> bond.bond_type
            'polar_covalent'
            >>> bond.confidence
            0.95
        """
        pass

    @staticmethod
    def is_noble_gas(elem: Element) -> bool:
        """Check if element is a noble gas (full valence shell)."""
        pass

    @staticmethod
    def classify_bond_type(elem_a: Element, elem_b: Element) -> str:
        """Classify bond type based on electronegativity difference."""
        pass

    @staticmethod
    def satisfies_octet(elem_a: Element, elem_b: Element) -> bool:
        """Check if bonding satisfies octet rule."""
        pass
```

---

## Performance Validation

### Speed Test Goals

To validate "orders of magnitude speedup":

**Naive approach**: Try all pairs of elements
- 118 elements × 118 elements = 13,924 pairs
- If each bond check is O(1) with property lookups
- Target: < 1ms per bond check → ~14 seconds total

**Optimized approach**: Pre-filter impossible bonds
- Noble gases: 7 elements never bond → eliminate 7×118 + 118×7 = 1,652 pairs
- Remaining: 13,924 - 1,652 = 12,272 pairs
- Target: < 10 seconds for all-pairs bonding table

**Comparison to brute force**:
- Brute force: Quantum chemistry calculations (seconds to hours per bond)
- LUT approach: Property lookups + simple rules (milliseconds per bond)
- **Speedup**: 10³ to 10⁶ times faster

### Success Criteria

✅ Can predict C-H, C-C, C-O, C-N bonds (organic chemistry)
✅ Can predict Na-Cl, Mg-O ionic bonds
✅ Rejects He-He, Ne-Ne (noble gases)
✅ Confidence propagates correctly from Level 0
✅ All-pairs bonding table for Z=1-118 in < 15 seconds

---

## Implementation Plan

### Phase 2.5: Add Electronegativity to Element

**Goal**: Add the missing electronegativity property

1. **Add to Element dataclass**:
   ```python
   electronegativity: Optional[float] = None
   ```

2. **Add to ConfidenceScorer**:
   - Already have `electronegativity_confidence(Z)` ✓

3. **Add to ElementGenerator**:
   - Implement `_compute_electronegativity(Z)` using Pauling scale
   - For Z≤118: Load from database or calculate from known values
   - For Z>118: Extrapolate from group trends

4. **Update tests**:
   - Validate electronegativity for H, C, O, Na, Cl

### Phase 3: Implement BondingRules

**Goal**: Implement minimal bonding prediction

1. **Create `src/level1/bonding.py`**:
   - `BondPrediction` dataclass
   - `BondingRules` class with static methods
   - Implement `can_bond()`, `classify_bond_type()`, etc.

2. **Create tests**:
   - Test C-H bond (polar covalent)
   - Test Na-Cl bond (ionic)
   - Test He-He (no bond)
   - Test confidence propagation

3. **Performance benchmark**:
   - All-pairs bonding table (118×118)
   - Measure time and validate < 15 seconds

---

## Open Questions for You

1. **Electronegativity data source**:
   - Should I use hardcoded Pauling values for common elements?
   - Or scrape from a database (PubChem, Wikipedia)?
   - Or use an existing Python library for quick implementation?

2. **Confidence threshold for bonding**:
   - Should we reject bonds if confidence < 0.5?
   - Or return the prediction with a warning?
   - Different thresholds for different applications (materials vs drugs)?

3. **Scope of minimal demo**:
   - Just predict "can bond: yes/no" with confidence?
   - Or also predict bond type (covalent/ionic)?
   - Or go further and predict bond order (single/double/triple)?

4. **Performance baseline**:
   - What's the acceptable time for all-pairs bonding table?
   - 1 second? 10 seconds? 1 minute?

---

## Next Steps

After your feedback, I'll implement:
1. Phase 2.5: Add electronegativity to Element generation
2. Phase 3: Implement BondingRules with minimal algorithm
3. Validation: Test against known bonds (C-H, Na-Cl, etc.)
4. Performance: Benchmark all-pairs bonding table

This will demonstrate that the hierarchical LUT approach **actually works** for fast chemical discovery!
