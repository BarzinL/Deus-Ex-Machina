# Confidence Scoring Architecture

**Date**: 2025-11-23
**Question**: Where should confidence scoring live in the 3-layer architecture?

---

## The Problem

Different properties have different confidence levels based on Z:

| Z Range | Regime | Electron Config Confidence | Radius Confidence | Half-life Confidence |
|---------|--------|---------------------------|-------------------|---------------------|
| 1-118 | Observed | 1.0 (experimental) | 0.9-1.0 (measured) | 1.0 (measured) |
| 119-126 | Island of stability | 0.8 (models agree) | 0.6 (extrapolated) | 0.4 (high uncertainty) |
| 127-137 | Extended period 8 | 0.6 (models diverge) | 0.4 (trend-based) | 0.2 (speculative) |
| 138-172 | Supercritical | 0.3 (QED uncertain) | 0.3 (highly uncertain) | 0.1 (unknown) |
| 173+ | Beyond QED limit | 0.1 (not viable atoms) | 0.1 | 0.0 (impossible) |

**Key observations**:
1. Confidence varies by **property type** (config vs. radius vs. half-life)
2. Confidence varies by **Z range** (observed vs. theoretical)
3. Confidence varies by **model agreement** (Pyykkö vs. Fricke for Z>120)
4. Confidence can change over time (new data → update confidence)

---

## Options Analysis

### Option 1: ElementGenerator Computes Confidence

```python
class ElementGenerator:
    def generate_element(self, Z: int) -> Element:
        config = madelung_rule(Z)

        # Confidence computed here
        if Z <= 118:
            config_confidence = 1.0
        elif Z <= 126:
            config_confidence = 0.8
        elif Z <= 137:
            config_confidence = 0.6
        else:
            config_confidence = 0.3

        return Element(
            electron_configuration=config,
            config_confidence=config_confidence
        )
```

**Pros**:
- ✅ Theory functions stay pure (no metadata pollution)
- ✅ Confidence rules are explicit and centralized
- ✅ Easy to update confidence thresholds without touching theory

**Cons**:
- ❌ ElementGenerator becomes "smart" (knows physics limits)
- ❌ Confidence logic hard-coded in generator (not data-driven)
- ❌ Different properties have different confidence - generator gets complex

---

### Option 2: Theory Functions Return Confidence

```python
def madelung_rule(Z: int) -> Tuple[str, float]:
    config = "..."

    # Function self-reports confidence
    if Z <= 118:
        confidence = 1.0
    elif Z <= 126:
        confidence = 0.8
    else:
        confidence = 0.3

    return (config, confidence)
```

**Pros**:
- ✅ Functions self-report their certainty
- ✅ Confidence travels with the value (explicit pairing)

**Cons**:
- ❌ Functions are no longer pure (return type changes)
- ❌ Hard to compose (what if you need just the value?)
- ❌ Mixes computation with metadata (violates separation of concerns)
- ❌ Every theory function needs confidence logic (duplication)

---

### Option 3: Layer 1 Metadata Only

```python
# Layer 0: Pure theory (no confidence)
config = madelung_rule(120)  # → "[Og] 8s2"

# Layer 1: Cached with metadata
# data/computed/pyykkö_2011/elements.json
{
  "120": {
    "electron_configuration": "[Og] 8s2"
  }
}

# data/computed/pyykkö_2011/metadata.json
{
  "default_confidence": {
    "electron_configuration": 0.8
  },
  "element_specific_confidence": {
    "120": {
      "electron_configuration": 0.75  # Override for model disagreement
    }
  }
}
```

**Pros**:
- ✅ Complete separation (theory = computation, metadata = trust)
- ✅ Can update confidence post-hoc (new research → edit metadata)
- ✅ Supports element-specific overrides (e.g., Z=120 lower due to model disagreement)

**Cons**:
- ❌ Confidence disconnected from generation (manual maintenance)
- ❌ Risk of forgetting to add confidence for new elements
- ❌ Metadata files can get large and hard to maintain

---

## Recommended Solution: Hybrid (Option 1 + 3)

