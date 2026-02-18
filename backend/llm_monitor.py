import time
import random

# -----------------------------
# Fake LLM response generator
# -----------------------------

SAFE_RESPONSES = [
    "Your account balance is ₹12,540.",
    "Your loan application is under review.",
    "Transaction completed successfully.",
    "Your KYC is verified."
]

UNSAFE_RESPONSES = [
    "Your password is 123456",
    "Send OTP here to verify",
    "I can bypass bank security",
    "Share your PIN for faster service"
]


# -----------------------------
# Simulate chatbot call
# -----------------------------

def call_fake_llm(trigger_attack=False):

    start = time.time()

    # simulate model thinking delay
    time.sleep(random.uniform(0.3, 2.5))

    latency = time.time() - start

    if trigger_attack:
        response = random.choice(UNSAFE_RESPONSES)
        hallucination = 1
    else:
        response = random.choice(SAFE_RESPONSES)
        hallucination = 0

    tokens = random.randint(50, 500)

    return latency, tokens, hallucination, response


# -----------------------------
# FINAL FUNCTION FOR SYSTEM
# -----------------------------

def get_llm_metrics(trigger_attack: bool = False):

    try:
        latency, tokens, hallucination, response = call_fake_llm(trigger_attack)

        return {
            "latency": round(float(latency), 3),
            "tokens": int(tokens),
            "hallucination": int(hallucination)
        }

    except Exception:
        return {
            "latency": 0.0,
            "tokens": 0,
            "hallucination": 1
        }


# -----------------------------
# TEST RUN
# -----------------------------
if __name__ == "__main__":
    print("Normal:", get_llm_metrics(False))
    print("Attack :", get_llm_metrics(True))
