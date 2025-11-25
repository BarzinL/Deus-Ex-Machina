"""
Crystallization: Measuring compositional emergence across scales.

This module studies the fundamental question: Why does reality exhibit stable
compositional structure? What determines where compositional boundaries form?

The approach:
1. Measure additivity violations (naive composition vs actual properties)
2. Extract structural/topological features
3. Look for patterns that predict when units should be cached
4. Discover general principles of compositional emergence

Domain-agnostic design allows application to:
- Chemistry: Atoms → Molecules (benzene, resonance)
- QCD: Quarks/gluons → Hadrons (Karyons)
- Biology: Amino acids → Protein domains
- Engineering: Components → Systems
"""

from src.crystallization.detector import (
    CrystallizationDetector,
    AdditivityViolation,
    StructuralFeatures
)

__all__ = [
    'CrystallizationDetector',
    'AdditivityViolation',
    'StructuralFeatures',
]
