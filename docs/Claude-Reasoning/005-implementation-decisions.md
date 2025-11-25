# Implementation Decisions: Layer 2 Completeness & Layer 0 Organization

**Date**: 2025-11-23
**Context**: Clarifications before implementing 3-layer architecture

---

## Question 1: Layer 2 Completeness for Z=1-118

### The Reality of Experimental Data

Even for observed elements, experimental data completeness varies wildly:

| Property | Coverage (Z=1-118) |
|----------|-------------------|
| Atomic number, symbol, name | 118/118 (100%) |
| Atomic weight | 118/118 (but some ranges for radioactive) |
| Electron configuration | 118/118 (spectroscopic) |
| Melting point | ~100/118 (superheavy = theoretical) |
| Boiling point | ~95/118 (some superheavy never measured) |
| Density | ~105/118 (some only calculated) |
| Electronegativity (Pauling) | ~84/118 (noble gases undefined) |
| Thermal conductivity | ~60/118 (rare/radioactive not measured) |
| Specific heat capacity | ~80/118 |
| Economic data (price, supply) | ~70/118 (no market for radioactive) |
| Political stability of producer | ~70/118 (doesn't apply to lab-made) |

### Options

**Option A: Comprehensive Layer 2**
- Include ALL properties from NIST, even sparse/uncertain ones
- Pros: One-stop shop, no fallthrough logic needed
- Cons: Mixes high-confidence (atomic weight) with low-confidence (Og boiling point?) data

**Option B: Selective Layer 2 (Recommended)**
- Only include high-confidence experimental measurements
- Missing properties → fall through to Layer 1 (computed/extrapolated)
- Pros: Layer 2 is pristine "ground truth", uncertainty explicitly in Layer 1
- Cons: Need fallthrough logic, must decide confidence threshold

**Option C: Property-Specific Rules**
- Core properties (weight, config): Always Layer 2
- Thermal properties: Layer 2 if measured, else Layer 1
- Economic properties: Layer 2 only if market exists
- Pros: Nuanced, realistic
- Cons: Complex rules, harder to maintain

### Recommendation: **Option B (Selective)**

**Rationale**:
1. **Clear semantics**: Layer 2 = "directly measured with high confidence"
2. **Uncertainty tracking**: If it's in Layer 2, confidence = 1.0; if computed, confidence < 1.0
3. **Composability**: Layer 1 can use Layer 2 trends to extrapolate (e.g., thermal conductivity fits)
4. **Future-proof**: When element 120 is discovered, we add measured properties to Layer 2, computed ones stay in Layer 1

**Confidence threshold**:
- Layer 2: Directly measured OR consensus theoretical (electron config from spectroscopy)
- Layer 1: Calculated from model, extrapolated from trends, or uncertain

**Example (Oganesson, Z=118)**:
```json
// Layer 2: data/experimental/nist_2024.json
{
  "118": {
    "symbol": "Og",
    "name": "Oganesson",
    "atomic_number": 118,
    "atomic_weight": 294,  // Most stable isotope, measured
    "discovery_year": 2002,
    "is_radioactive": true,
    "half_life": 0.00069  // 0.69 ms, measured
    // NO melting_point, boiling_point, density (never measured)
  }
}

// Layer 1: data/computed/pyykkö_2011/elements.json
{
  "118": {
    "electron_configuration": "[Rn] 5f14 6d10 7s2 7p6",
    "melting_point_estimated": 325,  // Extrapolated from noble gas trend
    "boiling_point_estimated": 450,  // Highly uncertain
    "density_estimated": 7.2,        // Calculated from crystal structure prediction
    "electronegativity_pauling": null  // Noble gas, undefined
  }
}
```

**Fallthrough logic**:
```python
def get_property(self, Z: int, prop: str) -> PropertyValue:
    # Layer 2: Experimental (if exists)
    if Z in self.experimental_data and prop in self.experimental_data[Z]:
        return PropertyValue(
            value=self.experimental_data[Z][prop],
            source='experimental',
            confidence=1.0
        )

    # Layer 1: Computed (if exists)
    if Z in self.computed_cache and prop in self.computed_cache[Z]:
        return PropertyValue(
            value=self.computed_cache[Z][prop],
            source='computed',
            confidence=self.computed_cache.metadata[Z][prop]['confidence']
        )

    # Layer 0: Generate on-demand
    return self.generator.compute_property(Z, prop)
```

---

## Question 2: Layer 0 Organization

### Considering Level 1 (Bonding Rules) Requirements

Level 1 will need to call Layer 0 for:
- **Valence electron count** (from electron config)
- **Orbital hybridization** (sp3, sp2, sp, from config + geometry)
- **Electronegativity** (multiple scales)
- **Atomic radius** (covalent, van der Waals)
- **Oxidation states** (from valence and stability)

Example Level 1 use case:
```python
# Bond formation between Carbon (Z=6) and Hydrogen (Z=1)
c_valence = element_theory.valence_electrons(6)  # → 4
h_valence = element_theory.valence_electrons(1)  # → 1
c_radius = element_theory.covalent_radius(6)     # → 77 pm
h_radius = element_theory.covalent_radius(1)     # → 31 pm

bond_length = c_radius + h_radius  # → 108 pm (C-H bond)
bond_polarity = abs(element_theory.electronegativity(6) - element_theory.electronegativity(1))  # → |2.55 - 2.20| = 0.35
```

### Options

**Option A: Pure Functions**
```python
# src/theory/electron_config.py
def electron_config(Z: int) -> str:
    """Compute electron configuration using Madelung rule."""
    pass

def valence_electrons(Z: int) -> int:
    """Extract valence electrons from config."""
    config = electron_config(Z)
    return count_valence(config)

# src/theory/atomic_radius.py
def covalent_radius(Z: int) -> float:
    """Extrapolate covalent radius from group trends."""
    pass
```

**Pros**:
- Simple, testable, no state
- Easy to compose: `valence = valence_electrons(electron_config(Z))`
- Pure mathematical functions (same input → same output)

**Cons**:
- No model versioning (Pyykkö vs. Fricke both use same functions?)
- Repeated computation (call `electron_config(Z)` multiple times)
- Hard to extend (how to add new models?)

---

**Option B: Class-Based**
```python
class ElementGenerator:
    def __init__(self, model: str = 'pyykkö_2011'):
        self.model = model
        self._config_cache = {}  # Cache electron configs

    def electron_config(self, Z: int) -> str:
        if Z not in self._config_cache:
            self._config_cache[Z] = self._compute_config(Z)
        return self._config_cache[Z]

    def valence_electrons(self, Z: int) -> int:
        config = self.electron_config(Z)
        return self._count_valence(config)

    def covalent_radius(self, Z: int) -> float:
        # Model-specific implementation
        if self.model == 'pyykkö_2011':
            return self._pyykkö_radius(Z)
        elif self.model == 'fricke_1971':
            return self._fricke_radius(Z)
```

**Pros**:
- Model versioning built-in (different instances for different models)
- Can cache intermediate results (avoid recomputation)
- Easy to extend (inherit base class, override methods)
- Stateful (can accumulate data during generation)

**Cons**:
- More complex, potential for "god object" antipattern
- Harder to test (need to instantiate class)
- State management (when to clear cache?)

---

**Option C: Hybrid (Recommended)**

**Pure functions for theory, class for model selection**

```python
# src/theory/quantum.py (pure functions, model-agnostic)
def madelung_rule(Z: int) -> str:
    """Standard Madelung/Aufbau filling order."""
    pass

def count_valence(config: str) -> int:
    """Parse config string, count outermost electrons."""
    pass

def slater_radius(Z: int, config: str) -> float:
    """Slater atomic radius from Z and config."""
    pass

# src/theory/models/pyykkö_2011.py (model-specific corrections)
def relativistic_config(Z: int, base_config: str) -> str:
    """Apply Pyykkö's Dirac-Fock corrections for Z>100."""
    pass

def relativistic_radius(Z: int, base_radius: float) -> float:
    """Apply relativistic contraction/expansion."""
    pass

# src/theory/generator.py (orchestration)
class ElementGenerator:
    def __init__(self, model: str = 'pyykkö_2011'):
        self.model = model
        self._load_model()

    def _load_model(self):
        """Import model-specific functions."""
        if self.model == 'pyykkö_2011':
            from .models import pyykkö_2011
            self.model_config = pyykkö_2011.relativistic_config
            self.model_radius = pyykkö_2011.relativistic_radius
        elif self.model == 'fricke_1971':
            from .models import fricke_1971
            self.model_config = fricke_1971.relativistic_config
            self.model_radius = fricke_1971.relativistic_radius

    def electron_config(self, Z: int) -> str:
        """Generate electron configuration for element Z."""
        base = madelung_rule(Z)
        if Z > 100:  # Apply relativistic corrections
            return self.model_config(Z, base)
        return base

    def valence_electrons(self, Z: int) -> int:
        """Get valence electron count."""
        config = self.electron_config(Z)
        return count_valence(config)

    def covalent_radius(self, Z: int) -> float:
        """Get covalent radius."""
        config = self.electron_config(Z)
        base = slater_radius(Z, config)
        if Z > 100:  # Apply relativistic corrections
            return self.model_radius(Z, base)
        return base
```

**Structure**:
```
src/theory/
  __init__.py
  quantum.py              # Pure functions (aufbau, Slater, etc.)
  nuclear.py              # Shell model, binding energy, half-life
  qed.py                  # QED limits, pair creation
  trends.py               # Extrapolation algorithms
  generator.py            # ElementGenerator class (orchestration)
  models/
    __init__.py
    pyykkö_2011.py        # Model-specific corrections
    fricke_1971.py
    nefedov_2006.py
```

**Why Hybrid?**
1. ✅ **Pure functions** = core theory (testable, composable, reusable)
2. ✅ **Classes** = model selection + orchestration (extensible, stateful caching OK)
3. ✅ **Separation**: Theory (quantum.py) vs. Models (pyykkö_2011.py) vs. API (generator.py)
4. ✅ **Level 1 interface**: Can import pure functions directly OR use generator class
   ```python
   # Level 1 option A: Direct function calls
   from src.theory.quantum import count_valence, madelung_rule
   valence = count_valence(madelung_rule(6))  # → 4

   # Level 1 option B: Via generator
   generator = ElementGenerator(model='pyykkö_2011')
   valence = generator.valence_electrons(6)  # → 4
   ```

### Recommendation: **Option C (Hybrid)**

**Rationale**:
1. **Testability**: Pure functions are easy to unit test
2. **Composability**: Level 1 can call functions directly (no object instantiation)
3. **Model versioning**: Class handles model selection without duplicating core theory
4. **Performance**: Class can cache expensive computations (e.g., orbital energies)
5. **Extensibility**: New models = new file in `models/`, override specific functions

---

## Implementation Plan

### Phase 1: Pure Theory Functions (No models yet)
```python
# src/theory/quantum.py
def madelung_rule(Z: int) -> str:
    """Generate electron configuration using standard Aufbau principle."""
    pass

def count_valence(config: str) -> int:
    """Count valence electrons from configuration string."""
    pass

def orbital_type(config: str) -> str:
    """Determine highest occupied orbital type (s, p, d, f, g)."""
    pass
```

**Test cases**:
- `madelung_rule(1)` → `"1s1"`
- `madelung_rule(6)` → `"1s2 2s2 2p2"`
- `madelung_rule(79)` → `"[Xe] 4f14 5d10 6s1"` (Au)
- `count_valence("1s2 2s2 2p2")` → `4` (C)
- `count_valence("[Xe] 4f14 5d10 6s1")` → `1` (Au)

### Phase 2: Add ElementGenerator Class
```python
# src/theory/generator.py
class ElementGenerator:
    def __init__(self, model: str = 'standard'):
        self.model = model

    def electron_config(self, Z: int) -> str:
        return madelung_rule(Z)

    def valence_electrons(self, Z: int) -> int:
        return count_valence(self.electron_config(Z))

    def generate_element(self, Z: int) -> dict:
        """Generate all properties for element Z."""
        return {
            'atomic_number': Z,
            'electron_configuration': self.electron_config(Z),
            'valence_electrons': self.valence_electrons(Z),
            # ... more properties
        }
```

**Test cases**:
- Generate elements 1, 6, 79, 118
- Validate against known configurations
- Check valence electron counts

### Phase 3: Add Model-Specific Corrections
```python
# src/theory/models/pyykkö_2011.py
def relativistic_config(Z: int, base_config: str) -> str:
    """Apply Dirac-Fock corrections for superheavy elements."""
    if Z == 118:  # Oganesson
        return "[Rn] 5f14 6d10 7s2 7p6"  # Pyykkö prediction
    if Z == 119:  # Ununennium
        return "[Og] 8s1"  # Pyykkö: 8s before 7d
    if Z == 120:  # Unbinilium
        return "[Og] 8s2"
    # ... more Z>118 cases
    return base_config
```

### Phase 4: Test Against Known Elements
```python
# scripts/validate_theory.py
def validate_against_nist():
    """Compare generated configs for Z=1-118 vs. NIST data."""
    generator = ElementGenerator()
    nist_data = load_json('data/experimental/nist_2024.json')

    mismatches = []
    for Z in range(1, 119):
        generated = generator.electron_config(Z)
        if Z in nist_data:
            experimental = nist_data[Z]['electron_configuration']
            if normalize(generated) != normalize(experimental):
                mismatches.append((Z, generated, experimental))

    print(f"Matched: {118 - len(mismatches)}/118")
    print(f"Mismatches: {mismatches}")
```

---

## Summary

**Question 1 Answer**: **Selective Layer 2**
- Only high-confidence experimental data in Layer 2
- Missing properties fall through to Layer 1 (computed)
- Clear semantics: Layer 2 = measured, Layer 1 = computed

**Question 2 Answer**: **Hybrid (Pure Functions + Class)**
- Core theory = pure functions (`quantum.py`, `nuclear.py`)
- Model selection = class (`ElementGenerator`)
- Model-specific = separate modules (`models/pyykkö_2011.py`)
- Level 1 can use either functions directly or generator class

**Implementation order**:
1. Pure theory functions (electron config, valence count)
2. ElementGenerator class (orchestration)
3. Validate against NIST for Z=1-118
4. Add model-specific corrections (Pyykkö, Fricke)
5. Generate Layer 1 cache (JSON snapshots)

Ready to implement?
