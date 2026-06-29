"""Tests for the resilience (SCRI) service."""
from __future__ import annotations

from app.services.resilience import SCRIService


class TestSCRIComputation:
    def test_stub_scri_returns_valid_response(self) -> None:
        service = SCRIService(db=None)
        response = service._stub_scri()
        assert response.scri_score > 0
        assert response.category in {"Weak", "Moderate", "Strong", "Highly Resilient"}
        assert len(response.drivers) == 7
        assert all(v >= 0 for v in response.drivers.values())
        assert "Category Concentration" in response.drivers
        assert "Order Fulfillment" in response.drivers

    def test_score_category_boundaries(self) -> None:
        assert SCRIService._score_category(0) == "Weak"
        assert SCRIService._score_category(39.9) == "Weak"
        assert SCRIService._score_category(40) == "Moderate"
        assert SCRIService._score_category(59.9) == "Moderate"
        assert SCRIService._score_category(60) == "Strong"
        assert SCRIService._score_category(79.9) == "Strong"
        assert SCRIService._score_category(80) == "Highly Resilient"
        assert SCRIService._score_category(100) == "Highly Resilient"

    def test_hhi_diversity_perfect(self) -> None:
        """Equal distribution should produce high diversity score."""
        score = SCRIService._hhi_diversity_score([100, 100, 100, 100], max_score=15.0)
        assert score > 12.0  # Close to maximum 15

    def test_hhi_diversity_monopoly(self) -> None:
        """Single dominant player should produce low diversity."""
        score = SCRIService._hhi_diversity_score([1000, 1, 1, 1], max_score=15.0)
        assert score < 3.0

    def test_entropy_diversity_uniform(self) -> None:
        """Uniform distribution should produce maximum entropy."""
        score = SCRIService._entropy_diversity_score([50, 50, 50, 50], max_score=15.0)
        assert score >= 14.0  # Should be very close to 15

    def test_entropy_diversity_single(self) -> None:
        """Single category should produce zero entropy."""
        score = SCRIService._entropy_diversity_score([100], max_score=15.0)
        assert score == 0.0

    def test_empty_counts_return_zero(self) -> None:
        assert SCRIService._hhi_diversity_score([], max_score=15.0) == 0.0
        assert SCRIService._entropy_diversity_score([], max_score=15.0) == 0.0

    def test_stub_drivers_sum_to_score(self) -> None:
        service = SCRIService(db=None)
        response = service._stub_scri()
        assert abs(response.scri_score - sum(response.drivers.values())) < 0.01