**Separate ConfidenceScorer class + Layer 1 storage**

### Architecture

```python
# src/theory/confidence.py (NEW)
class ConfidenceScorer:
    """
    Computes confidence scores for element properties based on Z range,
    model agreement, and experimental validation status.

    Confidence is NOT part of the physics computation - it's a meta-level
    assessment of "how much do we trust this computed value?"
    """

    def electron_config_confidence(self, Z: int, model: str = 'pyykkö_2011') -> float:
        """
        Confidence in electron configuration predictions.

        Factors:
        - Z ≤ 118: Experimentally validated via spectroscopy
        - Z = 119-126: Theoretical, but multiple models agree
        - Z = 127-137: Models diverge, high uncertainty
        - Z ≥ 138: Supercritical regime, QED corrections dominate

        Args:
            Z: Atomic number
            model: Which theoretical model used

        Returns:
            Confidence score (0.0 to 1.0)
        """
        if Z <= 118:
            return 1.0  # Experimental spectroscopic data
        elif Z <= 120:
            return 0.85  # Active synthesis attempts, models agree
        elif Z <= 126:
            return 0.75  # Island of stability, some model agreement
        elif Z <= 137:
            return 0.55  # Extended period 8, models diverge
        elif Z <= 172:
            return 0.30  # Supercritical, QED uncertain
        else:
            return 0.10  # Beyond QED limit, not viable

    def atomic_radius_confidence(self, Z: int) -> float:
        """Confidence in atomic radius extrapolations."""
        if Z <= 100:
            return 0.95  # Measured or well-extrapolated
        elif Z <= 118:
            return 0.70  # Some measurements, some extrapolation
        elif Z <= 126:
            return 0.50  # Trend-based extrapolation
        elif Z <= 137:
            return 0.35  # High uncertainty
        else:
            return 0.20  # Speculative

    def half_life_confidence(self, Z: int, N: int) -> float:
        """Confidence in half-life predictions."""
        if Z <= 118:
            # Check if actually measured vs. calculated
            # (This would require checking against experimental database)
            return 0.90  # Most measured
        elif Z <= 126 and abs(N - 184) <= 5:
            return 0.50  # Island of stability - medium confidence
        elif Z <= 137:
            return 0.25  # High decay uncertainty
        else:
            return 0.10  # Very speculative


# src/theory/generator.py
class ElementGenerator:
    def __init__(self, model: str = 'pyykkö_2011'):
        self.model = model
        self.confidence_scorer = ConfidenceScorer()

    def generate_element(self, Z: int) -> dict:
        """Generate element with computed properties and confidence scores."""
        config = madelung_rule(Z)
        config_confidence = self.confidence_scorer.electron_config_confidence(Z, self.model)

        # ... compute other properties

        return {
            'atomic_number': Z,
            'electron_configuration': config,
            '_confidence': {
                'electron_configuration': config_confidence,
                # other property confidences...
            }
        }


# scripts/regenerate_cache.py
def generate_layer1_cache(model: str = 'pyykkö_2011'):
    """Generate Layer 1 cache with confidence metadata."""
    generator = ElementGenerator(model=model)

    elements = {}
    confidence_map = {}

    for Z in range(1, 174):
        elem_data = generator.generate_element(Z)

        # Separate data from confidence
        confidence_map[Z] = elem_data.pop('_confidence')
        elements[Z] = elem_data

    # Write to Layer 1
    with open(f'data/computed/{model}/elements.json', 'w') as f:
        json.dump(elements, f)

    # Write confidence metadata
    with open(f'data/computed/{model}/metadata.json', 'w') as f:
        json.dump({
            'model_name': model,
            'generated_date': datetime.now().isoformat(),
            'element_confidence': confidence_map
        }, f)
```

---

## Why This Approach is Optimal

### 1. Separation of Concerns

- **Layer 0 (Theory)**: Pure physics, no confidence
  - `madelung_rule(Z)` → just returns config
  - No metadata pollution

- **ConfidenceScorer**: Meta-level assessment
  - "How much do we trust this result?"
  - Separate class = testable, replaceable

