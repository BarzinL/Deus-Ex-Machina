"""
Confidence scoring for element property predictions.

This module assesses the reliability of computed element properties based on
atomic number, theoretical model, and current physics understanding.

Confidence is NOT part of the physics computation - it's a meta-level
assessment of "how much do we trust this computed value?"
"""

import json
from pathlib import Path
from typing import Dict, Optional


class ConfidenceScorer:
    """
    Computes confidence scores for element properties based on Z range,
    model agreement, and experimental validation status.

    Confidence scores range from 0.0 (completely uncertain) to 1.0 (experimental certainty).

    The scorer loads confidence profiles from config/confidence_profiles.json,
    allowing confidence ranges to be tuned without code changes.

    Physical basis for confidence degradation:
    - Z ≤ 118: Experimental spectroscopy and measurements (high confidence)
    - Z = 119-126: Theoretical predictions, island of stability (medium confidence)
    - Z = 127-137: Extended period 8, models diverge (low confidence)
    - Z ≥ 138: Supercritical QED regime, highly uncertain (very low confidence)
    - Z ≥ 173: Beyond QED limit, not viable atoms (minimal confidence)

    References:
    - Pyykkö, P. (2011). A suggested periodic table up to Z≤172. Phys. Chem. Chem. Phys. 13, 161
    - Greiner, W. et al. (1985). Quantum Electrodynamics of Strong Fields (QED limits)
    """

    def __init__(self, profile: str = "default", config_path: Optional[Path] = None):
        """
        Initialize confidence scorer with specified profile.

        Args:
            profile: Profile name from confidence_profiles.json
                     ("default", "conservative", or "optimistic")
            config_path: Optional path to confidence_profiles.json
                        (defaults to config/confidence_profiles.json)

        Raises:
            FileNotFoundError: If config file not found
            KeyError: If profile doesn't exist in config
        """
        self.profile_name = profile

        # Load configuration
        if config_path is None:
            # Assume config is in project root/config/
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "confidence_profiles.json"

        with open(config_path, 'r') as f:
            config = json.load(f)

        if profile not in config["profiles"]:
            available = list(config["profiles"].keys())
            raise KeyError(
                f"Profile '{profile}' not found. Available profiles: {available}"
            )

        self.profile = config["profiles"][profile]
        self.z_ranges = self.profile["z_ranges"]
        self.version = config.get("version", "unknown")

    def _find_z_range(self, Z: int) -> Optional[Dict]:
        """
        Find the configuration range that Z falls into.

        Args:
            Z: Atomic number

        Returns:
            Range configuration dict, or None if Z is out of range
        """
        for range_name, range_config in self.z_ranges.items():
            z_min, z_max = range_config["range"]
            if z_min <= Z <= z_max:
                return range_config

        return None

    def electron_config_confidence(
        self,
        Z: int,
        model: str = "pyykkö_2011",
        models_agree: Optional[bool] = None
    ) -> float:
        """
        Confidence in electron configuration predictions.

        Factors considered:
        - Z range (observed vs. theoretical)
        - Theoretical model used
        - Agreement/disagreement between models (if known)

        Args:
            Z: Atomic number
            model: Theoretical model name (e.g., "pyykkö_2011", "fricke_1971")
            models_agree: Optional flag - if True, add bonus; if False, add penalty

        Returns:
            Confidence score (0.0 to 1.0)

        Examples:
            >>> scorer = ConfidenceScorer()
            >>> scorer.electron_config_confidence(6)  # Carbon
            1.0
            >>> scorer.electron_config_confidence(120)  # Unbinilium
            0.85
            >>> scorer.electron_config_confidence(120, models_agree=False)
            0.75
        """
        range_config = self._find_z_range(Z)

        if range_config is None:
            # Z is outside defined ranges (very high Z)
            return 0.0

        base_confidence = range_config["confidence"]["electron_configuration"]

        # Apply model agreement modifiers if known
        if models_agree is not None and "property_modifiers" in self.profile:
            modifiers = self.profile["property_modifiers"].get("electron_configuration", {})
            if models_agree:
                bonus = modifiers.get("model_agreement_bonus", 0.0)
                base_confidence = min(1.0, base_confidence + bonus)
            else:
                penalty = modifiers.get("model_disagreement_penalty", 0.0)
                base_confidence = max(0.0, base_confidence + penalty)

        return base_confidence

    def atomic_radius_confidence(self, Z: int) -> float:
        """
        Confidence in atomic radius extrapolations.

        Atomic radii are measured for lighter elements, but must be
        extrapolated from periodic trends for superheavy elements.
        Relativistic effects (orbital contraction/expansion) make
        extrapolation increasingly uncertain at high Z.

        Args:
            Z: Atomic number

        Returns:
            Confidence score (0.0 to 1.0)

        Physical note:
            Relativistic effects cause:
            - s/p orbital contraction (stronger nuclear attraction)
            - d/f orbital expansion (screening effects)
            This makes simple trend extrapolation unreliable for Z > 100.
        """
        range_config = self._find_z_range(Z)

        if range_config is None:
            return 0.0

        return range_config["confidence"]["atomic_radius"]

    def electronegativity_confidence(self, Z: int) -> float:
        """
        Confidence in electronegativity predictions.

        Electronegativity is challenging to predict for superheavy elements
        because it depends on:
        - Effective nuclear charge (relativistic corrections)
        - Orbital energies (QED effects)
        - Chemical environment (uncertain for undiscovered elements)

        Args:
            Z: Atomic number

        Returns:
            Confidence score (0.0 to 1.0)
        """
        range_config = self._find_z_range(Z)

        if range_config is None:
            return 0.0

        return range_config["confidence"]["electronegativity"]

    def ionization_energy_confidence(self, Z: int) -> float:
        """
        Confidence in ionization energy predictions.

        Ionization energies can be calculated from orbital energies,
        but require accurate treatment of:
        - Electron correlation
        - Relativistic effects
        - QED corrections (vacuum polarization, self-energy)

        Args:
            Z: Atomic number

        Returns:
            Confidence score (0.0 to 1.0)
        """
        range_config = self._find_z_range(Z)

        if range_config is None:
            return 0.0

        return range_config["confidence"]["ionization_energy"]

    def oxidation_states_confidence(self, Z: int) -> float:
        """
        Confidence in oxidation state predictions.

        Oxidation states are inferred from electron configuration
        and chemical analogy, but superheavy elements may exhibit
        unexpected oxidation states due to relativistic effects.

        Args:
            Z: Atomic number

        Returns:
            Confidence score (0.0 to 1.0)
        """
        range_config = self._find_z_range(Z)

        if range_config is None:
            return 0.0

        return range_config["confidence"]["oxidation_states"]

    def half_life_confidence(self, Z: int, N: Optional[int] = None) -> float:
        """
        Confidence in half-life predictions.

        Half-life predictions are highly uncertain for superheavy elements
        because they depend on:
        - Nuclear shell effects (magic numbers)
        - Fission barrier heights
        - Alpha decay Q-values
        - Competition between decay modes

        The island of stability (Z~120-126, N~184) may dramatically
        increase half-lives, but predictions vary by orders of magnitude.

        Args:
            Z: Atomic number
            N: Neutron number (optional, used to check proximity to N=184)

        Returns:
            Confidence score (0.0 to 1.0)

        Physical note:
            If N is close to 184 (magic number), confidence may be higher
            due to shell stabilization effects.
        """
        range_config = self._find_z_range(Z)

        if range_config is None:
            return 0.0

        base_confidence = range_config["confidence"]["half_life"]

        # Apply island of stability bonus if near magic neutron number
        if N is not None and "property_modifiers" in self.profile:
            modifiers = self.profile["property_modifiers"].get("half_life", {})

            # N=184 is predicted magic number
            if 179 <= N <= 189:  # Within 5 neutrons of magic number
                bonus = modifiers.get("island_of_stability_bonus", 0.0)
                base_confidence = min(1.0, base_confidence + bonus)
            elif abs(N - 184) > 20:  # Far from magic number
                penalty = modifiers.get("far_from_magic_numbers_penalty", 0.0)
                base_confidence = max(0.0, base_confidence + penalty)

        return base_confidence

    def get_all_confidences(self, Z: int, N: Optional[int] = None) -> Dict[str, float]:
        """
        Get confidence scores for all properties at once.

        Args:
            Z: Atomic number
            N: Neutron number (optional, for half-life calculation)

        Returns:
            Dictionary mapping property names to confidence scores

        Example:
            >>> scorer = ConfidenceScorer()
            >>> scores = scorer.get_all_confidences(120, N=184)
            >>> scores
            {
                'electron_configuration': 0.85,
                'atomic_radius': 0.60,
                'electronegativity': 0.55,
                'ionization_energy': 0.60,
                'oxidation_states': 0.70,
                'half_life': 0.60  # Bonus for N=184 magic number
            }
        """
        return {
            "electron_configuration": self.electron_config_confidence(Z),
            "atomic_radius": self.atomic_radius_confidence(Z),
            "electronegativity": self.electronegativity_confidence(Z),
            "ionization_energy": self.ionization_energy_confidence(Z),
            "oxidation_states": self.oxidation_states_confidence(Z),
            "half_life": self.half_life_confidence(Z, N),
        }

    def __repr__(self) -> str:
        return f"ConfidenceScorer(profile='{self.profile_name}', version='{self.version}')"
