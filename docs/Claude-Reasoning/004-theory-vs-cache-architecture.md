# Theory vs. Cache: Architectural Analysis

**Date**: 2025-11-23
**Problem**: Resolve tension between fast O(1) LUT lookups and generative theory-based computation
**Core Question**: How do we separate "what we know" from "why we know it" while keeping them connected?

---

## The Fundamental Tension

### What We Need

1. **Fast lookups** (O(1)): `periodic_table.get('C')` → instant
2. **Theoretical grounding**: Properties derivable from first principles
3. **Provenance tracking**: Know which values are measured vs. computed
4. **Update propagation**: New data or theory → system updates
5. **Model versioning**: Handle competing theories (Pyykkö vs. Fricke for Z>120)
6. **Uncertainty quantification**: Confidence scores based on data source

### The Conflict

- **Static LUTs**: Fast but brittle (hardcoded, no theory visible, manual updates)
- **Pure generators**: Theoretically grounded but slow (compute every time, no caching)
- **Naive hybrid**: Two sources of truth (cache vs. generator), synchronization hell

**Insight**: This is the same problem NGL-1 solved by decoupling token embeddings from conceptual space!
- Token embeddings = cached lookup (fast)
- Conceptual space = compositional rules (generative)
- Bridge = explicit mapping layer

Can we apply the same pattern here?

---

## Architectural Options

### Option A: Generator-First with Lazy Caching

```python
class PeriodicTable:
    def __init__(self):
        self._cache = {}  # Z → Element
        self._generator = ElementGenerator()

    def get(self, Z: int) -> Element:
        if Z not in self._cache:
            self._cache[Z] = self._generator.generate(Z)
        return self._cache[Z]
```

**Pros**:
- Theory is explicit and always available
- Cache is transparent (just optimization)
- Easy to invalidate: `cache.clear()` after generator update

