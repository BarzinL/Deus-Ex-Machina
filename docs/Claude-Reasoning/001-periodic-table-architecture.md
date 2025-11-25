# Periodic Table Architecture Analysis

**Date**: 2025-11-23
**Context**: Level 0 foundation for hierarchical LUT framework
**Goal**: Design optimal data structure and storage for periodic table that enables efficient Level 1 composition

---

## First Principles Analysis

### What Are We Actually Representing?

The periodic table is **static, well-defined domain knowledge** with:
- **Fixed size**: 118 elements (+ potentially synthetic elements)
- **Rich properties**: ~20-50 properties per element depending on domain needs
- **Natural hierarchy**: Groups, periods, blocks provide implicit structure
- **Bonding rules**: Elements → bonds → functional groups (Level 0 → Level 1 transition)

### Key Insight from NGL-1 Analogy

NGL-1 achieved 95% memory reduction by:
1. **Splitting data into multiple LUTs** (decoupling token embeddings from conceptual space)
2. **Hierarchical lookup** (efficient access patterns)
3. **Compact representation** (4.4MB for 1.1M+ codepoints)

**Question**: Can we apply similar principles here?
- Periodic table: ~118 elements × ~30 properties = ~3,540 data points
- This is TINY compared to NGL-1's scale
- **Implication**: Memory isn't the constraint; query patterns and composition rules are

---

## Critical Design Questions

### 1. Query Patterns We Need to Optimize

**Direct lookup** (most common):
- `get_element(atomic_number=6)` → Carbon
- `get_element(symbol='C')` → Carbon

**Range queries** (materials science filtering):
- "All elements with electronegativity 2.0-3.0"
- "All metals with melting point < 200°C"
- "All elements with valence electrons = 4"

**Bonding compatibility** (Level 1 composition):
- "What can carbon bond with?" → Based on valence, electronegativity
- "What geometries can nitrogen form?" → Based on orbital hybridization
- "What oxidation states are common?" → Domain-specific rules

**Bulk operations** (materials search):
- "Filter all semiconductors"
- "Find all air-stable elements"

### 2. Level 0 → Level 1 Interface

**Critical transition**: Atoms → Functional Groups

What properties enable bonding rules?
- **Valence electrons**: Determines bond capacity
- **Electronegativity**: Determines bond polarity
- **Atomic radius**: Determines bond length/strength
- **Orbital structure**: Determines geometry (sp3, sp2, sp)
- **Oxidation states**: Determines ionic bonding

**Architecture requirement**: Element data structure must expose a "bonding capability" interface

---

## Architectural Options

### Option A: Pure Data (JSON/YAML) + Runtime Indexing

```
data/periodic_table.json:
{
  "elements": [
    {
      "atomic_number": 6,
      "symbol": "C",
      "name": "Carbon",
      "mass": 12.011,
      "electronegativity": 2.55,
      "valence_electrons": 4,
      "common_oxidation_states": [-4, -3, -2, -1, 0, 1, 2, 3, 4],
      "covalent_radius": 77,
      ...
    }
  ]
}
```

**Pros**:
- Human-readable, easy to edit
- Version control friendly
- Language-agnostic (can load from any language)
- Data/code separation

**Cons**:
- Loading overhead (parse JSON every time)
- No type safety (typos in property names fail at runtime)
- Query requires manual filtering (no built-in indexing)

**Optimization**: Build indices on load (symbol→element, atomic_number→element)

---

### Option B: Code-Based (Python Classes)

```python
@dataclass
class Element:
    atomic_number: int
    symbol: str
    name: str
    mass: float
    electronegativity: float
    valence_electrons: int
    ...

    def can_bond_with(self, other: Element) -> bool:
        """Level 0 → Level 1 bonding rules"""
        pass

# Hardcode all elements
CARBON = Element(6, "C", "Carbon", 12.011, 2.55, 4, ...)
HYDROGEN = Element(1, "H", "Hydrogen", 1.008, 2.20, 1, ...)

PERIODIC_TABLE = [HYDROGEN, HELIUM, LITHIUM, ...]  # 118 elements
```

**Pros**:
- Type safety (IDE autocomplete, static analysis)
- Zero loading overhead (imported as code)
- Methods can embed domain logic (bonding rules)
- Fast direct access

