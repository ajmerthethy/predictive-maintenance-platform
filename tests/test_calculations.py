from app.services.downtime_cost import calculate_downtime_cost
from app.services.health_score import calculate_asset_health_score
from app.services.maintenance_recommendation import generate_maintenance_recommendation
from app.services.maintenance_roi import calculate_maintenance_roi


# -----------------------------
# HEALTH SCORE
# (feeds directly into both downtime cost and ROI below - both routers
# compute this first and pass its output into the other two functions)
# -----------------------------

def test_health_score_normal_case():
    # 100 - (0.2*100) = 80, no status/alert/work-order penalties.
    result = calculate_asset_health_score(
        failure_probability=0.2, health_status="LOW"
    )
    assert result == {"health_score": 80, "rating": "Good"}


def test_health_score_critical_with_alerts_and_work_orders():
    # 100 - 90 = 10; -10 (CRITICAL); -6 (3 alerts * 2); -2 (2 work orders * 1)
    # = -8, clamped to 0.
    result = calculate_asset_health_score(
        failure_probability=0.9,
        health_status="CRITICAL",
        active_alerts=3,
        open_work_orders=2,
    )
    assert result == {"health_score": 0, "rating": "Critical"}


def test_health_score_zero_probability_perfect_health():
    result = calculate_asset_health_score(failure_probability=0.0, health_status="LOW")
    assert result == {"health_score": 100, "rating": "Excellent"}


def test_health_score_clamps_out_of_range_probability_above_one():
    # Invalid input (probability should be 0-1): 100 - 150 = -50, clamped to 0.
    # Documents that the function tolerates out-of-range input via
    # clamping rather than raising.
    result = calculate_asset_health_score(failure_probability=1.5, health_status="LOW")
    assert result["health_score"] == 0
    assert result["rating"] == "Critical"


def test_health_score_clamps_negative_probability():
    # Invalid input: 100 - (-20) = 120, clamped to 100.
    result = calculate_asset_health_score(
        failure_probability=-0.2, health_status="LOW"
    )
    assert result["health_score"] == 100
    assert result["rating"] == "Excellent"


def test_health_score_rating_boundaries():
    # Exact boundary values - each tier's "if score >= N" cutoff.
    assert calculate_asset_health_score(failure_probability=0.10, health_status="LOW")["rating"] == "Excellent"  # 90
    assert calculate_asset_health_score(failure_probability=0.25, health_status="LOW")["rating"] == "Good"       # 75
    assert calculate_asset_health_score(failure_probability=0.50, health_status="LOW")["rating"] == "Monitor"    # 50
    assert calculate_asset_health_score(failure_probability=0.75, health_status="LOW")["rating"] == "At Risk"    # 25


# -----------------------------
# DOWNTIME COST
# -----------------------------

def test_downtime_cost_critical_status():
    # multiplier=2.5, risk_factor=(100-20)/100=0.8 -> 5000*2.5*0.8=10000
    result = calculate_downtime_cost(machine_status="CRITICAL", health_score=20)
    assert result == {"estimated_daily_cost": 10000.0, "currency": "USD"}


def test_downtime_cost_warning_status():
    # multiplier=1.5, risk_factor=(100-60)/100=0.4 -> 5000*1.5*0.4=3000
    result = calculate_downtime_cost(machine_status="WARNING", health_score=60)
    assert result == {"estimated_daily_cost": 3000.0, "currency": "USD"}


def test_downtime_cost_other_status_defaults_to_multiplier_one():
    # multiplier=1, risk_factor=(100-90)/100=0.1 -> 5000*1*0.1=500
    result = calculate_downtime_cost(machine_status="LOW", health_score=90)
    assert result == {"estimated_daily_cost": 500.0, "currency": "USD"}


def test_downtime_cost_zero_at_perfect_health_regardless_of_status():
    # Edge case: health_score=100 -> risk_factor=0 -> cost is 0 even for
    # CRITICAL status (an inconsistent input combination, but the
    # arithmetic result is well-defined and worth locking in).
    result = calculate_downtime_cost(machine_status="CRITICAL", health_score=100)
    assert result == {"estimated_daily_cost": 0.0, "currency": "USD"}


