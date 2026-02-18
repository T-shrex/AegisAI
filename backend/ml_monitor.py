def get_ml_metrics(trigger_drift: bool = False):
    
    try:
        live_data = get_live_data(trigger_drift)

        drift = calculate_drift(live_data)

        preds = model.predict(live_data)
        actual = (live_data[:, 0] + live_data[:, 1] > 100).astype(int)
        accuracy = np.mean(preds == actual)

        status = "stable"
        if drift > 0.25:
            status = "drift_detected"

        return {
            "drift": round(float(drift), 3),
            "accuracy": round(float(accuracy), 3),
            "status": status
        }

    except Exception as e:
        # prevents API crash during demo
        return {
            "drift": 0.0,
            "accuracy": 0.0,
            "status": "error"
        }
# -----------------------------
# TEST RUN
# -----------------------------
if __name__ == "__main__":
    print("Normal:", get_ml_metrics(False))
    print("Drift :", get_ml_metrics(True))
