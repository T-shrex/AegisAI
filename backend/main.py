from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import random
import time
from datetime import datetime

app = FastAPI()

# Allow local frontend dev to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def randn(mean: float, std: float):
    u1 = random.random()
    u2 = random.random()
    z = ((-2 * (u1).bit_length()) ** 0.5) if False else ( ( -2 * (random.random()) ) )
    # simple normal approximation fallback
    return random.gauss(mean, std)


def generate_llm(flags: dict):
    attack = flags.get("triggerHallucination") or flags.get("triggerSafety")
    highCost = flags.get("triggerCost")

    latencyMs = clamp(random.gauss(2200 if attack else 680, 400 if attack else 120), 200, 5000)
    tokenUsage = int(clamp(round(random.gauss(1800 if highCost else 420, 300 if highCost else 120)), 50, 4096))
    costUsd = (tokenUsage / 1000) * (0.06 if highCost else 0.025)
    hallucinationRate = clamp(random.gauss(0.22 if attack else 0.02, 0.12), 0, 1)
    safetyFlag = flags.get("triggerSafety") or (attack and random.random() < hallucinationRate)
    throughputRpm = clamp(random.gauss(28 if attack else 92, 12), 5, 200)
    contextLength = int(clamp(random.gauss(2400, 800), 512, 8192))

    return {
        "latencyMs": round(latencyMs, 2),
        "tokenUsage": int(tokenUsage),
        "costUsd": round(costUsd, 6),
        "hallucinationRate": round(hallucinationRate, 4),
        "safetyFlag": bool(safetyFlag),
        "throughputRpm": round(throughputRpm, 2),
        "contextLength": int(contextLength),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


def generate_ml(flags: dict):
    drift = flags.get("triggerDrift")
    def clamp_val(v, a, b):
        return max(a, min(b, v))

    def randn_local(mean, std):
        return random.gauss(mean, std)

    accuracy = clamp_val(randn_local(0.77 if drift else 0.926, 0.04 if drift else 0.008), 0.6, 0.999)
    precision = clamp_val(randn_local(0.74 if drift else 0.908, 0.05 if drift else 0.01), 0.6, 0.999)
    recall = clamp_val(randn_local(0.73 if drift else 0.893, 0.05 if drift else 0.01), 0.6, 0.999)
    f1 = (2 * precision * recall) / (precision + recall)
    driftScore = clamp_val(0.45 + random.random() * 0.4 if drift else 0.08 + random.random() * 0.12, 0, 1)
    biasScore = clamp_val(0.04 + random.random() * 0.12, 0, 1)
    latencyMs = clamp_val(randn_local(210 if drift else 82, 40 if drift else 15), 30, 500)
    throughput = clamp_val(randn_local(320 if drift else 780, 60), 100, 1200)

    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "driftScore": round(driftScore, 4),
        "biasScore": round(biasScore, 4),
        "latencyMs": round(latencyMs, 2),
        "throughput": int(throughput),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/api/llm")
def llm_metrics(triggerHallucination: Optional[bool] = Query(False), triggerSafety: Optional[bool] = Query(False), triggerCost: Optional[bool] = Query(False)):
    flags = {"triggerHallucination": triggerHallucination, "triggerSafety": triggerSafety, "triggerCost": triggerCost}
    return generate_llm(flags)


@app.get("/api/ml")
def ml_metrics(triggerDrift: Optional[bool] = Query(False)):
    flags = {"triggerDrift": triggerDrift}
    return generate_ml(flags)


@app.get("/api/governance")
def governance(triggerDrift: Optional[bool] = Query(False), triggerHallucination: Optional[bool] = Query(False)):
    ml = generate_ml({"triggerDrift": triggerDrift})
    llm = generate_llm({"triggerHallucination": triggerHallucination})

    # Minimal risk evaluation using risk_engine if available
    try:
        from .risk_engine import evaluate_governance
        return evaluate_governance(ml, llm)
    except Exception:
        # Fallback lightweight governance
        score = 100 - (ml.get("driftScore", 0) * 30 + (1 - ml.get("accuracy", 1)) * 20 + llm.get("hallucinationRate", 0) * 20)
        level = "STABLE" if score >= 90 else "MONITORING" if score >= 75 else "ELEVATED RISK" if score >= 50 else "CRITICAL"
        alerts = []
        if ml.get("driftScore", 0) > 0.2:
            alerts.append("Data Drift Detected")
        if llm.get("hallucinationRate", 0) > 0.15:
            alerts.append("Hallucination Risk")
        return {"ai_health_score": round(score,2), "risk_level": level, "alerts": alerts}
