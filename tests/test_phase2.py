"""
Test ElementGenerator and ConfidenceScorer (Phase 2).
"""

import sys
sys.path.insert(0, '/run/media/Barzin/SyncSpace-ext4/Codebases/Deus Ex Machina')

from src.theory.generator import ElementGenerator
from src.theory.confidence import ConfidenceScorer
from src.core.element import ElementStatus


def test_confidence_scorer():
    """Test confidence scoring across different Z ranges."""
    print("\n" + "="*60)
    print("TEST: ConfidenceScorer")
    print("="*60)

    scorer = ConfidenceScorer(profile="default")
    print(f"Scorer: {scorer}\n")

    # Test different Z ranges
    test_cases = [
        (6, "Carbon", "observed"),
        (79, "Gold", "observed"),
        (118, "Oganesson", "observed"),
        (120, "Unbinilium", "synthesis_planned"),
        (126, "Island of stability", "island_of_stability"),
        (137, "QED critical", "extended_period_8"),
        (172, "QED limit", "supercritical"),
        (173, "Beyond limit", "beyond_qed_limit"),
    ]

    for Z, name, expected_range in test_cases:
        scores = scorer.get_all_confidences(Z)
        print(f"{name} (Z={Z}):")
        print(f"  Electron config: {scores['electron_configuration']:.2f}")
        print(f"  Atomic radius:   {scores['atomic_radius']:.2f}")
        print(f"  Half-life:       {scores['half_life']:.2f}")
        print()

    print("✓ ConfidenceScorer test complete\n")


def test_element_generator():
    """Test element generation with confidence scores."""
    print("="*60)
    print("TEST: ElementGenerator")
    print("="*60)

    gen = ElementGenerator(model="pyykkö_2011", confidence_profile="default")
    print(f"Generator: {gen}\n")

    # Test elements across different regimes
    test_elements = [1, 6, 79, 118, 120]

    for Z in test_elements:
        elem = gen.generate(Z)

        print(f"{elem}")
        print(f"  Symbol: {elem.symbol}")
        print(f"  Config: {elem.electron_configuration}")
        print(f"  Valence: {elem.valence_electrons}")
        print(f"  Block: {elem.block}")
        print(f"  Status: {elem.status.value}")
        print(f"  Config confidence: {elem.confidence['electron_configuration']:.2f}")
        print()

    print("✓ ElementGenerator test complete\n")


def test_element_status_classification():
    """Test element status classification."""
    print("="*60)
    print("TEST: Element Status Classification")
    print("="*60)

    gen = ElementGenerator()

    status_tests = [
        (1, ElementStatus.OBSERVED),
        (118, ElementStatus.OBSERVED),
        (119, ElementStatus.SYNTHESIS_PLANNED),
        (120, ElementStatus.SYNTHESIS_PLANNED),
        (126, ElementStatus.PREDICTED),
        (137, ElementStatus.PREDICTED),
        (150, ElementStatus.SUPERCRITICAL),
        (172, ElementStatus.SUPERCRITICAL),
        (173, ElementStatus.IMPOSSIBLE),
    ]

    passed = 0
    for Z, expected_status in status_tests:
        elem = gen.generate(Z)
        if elem.status == expected_status:
            print(f"✓ Z={Z:3d}: {elem.status.value:20s} (expected: {expected_status.value})")
            passed += 1
        else:
            print(f"✗ Z={Z:3d}: {elem.status.value:20s} (expected: {expected_status.value})")

    print(f"\nPassed: {passed}/{len(status_tests)}")
    print()


def test_confidence_profiles():
    """Test different confidence profiles."""
    print("="*60)
    print("TEST: Confidence Profiles (default vs. conservative vs. optimistic)")
    print("="*60)

    Z = 120  # Test element in theoretical range

    for profile in ["default", "conservative", "optimistic"]:
        scorer = ConfidenceScorer(profile=profile)
        config_conf = scorer.electron_config_confidence(Z)
        radius_conf = scorer.atomic_radius_confidence(Z)

        print(f"{profile.capitalize():12s}: config={config_conf:.2f}, radius={radius_conf:.2f}")

    print("\n✓ Profile comparison complete\n")


def main():
    """Run all Phase 2 tests."""
    print("\n" + "="*60)
    print("PHASE 2 TEST SUITE: ElementGenerator + ConfidenceScorer")
    print("="*60)

    test_confidence_scorer()
    test_element_generator()
    test_element_status_classification()
    test_confidence_profiles()

    print("="*60)
    print("ALL PHASE 2 TESTS COMPLETE")
    print("="*60)


if __name__ == '__main__':
    main()