**Cons**:
- Experimental data mixed with generated data (provenance unclear)
- Cache invalidation: When to recompute?
- Generator must be fast (can't do expensive calculations)
- Two sources of truth: generator code vs. cached results

**Verdict**: Good for pure theoretical systems, but our data is hybrid (experimental + theoretical)

---

### Option B: Data-First with Provenance Metadata

```python
Element:
    electronegativity: float = 2.55
    electronegativity_meta: PropertyMetadata = {
        "source": "NIST",
        "method": "experimental",
        "confidence": 1.0,
        "reference": "doi:10.1021/...",
        "last_updated": "2024-06-15"
    }
```

**Pros**:
- LUT is source of truth (fast, reliable)
- Provenance explicit for every property
- Clear which values are experimental vs. theoretical

**Cons**:
- Theory disconnected from data (generator is external tool)
- Updates require manual data file edits
- No way to recompute theoretical values automatically
- Metadata bloat (2x storage per property)

**Verdict**: Good for data-heavy systems, but theory is not first-class

---

### Option C: Layered Architecture (Recommended)

**Three layers with explicit precedence**:

```python
Layer 0: Theory (Generators)
├─ ElectronConfigGenerator(Z) → config string
├─ AtomicRadiusModel(Z, config) → radius estimate
├─ ElectronegativityModel(Z, config) → EN estimate
└─ NuclearStabilityModel(Z, N) → half-life estimate

Layer 1: Computed Cache (Generated LUT)
├─ Generated from Layer 0
├─ Versioned by model (e.g., "pyykkö_2011", "fricke_1971")
├─ Immutable snapshots (JSON files)
└─ Metadata: {"model_version": "v1.0", "generated_date": "2025-11-23"}

Layer 2: Experimental Overrides (Measured Data)
├─ NIST atomic properties (Z=1-118)
├─ IUPAC validated values
├─ Always takes precedence over Layer 1
└─ Metadata: {"source": "NIST", "confidence": 1.0, "measured_date": "2024"}

Query Path: Layer 2 → Layer 1 → Layer 0 (fallback)
```

**Lookup algorithm**:

```python
class PeriodicTable:
    def __init__(self):
        self.experimental_data = load_json('data/nist_elements.json')     # Layer 2
        self.computed_cache = load_json('data/generated_elements.json')   # Layer 1
        self.generator = ElementGenerator()                               # Layer 0

    def get_property(self, Z: int, property_name: str) -> PropertyValue:
        # Layer 2: Check experimental override
        if Z in self.experimental_data:
            if property_name in self.experimental_data[Z]:
                return PropertyValue(
                    value=self.experimental_data[Z][property_name],
                    source="experimental",
                    confidence=1.0
                )

        # Layer 1: Check computed cache
        if Z in self.computed_cache:
            if property_name in self.computed_cache[Z]:
                return PropertyValue(
                    value=self.computed_cache[Z][property_name],
                    source="computed",
                    confidence=self.computed_cache[Z][f"{property_name}_confidence"]
                )

        # Layer 0: Generate on demand (cache miss)
        element = self.generator.generate(Z)
        computed_value = getattr(element, property_name)

        # Optionally: Write to Layer 1 cache for future
        self._update_cache(Z, property_name, computed_value)

        return PropertyValue(
            value=computed_value,
            source="generated",
            confidence=0.5  # Default for uncached
        )
```

**Pros**:
- ✅ Fast lookups: Layer 2 and Layer 1 are both O(1) dict access
- ✅ Theory explicit: Layer 0 is pure code, versioned, inspectable
- ✅ Provenance implicit: Layer determines source (experimental > computed > generated)
- ✅ Clear update path:
  - New NIST data → update Layer 2 file
  - New theory → regenerate Layer 1 from Layer 0
  - New element discovered → add to Layer 2, invalidate Layer 1 cache for that Z
- ✅ Model versioning: Multiple Layer 1 caches (one per theory version)
- ✅ Competing models: User can choose: `pt.get(120, model='pyykkö')` vs. `pt.get(120, model='fricke')`

**Cons**:
- Three layers to maintain (complexity)
- Cache invalidation strategy needed (when to regenerate Layer 1?)
- Storage overhead (multiple model snapshots)

**Verdict**: Best balance. Mirrors NGL-1 pattern: experimental = token embeddings (cached), computed = conceptual space (LUT), generated = composition rules (theory).

---

### Option D: Immutable Snapshots with Version History

```python
data/
  snapshots/
    nist_2024-06-15.json           # Experimental snapshot
    pyykkö_2011_generated.json     # Theory snapshot v1
    pyykkö_2025_qed.json           # Theory snapshot v2 (improved QED)
  metadata/
    snapshot_registry.json         # Tracks all versions

PeriodicTable(snapshot="nist_2024-06-15", fallback="pyykkö_2025_qed")
```

**Pros**:
- Reproducibility: Can recreate exact state from any date
- Version comparison: Diff snapshots to see what changed
- Rollback: Revert to previous snapshot if new theory is wrong

**Cons**:
- Storage explosion (N snapshots × 118-173 elements × 115 properties)
- Complexity: Which snapshot to load by default?
- Query interface: How to specify snapshot version?

**Verdict**: Over-engineered for v1, but useful for research. Consider for v2 after Option C is working.

---

## Recommended Architecture: Layered with Provenance

### Design Principles

1. **Separation of Concerns**:
   - **Theory (Layer 0)**: Pure functions, no state, versioned code
   - **Cache (Layer 1)**: Immutable snapshots, regenerable, versioned data
   - **Experiment (Layer 2)**: Ground truth, manually curated, timestamped

2. **Precedence Hierarchy**:
   - Experimental > Computed > Generated
   - Higher layers override lower layers
   - Lower layers provide fallback for missing data

3. **Provenance by Layer**:
   - No need for per-property metadata (reduces bloat)
   - Source determined by which layer provided the value
   - Confidence scores stored in Layer 1 metadata

4. **Update Strategy**:
   - **Layer 2 updates**: Manual (NIST releases new data, we update JSON)
   - **Layer 1 updates**: Automatic (run generator, write new snapshot)
   - **Layer 0 updates**: Code changes (new generator version, tag in git)

5. **Versioning**:
   - **Layer 0**: Git tags (`element-generator-v1.0`)
   - **Layer 1**: Snapshot files (`generated_pyykkö_2025-11-23.json`)
   - **Layer 2**: Timestamped sources (`nist_2024-06-15.json`)

---

## Handling Competing Theoretical Models

**Problem**: Pyykkö (2011) vs. Fricke (1971) predict different electron configs for Z>120

**Solution**: Multiple Layer 1 caches

```python
data/
  experimental/
    nist_2024.json                 # Layer 2
  computed/
    pyykkö_2011/
      elements.json                # Layer 1a
      metadata.json                # Model info
    fricke_1971/
      elements.json                # Layer 1b
      metadata.json
    nefedov_2006/
      elements.json                # Layer 1c
      metadata.json

# Query with model selection
pt = PeriodicTable(model='pyykkö_2011')  # Default model
pt.get(120).electron_configuration       # Uses Pyykkö

# Compare models
pt_fricke = PeriodicTable(model='fricke_1971')
diff = compare(pt.get(120), pt_fricke.get(120))  # Show differences
```

**Multi-model query**:

```python
# Get all predictions for element 120
predictions = pt.get_all_models(120)
# {
#   'pyykkö_2011': Element(120, config='[Og] 8s2', confidence=0.8),
#   'fricke_1971': Element(120, config='[Og] 8s2', confidence=0.6),
#   'nefedov_2006': Element(120, config='[Og] 8s1 8p1', confidence=0.5)
# }

# Consensus check
if len(set(p.electron_configuration for p in predictions.values())) > 1:
    warnings.warn("Models disagree on electron configuration for Z=120")
```

---

## Cache Invalidation Strategy

**When to regenerate Layer 1?**

### Trigger 1: Theory Update (Layer 0 change)

```python
# Developer updates generator code
git commit -m "Improved QED corrections for Z>137"
git tag element-generator-v2.0

# Regenerate Layer 1
python scripts/regenerate_cache.py --model pyykkö_2011 --version v2.0

# Output: data/computed/pyykkö_2011_v2/elements.json
```

### Trigger 2: New Experimental Data (Layer 2 update)

```python
# NIST releases new ionization energies for lanthanides
# Developer updates data/experimental/nist_2025.json

# Layer 1 unaffected (theory unchanged)
# But can regenerate to incorporate new trends for extrapolation
python scripts/regenerate_cache.py --incorporate-nist data/experimental/nist_2025.json
```

### Trigger 3: New Element Discovered

```python
# Element 120 synthesized! Half-life measured: 0.5 seconds
# Add to data/experimental/element_120_discovery.json

# Layer 1 cache for Z=120 becomes stale
# Regenerate only Z=120 (or Z>118 range)
python scripts/regenerate_cache.py --elements 120
```

**Cache invalidation policy**:
- **Automatic**: On Layer 0 code change (detected via git hook)
- **Manual**: Developer triggers after curating new Layer 2 data
- **Partial**: Can regenerate specific Z ranges instead of all 173 elements

---

## Provenance Tracking Without Metadata Bloat

**Problem**: Storing `{"value": 2.55, "source": "NIST", "confidence": 1.0}` for every property doubles data size

**Solution**: Implicit provenance from layer + property-level metadata in separate file

```json
// data/experimental/nist_2024.json (Layer 2)
{
  "6": {
    "symbol": "C",
    "atomic_weight": 12.011,
    "electronegativity_pauling": 2.55,
    "melting_point": 3823.0
  }
}

// data/computed/pyykkö_2011/elements.json (Layer 1)
{
  "120": {
    "symbol": "Ubn",
    "electron_configuration": "[Og] 8s2",
    "atomic_radius_estimated": 200,
    "electronegativity_pauling_extrapolated": 1.3
  }
}

// data/computed/pyykkö_2011/metadata.json (Layer 1 metadata)
{
  "model_name": "Pyykkö 2011 Dirac-Fock",
  "model_version": "v1.0",
  "generated_date": "2025-11-23",
  "generator_git_tag": "element-generator-v1.0",
  "default_confidence": {
    "electron_configuration": 0.8,
    "atomic_radius_estimated": 0.5,
    "electronegativity_pauling_extrapolated": 0.4
  },
  "element_specific_confidence": {
    "120": {"electron_configuration": 0.75},  // Lower due to model disagreement
    "173": {"all_properties": 0.1}  // QED limit, highly uncertain
  }
}
```

**Provenance query**:

```python
value = pt.get_property(6, 'electronegativity_pauling')
# PropertyValue(value=2.55, source='experimental', confidence=1.0)

value = pt.get_property(120, 'electronegativity_pauling')
# PropertyValue(value=1.3, source='computed', confidence=0.4)

# Detailed provenance
provenance = pt.get_provenance(120, 'electronegativity_pauling')
# {
#   'value': 1.3,
#   'source': 'computed',
#   'layer': 'L1',
#   'model': 'pyykkö_2011',
#   'method': 'trend_extrapolation',
#   'confidence': 0.4,
#   'generated_date': '2025-11-23',
#   'generator_version': 'v1.0'
# }
```

---

## Implementation Structure

```
src/
  theory/                          # Layer 0
    __init__.py
    electron_config.py             # Madelung + relativistic
    atomic_radius.py               # Trend extrapolation
    electronegativity.py           # Multiple scales
    nuclear_stability.py           # Shell model + QED
    qed_limits.py                  # Spontaneous pair creation flags
    models/
      pyykkö_2011.py               # Specific model implementation
      fricke_1971.py
      nefedov_2006.py

  core/                            # Layer 1 + Layer 2 interface
    element.py                     # Element class
    periodic_table.py              # Main API, layered lookup
    property_value.py              # PropertyValue(value, source, confidence)
    cache.py                       # Cache management
    provenance.py                  # Provenance tracking

data/
  experimental/                    # Layer 2
    nist_2024.json                 # Curated experimental data
    iupac_2024.json                # Alternative source
    element_120_discovery.json     # Future: when discovered

  computed/                        # Layer 1
    pyykkö_2011/
      elements.json                # Generated element properties
      metadata.json                # Model info, confidence scores
    fricke_1971/
      elements.json
      metadata.json

scripts/
  regenerate_cache.py              # Generate Layer 1 from Layer 0
  validate_theory.py               # Compare Layer 1 vs. Layer 2 for Z=1-118
  compare_models.py                # Diff between model predictions
```

---

## Tradeoffs Analysis

### Computation Cost vs. Lookup Speed

| Approach | Lookup Time | Computation Time | Storage | Flexibility |
|----------|-------------|------------------|---------|-------------|
| Pure generator | O(n) compute | Every query | 0 bytes | High (always fresh) |
| Pure static LUT | O(1) | Never | ~500KB | Low (manual updates) |
| Lazy cache | O(1) after first | First query only | ~500KB RAM | Medium |
| **Layered (Recommended)** | **O(1)** | **Pre-generated** | **~2MB** | **High** |

**Why Layered wins**:
- O(1) lookups (just dict access to Layer 1/2)
- Computation happens once, offline (regenerate_cache.py)
- Storage cost: 3 model snapshots × 173 elements × 50KB ≈ 2MB (negligible)
- Flexibility: Can switch models, compare versions, update theory without touching data

---

## Answers to Your Questions

### 1. Where should theoretical physics live vs cached element properties?

**Theory (Layer 0)**: Pure Python code in `src/theory/`
- Functions: `electron_config(Z)`, `atomic_radius(Z, config)`, `half_life(Z, N)`
- Versioned via git tags
- No state, no data

**Cache (Layer 1)**: JSON snapshots in `data/computed/`
- Generated from Layer 0
- Immutable (regenerate to update)
- Versioned by filename/metadata

**Experimental (Layer 2)**: JSON in `data/experimental/`
- Manually curated from NIST/IUPAC
- Timestamped sources
- Always overrides Layer 1

### 2. How do we track provenance - which properties came from measurement vs theory?

**Implicit from layer**:
- Layer 2 = experimental (confidence = 1.0)
- Layer 1 = computed from theory (confidence in metadata)
- Layer 0 = generated on-demand (confidence = default)

**Explicit for detailed queries**:
- `pt.get_provenance(Z, property_name)` returns full metadata
- No per-property storage bloat

### 3. When theory improves or new elements are discovered, how does the system update?

**Theory improves (Layer 0 change)**:
1. Developer updates `src/theory/qed_limits.py`
2. Git commit + tag: `element-generator-v2.0`
3. Run: `python scripts/regenerate_cache.py --all-models`
4. New Layer 1 snapshots created (`pyykkö_2011_v2/elements.json`)
5. Old snapshots retained for comparison/reproducibility

**New element discovered**:
1. Developer adds to `data/experimental/element_120.json`
2. Run: `python scripts/regenerate_cache.py --elements 120-173` (update superheavy range)
3. Layer 2 overrides Layer 1 for Z=120

### 4. How do we handle competing theoretical models?

**Multiple Layer 1 caches**:
- `data/computed/pyykkö_2011/elements.json`
- `data/computed/fricke_1971/elements.json`

**Query API**:
- `PeriodicTable(model='pyykkö_2011')` → default model
- `pt.get_all_models(120)` → returns all predictions
- `compare_models(120)` → diff between models

**Consensus flagging**:
- If models disagree → warning flag
- Confidence reduced when disagreement is large

---

## Optimal Architecture: 3-Layer Hierarchy

**Recommendation**: Implement **Option C (Layered Architecture)**

**Why**:
1. ✅ Solves all four tensions (fast lookups, theory explicit, provenance clear, updateable)
2. ✅ Mirrors NGL-1 LUT strategy (decoupled layers with composition rules)
3. ✅ Scales to competing models (multiple Layer 1 caches)
4. ✅ Supports versioning and reproducibility
5. ✅ Clear update paths (Layer 2 manual, Layer 1 regenerate, Layer 0 code)

**Next Steps**:
1. Implement Layer 0 (theory generators) first
2. Validate by comparing generated Z=1-118 against NIST (Layer 2)
3. Generate Layer 1 cache (snapshot of theoretical values)
4. Build Layer 2 → Layer 1 → Layer 0 query interface
5. Add provenance tracking and confidence scoring

Does this architecture solve the tensions you identified? Any modifications you'd suggest?
