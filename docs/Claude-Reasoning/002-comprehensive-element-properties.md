# Comprehensive Periodic Table Properties

**Date**: 2025-11-23
**Research Question**: How many element properties exist comprehensively?
**Sources**: Mendeleev Python package, PTable.com, NIST, PubChem

---

## Answer: 115+ Direct Properties + Extended Data Classes

Based on the **mendeleev Python package** (which aggregates data from NIST, IUPAC, and scientific literature), there are **115 direct element properties** stored in the Elements table, plus additional related data accessed through class references.

---

## Property Categories and Count

### 1. Identification (7 properties)
- atomic_number
- symbol
- name
- name_origin
- cas (Chemical Abstracts Service ID)
- inchi (IUPAC identifier)
- description

### 2. Nuclear/Atomic Structure (8 properties)
- protons
- neutrons
- electrons
- mass_number (most abundant isotope)
- atomic_weight
- atomic_weight_uncertainty
- nvalence (valence electron count)
- zeff (effective nuclear charge)

### 3. Electron Configuration (3 properties)
- econf (electron configuration)
- electrons
- nvalence

### 4. Atomic Radii (9 types!)
- atomic_radius (Slater)
- atomic_radius_rahm (Rahm et al.)
- covalent_radius_bragg (Bragg)
- covalent_radius_cordero (Cordero)
- covalent_radius_pyykko (single bond)
- covalent_radius_pyykko_double
- covalent_radius_pyykko_triple
- metallic_radius
- metallic_radius_c12 (12 neighbors)

### 5. Van der Waals Radii (9 types!)
Different force fields and methodologies:
- vdw_radius (standard)
- vdw_radius_alvarez
- vdw_radius_batsanov
- vdw_radius_bondi
- vdw_radius_dreiding
- vdw_radius_mm3
- vdw_radius_rt
- vdw_radius_truhlar
- vdw_radius_uff

### 6. Electronegativity (14 scales!)
Different measurement methodologies:
- electronegativity_pauling (most common)
- electronegativity_allen
- electronegativity_allred_rochow
- electronegativity_cottrell_sutton
- electronegativity_ghosh
- electronegativity_gordy
- electronegativity_li_xue
- electronegativity_martynov_batsanov
- electronegativity_mulliken
- electronegativity_nagle
- electronegativity_sanderson
- en_gunnarsson_lundqvist
- en_miedema
- en_mullay
- en_robles_bartolotti

### 7. Chemical Reactivity (6 properties)
- electron_affinity
- electrophilicity (Parr index)
- proton_affinity
- gas_basicity
- hardness (absolute hardness)
- softness (absolute softness)

### 8. Thermal Properties (10 properties)
- melting_point
- boiling_point
- critical_temperature
- critical_pressure
- triple_point_temperature
- triple_point_pressure
- fusion_heat (energy to melt)
- evaporation_heat (energy to vaporize)
- specific_heat_capacity (J/g/K)
- molar_heat_capacity (J/mol/K)
- thermal_conductivity

### 9. Physical Properties (6 properties)
- density
- atomic_volume (molar volume)
- miedema_molar_volume
- lattice_constant (crystal unit cell)
- lattice_structure (crystal type code)
- phase (solid/liquid/gas at STP)

### 10. Classification (9 properties)
- period (row in periodic table)
- group (column in periodic table)
- block (s, p, d, f)
- series (alkali metal, halogen, etc.)
- geochemical_class
- goldschmidt_class
- mendeleev_number (Pettifor scale)
- pettifor_number
- glawe_number

### 11. Discovery & History (4 properties)
- discovery_year
- discoverers
- discovery_location
- sources (natural occurrence)

### 12. Visualization (3 properties)
- cpk_color (CPK molecular model colors)
- jmol_color (Jmol visualization)
- molcas_gv_color (MOLCAS GV colors)

### 13. Dispersion/Polarizability (4 properties)
- dipole_polarizability
- dipole_polarizability_unc (uncertainty)
- c6 (Van der Waals dispersion coefficient)
- c6_gb (Gould & Bučko coefficient)

### 14. Miedema Model Parameters (2 properties)
For alloy formation predictions:
- miedema_electron_density
- miedema_molar_volume