**Cons**:
- Not human-friendly for editing (repetitive)
- Hard to version control diffs (large code changes)
- Tightly coupled to Python
- Properties are scattered across 118 definitions

---

### Option C: Hybrid (JSON Data + Python API)

```
data/periodic_table.json  [static data]
src/core/element.py       [API + indices]
```

```python
class Element:
    def __init__(self, data: dict):
        self.atomic_number = data['atomic_number']
        self.symbol = data['symbol']
        ...

    def can_bond_with(self, other: Element) -> bool:
        """Bonding logic here"""
        pass

class PeriodicTable:
    def __init__(self):
        data = json.load('data/periodic_table.json')
        self._elements = [Element(e) for e in data['elements']]
        self._by_symbol = {e.symbol: e for e in self._elements}
        self._by_number = {e.atomic_number: e for e in self._elements}

    def get(self, symbol: str) -> Element:
        return self._by_symbol[symbol]

    def filter(self, **criteria) -> List[Element]:
        """Range queries"""
        pass
```

**Pros**:
- Data/code separation
- Type-safe API with IDE support
- Human-editable data
- Indices built once on load
- Methods can implement domain logic

**Cons**:
- Small loading overhead (one-time JSON parse)
- Dual maintenance (data schema + Python class)

---

### Option D: Embedded Database (SQLite)

```sql
CREATE TABLE elements (
    atomic_number INTEGER PRIMARY KEY,
    symbol TEXT UNIQUE,
    name TEXT,
    mass REAL,
    electronegativity REAL,
    ...
);

CREATE INDEX idx_electronegativity ON elements(electronegativity);
```

**Pros**:
- Built-in indexing and query optimization
- Range queries are SQL-native
- Can add computed columns
- Standard interface (SQL)

**Cons**:
- Overkill for 118 rows
- Overhead for simple lookups
- Bonding logic would be in application code anyway
- Harder to version control (binary format)

---

## Recommendation: Hybrid (Option C) with Strategic Enhancements

**Rationale**:
1. **Human-editable data** (JSON) enables easy property additions without code changes
2. **Type-safe API** (Python classes) gives IDE support and prevents bugs
3. **Runtime indices** optimize common queries (O(1) by symbol/number)
4. **Method-based bonding rules** keep composition logic with the data
5. **Scales to Level 1**: Can extend Element class with bonding methods

**Enhanced design**:

```python
# Lazy loading: Only parse JSON when first accessed
# Singleton pattern: One instance across application
# Property validation: Ensure data integrity on load
# Extensible: Easy to add new properties or methods

class PeriodicTable:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_data()
        return cls._instance

    def _load_data(self):
        """Lazy load + validate + index"""
        pass

    def query(self, **filters) -> List[Element]:
        """Flexible filtering:
        pt.query(valence_electrons=4)
        pt.query(electronegativity__range=(2.0, 3.0))
        pt.query(symbol__in=['C', 'N', 'O'])
        """
        pass
```

---

## Open Questions for You

1. **Property granularity**: Should we include ALL known atomic properties upfront, or start minimal and expand as needed for each domain (materials vs. drugs)?

2. **Bonding rule representation**: Should bonding logic be:
   - Hard-coded methods in Element class?
   - Separate declarative rules (e.g., JSON config)?
   - Learned from data (ML model)?

3. **Data sources**: Should I:
   - Manually create JSON from Wikipedia/NIST?
   - Scrape from existing databases?
   - Use existing Python packages (e.g., `mendeleev`, `periodictable`) as data source?

4. **Computed vs. static properties**: Some properties (like common oxidation states) vary by context. How should we handle domain-specific property variants?

5. **Performance targets**: What's the acceptable latency for:
   - Single element lookup? (target: <1ms)
   - Filtering 118 elements? (target: <10ms)
   - Composition rule evaluation (atoms→functional group)? (target: ??)

---

## Next Steps

After your input, I'll implement the chosen architecture with:
- [ ] JSON schema for periodic table data
- [ ] Element class with type hints
- [ ] PeriodicTable singleton with indices
- [ ] Query interface for filtering
- [ ] Unit tests for data integrity
- [ ] Bonding capability interface (Level 0→1 bridge)

**Note**: This is ~118 elements × ~20-30 properties. Even with comprehensive data, we're looking at <1MB total. The real complexity is in the *interface design* for composition, not the storage.