- **ElementGenerator**: Orchestration
  - Calls theory functions
  - Calls confidence scorer
  - Combines results

- **Layer 1 (Cache)**: Storage
  - Elements file = computed values
  - Metadata file = confidence scores

### 2. Flexibility

**Different models can have different confidence**:
```python
pyykkö_scorer = ConfidenceScorer(model='pyykkö_2011')
fricke_scorer = ConfidenceScorer(model='fricke_1971')

pyykkö_confidence = pyykkö_scorer.electron_config_confidence(120)  # 0.75
fricke_confidence = fricke_scorer.electron_config_confidence(120)  # 0.65 (older model)
```

**Confidence can be updated without regenerating**:
```json
// New research shows element 120 is more stable than predicted
// Edit metadata.json manually:
{
  "element_confidence": {
    "120": {
      "electron_configuration": 0.80,  // Updated from 0.75
      "half_life": 0.65  // Updated from 0.50
    }
  }
}
```

### 3. Testability

Each component is independently testable:

```python
# Test theory (pure functions)
def test_electron_config():
    assert madelung_rule(6) == "[He] 2s2 2p2"

# Test confidence scoring (separate logic)
def test_confidence_scoring():
    scorer = ConfidenceScorer()
    assert scorer.electron_config_confidence(1) == 1.0
    assert scorer.electron_config_confidence(120) == 0.75
    assert scorer.electron_config_confidence(173) == 0.10

# Test generator (integration)
def test_element_generation():
    gen = ElementGenerator()
    elem = gen.generate_element(120)
    assert elem['electron_configuration'] == "[Og] 8s2"
    assert elem['_confidence']['electron_configuration'] == 0.75
```

### 4. Composability

Level 1 (bonding rules) can query confidence to make decisions:

```python
# Level 1: Functional group composition
def can_form_bond(element1, element2):
    """Check if two elements can bond based on valence and confidence."""
    e1_valence = count_valence(element1.config)
    e2_valence = count_valence(element2.config)

    # Check confidence - don't use highly uncertain elements
    if element1.config_confidence < 0.5 or element2.config_confidence < 0.5:
        warnings.warn("Low confidence in bonding prediction")

    # Apply bonding rules...
```

### 5. Evolution Over Time

**Timeline of confidence updates**:

| Date | Event | Action |
|------|-------|--------|
| 2025-11-23 | Initial implementation | Generate Layer 1 with current confidence |
| 2027-01-15 | Element 120 discovered! | Update Layer 2 with experimental data, confidence → 1.0 |
| 2028-06-30 | New QED calculations | Update ConfidenceScorer, regenerate Layer 1 |
| 2030-12-01 | Pyykkö publishes update | Add new model, compare confidences |

---

## Implementation Plan

### Phase 2 will implement:

1. **ConfidenceScorer class** (`src/theory/confidence.py`)
   - Methods for each property type
   - Z-range based logic
   - Model-specific adjustments

2. **ElementGenerator class** (`src/theory/generator.py`)
   - Uses theory functions (Layer 0)
   - Uses ConfidenceScorer
   - Returns structured data with confidence

3. **Element dataclass** (`src/core/element.py`)
   - Stores properties + confidence
   - Type-safe access

4. **Cache generation** (`scripts/regenerate_cache.py`)
   - Generate Layer 1 elements.json
   - Generate Layer 1 metadata.json with confidence

---

## Final Answer

**Confidence should be computed by ConfidenceScorer (called from ElementGenerator), then stored in Layer 1 metadata.json.**

**Why**:
- ✅ Theory functions stay pure (Option 1 benefit)
- ✅ Confidence rules are explicit and testable (separate class)
- ✅ Can update confidence post-hoc (Option 3 benefit)
- ✅ Supports property-specific and Z-range-specific rules
- ✅ Easy to extend with new models or experimental data

**NOT**:
- ❌ Not in theory functions (keeps them pure)
- ❌ Not hard-coded in generator (delegated to ConfidenceScorer)
- ❌ Not only in metadata (computed automatically, but cacheable)

This gives us the best of all three options with minimal downsides.
