"""
AegisAI Risk & Governance Engine
Owner: Person 3

This module:
- Combines ML + LLM metrics
- Computes AI Health Score (0–100)
- Generates Risk Level
- Generates Alert Flags
"""

# -------------------------------
# CONFIGURATION (Adjustable Weights)
# -------------------------------

DRIFT_WEIGHT = 30
HALLUCINATION_WEIGHT = 20
LATENCY_WEIGHT = 10
COST_WEIGHT = 20
ACCURACY_WEIGHT = 20  # penalizes low accuracy


# -------------------------------
# RISK SCORE CALCULATION
# -------------------------------

def compute_ai_health(ml_metrics: dict, llm_metrics: dict) -> float:
    """
    Calculates unified AI Health Score using enterprise risk modeling.
    Returns value between 0–100.
    Thresholds calibrated for banking & financial AI systems.
    """

    drift = ml_metrics.get("drift", 0)
    accuracy = ml_metrics.get("accuracy", 1)

    latency = llm_metrics.get("latency", 0)
    tokens = llm_metrics.get("tokens", 0)
    hallucination = llm_metrics.get("hallucination", 0)

    # Normalize values against risk thresholds
    drift_risk = min(drift / 0.3, 1)          # 0.3 PSI = severe drift
    accuracy_risk = 1 - accuracy              # lower accuracy = higher risk
    latency_risk = min(latency / 3, 1)        # >3 sec risky
    cost_risk = min(tokens / 1500, 1)         # >1500 tokens risky
    hallucination_risk = hallucination        # 0 or 1

    raw_penalty = (
        drift_risk * 25 +
        accuracy_risk * 25 +
        hallucination_risk * 20 +
        latency_risk * 5 +
        cost_risk * 10
    )

    score = 100 - raw_penalty
    score = max(0, min(score, 100))

    return round(score, 2)


# -------------------------------
# RISK CLASSIFICATION
# -------------------------------

def classify_risk(score: float) -> str:
    """
    Converts numeric score into enterprise governance risk label.
    Calibrated for banking and financial AI systems.
    """

    if score >= 90:
        return "STABLE"
    elif score >= 75:
        return "MONITORING"
    elif score >= 50:
        return "ELEVATED RISK"
    else:
        return "CRITICAL – GOVERNANCE ACTION REQUIRED"


# -------------------------------
# ALERT GENERATION
# -------------------------------

def generate_alerts(ml_metrics: dict, llm_metrics: dict) -> list:
    """
    Returns list of active governance alerts.
    """

    alerts = []

    if ml_metrics.get("drift", 0) > 0.2:
        alerts.append("⚠️ Data Drift Detected")

    if ml_metrics.get("accuracy", 1) < 0.8:
        alerts.append("⚠️ Model Accuracy Degradation")

    if llm_metrics.get("hallucination", 0) == 1:
        alerts.append("⚠️ Hallucination Risk")

    if llm_metrics.get("latency", 0) > 2:
        alerts.append("⚠️ High Latency")

    if llm_metrics.get("tokens", 0) > 1200:
        alerts.append("⚠️ Token Cost Spike")

    return alerts


# -------------------------------
# MASTER GOVERNANCE FUNCTION
# -------------------------------

def evaluate_governance(ml_metrics: dict, llm_metrics: dict) -> dict:
    """
    Unified governance output.
    Used by main.py
    """

    score = compute_ai_health(ml_metrics, llm_metrics)
    risk_label = classify_risk(score)
    alerts = generate_alerts(ml_metrics, llm_metrics)

    return {
        "ai_health_score": score,
        "risk_level": risk_label,
        "alerts": alerts
    }


# -------------------------------
# SCORE EXPLAINABILITY
# -------------------------------

def explain_score_breakdown(ml_metrics: dict, llm_metrics: dict) -> dict:
    """
    Returns detailed breakdown of score components for governance transparency.
    Shows contribution of each factor to the overall risk calculation.
    """
    return {
        "drift_impact": ml_metrics.get("drift", 0) * 30,
        "accuracy_impact": (1 - ml_metrics.get("accuracy", 1)) * 20,
        "hallucination_impact": llm_metrics.get("hallucination", 0) * 20,
        "latency_impact": llm_metrics.get("latency", 0) * 10,
        "cost_impact": (llm_metrics.get("tokens", 0)/1000) * 20
    }