def test_downtime_cost_maximal_at_zero_health():
    # Edge case: health_score=0 -> risk_factor=1 -> cost = base * multiplier
    # exactly. 5000*2.5*1=12500
    result = calculate_downtime_cost(machine_status="CRITICAL", health_score=0)
    assert result == {"estimated_daily_cost": 12500.0, "currency": "USD"}


def test_downtime_cost_unrecognized_status_falls_back_to_multiplier_one():
    # Invalid/unexpected status string (not "CRITICAL"/"WARNING") - falls
    # into the else branch rather than raising.
    result = calculate_downtime_cost(machine_status="not-a-real-status", health_score=50)
    assert result == {"estimated_daily_cost": 2500.0, "currency": "USD"}  # 5000*1*0.5


def test_downtime_cost_none_status_falls_back_to_multiplier_one():
    result = calculate_downtime_cost(machine_status=None, health_score=50)
    assert result == {"estimated_daily_cost": 2500.0, "currency": "USD"}


def test_downtime_cost_negative_health_score_not_clamped():
    # Invalid input (health_score should be 0-100): risk_factor=
    # (100-(-10))/100=1.1, exceeding the "worst case" of 1.0. Documents
    # that this function does not validate/clamp its health_score input -
    # a negative value produces a cost higher than the theoretical max.
    result = calculate_downtime_cost(machine_status="CRITICAL", health_score=-10)
    assert result == {"estimated_daily_cost": 13750.0, "currency": "USD"}  # 5000*2.5*1.1


# -----------------------------
# MAINTENANCE ROI
# -----------------------------

def test_maintenance_roi_normal_case():
    # potential_downtime_loss = 1000*3 = 3000; avoided_loss = 3000-500=2500
    result = calculate_maintenance_roi(
        downtime_cost_per_day=1000,
        health_score=80,
        maintenance_cost=500,
        downtime_days=3,
    )
    assert result == {
        "maintenance_cost": 500,
        "potential_downtime_loss": 3000.0,
        "estimated_savings": 2500.0,
        "recommendation": "Continue monitoring",
    }


def test_maintenance_roi_zero_downtime_cost():
    # Edge case: downtime_cost_per_day=0 -> potential_downtime_loss=0,
    # avoided_loss=0-500=-500, floored to 0.
    result = calculate_maintenance_roi(
        downtime_cost_per_day=0,
        health_score=10,
        maintenance_cost=500,
        downtime_days=3,
    )
    assert result == {
        "maintenance_cost": 500,
        "potential_downtime_loss": 0.0,
        "estimated_savings": 0.0,
        "recommendation": "Immediate maintenance recommended",
    }


def test_maintenance_roi_maintenance_cost_exceeds_downtime_loss():
    # Edge case: maintenance itself costs more than the downtime it
    # would avoid - savings floored at 0, not negative.
    result = calculate_maintenance_roi(
        downtime_cost_per_day=100,
        health_score=40,
        maintenance_cost=5000,
        downtime_days=1,
    )
    assert result == {
        "maintenance_cost": 5000,
        "potential_downtime_loss": 100.0,
        "estimated_savings": 0.0,
        "recommendation": "Schedule preventive maintenance",
    }


def test_maintenance_roi_negative_downtime_cost_not_validated():
    # Invalid input (downtime_cost_per_day should never be negative in
    # practice): potential_downtime_loss itself comes out negative too -
    # documents that only estimated_savings is floored at 0, not this
    # field. Worth knowing if this function is ever fed unvalidated data.
    result = calculate_maintenance_roi(
        downtime_cost_per_day=-100,
        health_score=10,
        maintenance_cost=500,
        downtime_days=3,
    )
    assert result["potential_downtime_loss"] == -300.0
    assert result["estimated_savings"] == 0.0
    assert result["recommendation"] == "Immediate maintenance recommended"