### 15. Abundance (2 properties)
- abundance_crust (mg/kg in Earth's crust)
- abundance_sea (mg/L in seawater)

### 16. Economic/Supply Chain (9 properties)
- price_per_kg (USD/kg)
- production_concentration (%)
- reserve_distribution (%)
- top_3_producers (nations/regions)
- top_3_reserve_holders
- political_stability_of_top_producer (percentile)
- political_stability_of_top_reserve_holder (percentile)
- relative_supply_risk (1-10 scale)
- recycling_rate (%)
- substitutability

### 17. Radioactivity (2 properties)
- is_radioactive (boolean)
- is_monoisotopic (single stable isotope)

### 18. Thermodynamic (2 properties)
- heat_of_formation (standard enthalpy)
- phase transitions

### 19. Practical Information (3 properties)
- uses (primary applications)
- oxides (possible oxide compounds)
- nist_webbook_url (reference link)

### 20. References to Extended Data Classes
Not direct properties but relationships to detailed tables:
- **isotopes** → Isotopes table (mass, abundance, half-life, decay modes, spin, etc.)
- **ionenergy** → IonizationEnergies table (1st through 30th ionization energies!)
- **ionic_radii** → IonicRadii table (radii for different oxidation states)
- **oxistates** → OxidationStates table (all possible oxidation states)
- **sconst** → ScreeningConstants table (Slater screening constants)

---

## Total Comprehensive Count

**Direct properties**: 115
**Extended classes**: 5 (each with multiple sub-properties per element)

### If we expand the extended classes:
- **Ionization energies**: Up to 30 per element = +30 properties
- **Isotopes**: Variable per element (H has 7, Sn has 39!) with ~10 properties each
- **Ionic radii**: Multiple per oxidation state (e.g., Fe²⁺, Fe³⁺) with coordination variants
- **Oxidation states**: Variable list per element
- **Screening constants**: Shell/orbital specific values

**Realistic total if fully expanded**: **~200-300+ properties per element** depending on how you count isotopes and oxidation state variants.

---

## Properties Critical for Level 0 → Level 1 (Bonding)

For your hierarchical framework, the **essential bonding properties** are:

**Must-have** (8):
1. valence_electrons (nvalence)
2. electronegativity_pauling
3. atomic_radius
4. covalent_radius_pyykko (single/double/triple)
5. electron_affinity
6. oxidation_states (from oxistates table)
7. electron_configuration (econf)
8. group/period/block

**Very useful** (6):
9. atomic_weight (for molecular mass calculations)
10. van der Waals radius (for molecular geometry)
11. density (for material properties)
12. melting/boiling points (for processing constraints)
13. thermal_conductivity (for semiconductors)
14. is_radioactive (for stability filtering)

**Domain-specific additions**:
- **Materials science**: thermal properties, electrical conductivity, crystal structure, band gap
- **Drug discovery**: toxicity, abundance in body, chemical reactivity
- **Organic semiconductors**: specifically C, H, N, O, S, Se with aromatic bonding

---

## Recommendation: Three-Tier Property Schema

Given the 115+ property count, I recommend structuring the data in **three tiers**:

### Tier 1: Core Properties (Always Loaded)
~30 essential properties for identification, classification, and basic bonding
- Fast lookup, minimal memory (~10KB for 118 elements)
- Includes: number, symbol, name, mass, valence, electronegativity, radius, group/period/block

### Tier 2: Extended Properties (Load on Demand)
~50 additional properties for specialized queries
- Thermal, mechanical, abundance, discovery data
- Loaded when filtering by these properties

### Tier 3: Relational Data (Query from Separate Tables)
~35 properties stored in related tables
- Isotopes, ionization energies, ionic radii, oxidation states
- Accessed via foreign key relationships when needed

**Rationale**: This mirrors the LUT hierarchical strategy from NGL-1:
- Fast access to common data (Tier 1)
- Efficient memory usage (don't load rarely-used properties)
- Decouple static atomic data (Tier 1) from context-dependent data (Tier 3: oxidation states vary by compound)

---

## Next Decision Point

You said you want **"absolutely ALL the properties"**. I need clarification:

1. **All 115 direct properties** in a single flat JSON structure? (Simpler, ~50-100KB total)
2. **Tiered structure** with core + extended + relational? (More complex, but scalable)
3. **Include expanded classes** (isotopes, all 30 ionization energies, etc.)? (Much larger, ~1-5MB)

My recommendation: **Start with all 115 direct properties in flat JSON** (Tier 1+2 combined), with references to the extended classes that we can add later if needed. This gives you maximum flexibility without premature optimization.

**File structure**:
```
data/
  periodic_table_core.json        # 115 properties × 118 elements
  isotopes.json                    # Extended data (optional)
  ionization_energies.json         # Extended data (optional)
  ionic_radii.json                 # Extended data (optional)
  oxidation_states.json            # Extended data (optional)
```

What do you prefer?