def test_maintenance_roi_recommendation_boundaries():
    # Exact threshold values for each recommendation tier.
    below_25 = calculate_maintenance_roi(
        downtime_cost_per_day=100, health_score=24, maintenance_cost=0, downtime_days=1
    )
    assert below_25["recommendation"] == "Immediate maintenance recommended"

    at_25 = calculate_maintenance_roi(
        downtime_cost_per_day=100, health_score=25, maintenance_cost=0, downtime_days=1
    )
    assert at_25["recommendation"] == "Schedule preventive maintenance"

    at_50 = calculate_maintenance_roi(
        downtime_cost_per_day=100, health_score=50, maintenance_cost=0, downtime_days=1
    )
    assert at_50["recommendation"] == "Continue monitoring"


def test_maintenance_roi_uses_configured_defaults_when_not_provided():
    from app.core.config import DEFAULT_MAINTENANCE_COST, DEFAULT_DOWNTIME_DAYS

    result = calculate_maintenance_roi(downtime_cost_per_day=1000, health_score=80)

    expected_loss = round(1000 * DEFAULT_DOWNTIME_DAYS, 2)
    expected_savings = round(
        max(0, expected_loss - DEFAULT_MAINTENANCE_COST), 2
    )
    assert result["maintenance_cost"] == DEFAULT_MAINTENANCE_COST
    assert result["potential_downtime_loss"] == expected_loss
    assert result["estimated_savings"] == expected_savings


# -----------------------------
# MAINTENANCE RECOMMENDATION
# (derives its CRITICAL/WARNING tiers from the single canonical classifier,
# app.services.risk_service.calculate_risk_level - see ML/MLOps audit,
# Immediate #3)
# -----------------------------

def test_maintenance_recommendation_75_to_80_percent_is_now_critical():
    """The actual bug being fixed: this function previously put CRITICAL at
    80%, while risk_service (and every other panel) calls 75-79.9%
    CRITICAL already. A machine must not be CRITICAL in one part of the
    app and only HIGH in another.
    """
    result = generate_maintenance_recommendation(
        probability=0.76, health_status="CRITICAL"
    )
    assert result["priority"] == "CRITICAL"
    assert result["recommended_window"] == "Immediate inspection required"


def test_maintenance_recommendation_critical_at_and_above_80_percent_unchanged():
    result = generate_maintenance_recommendation(
        probability=0.85, health_status="CRITICAL"
    )
    assert result["priority"] == "CRITICAL"
    assert result["recommended_action"] == (
        "Inspect machine components before next operating cycle."
    )


def test_maintenance_recommendation_high_tier_50_to_75_unchanged():
    result = generate_maintenance_recommendation(
        probability=0.60, health_status="WARNING"
    )
    assert result["priority"] == "HIGH"
    assert result["recommended_window"] == "Schedule maintenance within 7 days"
    assert result["recommended_action"] == (
        "Perform preventive inspection and check abnormal operating conditions."
    )


def test_maintenance_recommendation_medium_tier_20_to_50_unchanged():
    result = generate_maintenance_recommendation(
        probability=0.30, health_status="LOW"
    )
    assert result["priority"] == "MEDIUM"
    assert result["recommended_window"] == "Monitor and inspect within 30 days"
    assert result["recommended_action"] == (
        "Continue monitoring sensor trends and prepare preventive maintenance."
    )


def test_maintenance_recommendation_low_tier_below_20_unchanged():
    result = generate_maintenance_recommendation(
        probability=0.05, health_status="LOW"
    )
    assert result["priority"] == "LOW"
    assert result["recommended_window"] == "No immediate action required"
    assert result["recommended_action"] == "Continue normal operation."


def test_maintenance_recommendation_boundary_exactly_at_75_percent():
    result = generate_maintenance_recommendation(
        probability=0.75, health_status="CRITICAL"
    )
    assert result["priority"] == "CRITICAL"
