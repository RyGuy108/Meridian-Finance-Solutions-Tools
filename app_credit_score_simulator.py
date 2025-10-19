# app_credit_score_simulator.py
# Streamlit app — EDUCATIONAL-ONLY simulator to visualize how major factors may influence a score range.
# Factors: payment history, utilization, length of credit, new inquiries, credit mix.
# Outputs a pseudo-score (300–850), factor bars, guidance, and exports.
#
# NOTE: Real credit scoring models are proprietary. This is a teaching tool.

import io
import json
import math
import streamlit as st

st.set_page_config(page_title="Credit Score Impact Simulator", page_icon="💳", layout="centered")

st.title("💳 Credit Score Impact Simulator (Educational)")
st.caption("Understand the *directional* impact of key factors (not an actual score). Ranges reflect teaching weights, not any proprietary model.")
st.divider()

# Weights (roughly aligned with common education: PH 35%, Util 30%, Length 15%, New 10%, Mix 10)
WEIGHTS = {
    "payment": 0.35,
    "utilization": 0.30,
    "length": 0.15,
    "new": 0.10,
    "mix": 0.10,
}

def clamp01(x): return max(0.0, min(1.0, x))

def score_payment_history(on_time_pct: float):
    # 100% on-time -> 1.0; <90% drops sharply
    if on_time_pct >= 99: return 1.0
    if on_time_pct <= 80: return 0.2
    # interpolate 80..99
    return 0.2 + (on_time_pct - 80) / 19 * 0.8

def score_utilization(util_pct: float):
    # 0–9% ~ best, 10–29% good, 30–49% fair, 50–89% poor, 90%+ very poor
    if util_pct <= 9: return 1.0
    if util_pct <= 29: return 0.85
    if util_pct <= 49: return 0.6
    if util_pct <= 89: return 0.35
    return 0.15

def score_length(avg_years: float):
    # 9+ yrs best; 5–8 good; 2–4 fair; <2 poor
    if avg_years >= 9: return 1.0
    if avg_years >= 5: return 0.8
    if avg_years >= 2: return 0.55
    return 0.25

def score_new(inquiries_last_12m: int):
    # 0 best; 1 okay; 2–3 fair; 4–5 poor; 6+ very poor
    if inquiries_last_12m <= 0: return 1.0
    if inquiries_last_12m == 1: return 0.8
    if inquiries_last_12m <= 3: return 0.55
    if inquiries_last_12m <= 5: return 0.35
    return 0.2

def score_mix(open_accounts: int, has_installment: bool, has_revolving: bool):
    # Some variety helps: at least one revolving (credit card) and one installment (loan).
    variety = 1.0 if (has_installment and has_revolving) else 0.75 if (has_installment or has_revolving) else 0.4
    # Penalize too few accounts (0–1) and too many (>12) slightly
    if open_accounts <= 1:
        base = 0.5
    elif open_accounts <= 6:
        base = 0.9
    elif open_accounts <= 12:
        base = 0.8
    else:
        base = 0.6
    return clamp01(0.5 * base + 0.5 * variety)

def to_score_300_850(norm_0_1: float) -> int:
    return int(round(300 + norm_0_1 * (850 - 300)))

with st.form("credit_form"):
    col1, col2 = st.columns(2)
    with col1:
        on_time_pct = st.number_input("On-time payment rate (%)", min_value=0.0, max_value=100.0, value=100.0, step=1.0)
        util_pct = st.number_input("Credit utilization (%)", min_value=0.0, max_value=100.0, value=20.0, step=1.0,
                                   help="Total balances ÷ total limits × 100.")
        avg_age_years = st.number_input("Average age of accounts (years)", min_value=0.0, value=3.0, step=0.5)
    with col2:
        inquiries_12m = st.number_input("New hard inquiries (last 12 months)", min_value=0, value=0, step=1)
        open_accts = st.number_input("Open accounts (total)", min_value=0, value=3, step=1)
        has_install = st.checkbox("Has installment account (e.g., loan)?", value=True)
        has_revolv = st.checkbox("Has revolving account (e.g., credit card)?", value=True)

    show_breakdown = st.checkbox("Show factor breakdown bars", value=True)
    submitted = st.form_submit_button("Simulate")

if submitted:
    # Normalize factor scores 0..1
    s_pay = score_payment_history(on_time_pct)
    s_util = score_utilization(util_pct)
    s_len = score_length(avg_age_years)
    s_new = score_new(inquiries_12m)
    s_mix = score_mix(open_accts, has_install, has_revolv)

    # Weighted sum
    total_norm = (
        s_pay * WEIGHTS["payment"] +
        s_util * WEIGHTS["utilization"] +
        s_len * WEIGHTS["length"] +
        s_new * WEIGHTS["new"] +
        s_mix * WEIGHTS["mix"]
    )

    est_score = to_score_300_850(total_norm)

    st.subheader("Estimated Educational Score")
    a, b = st.columns([1,2])
    a.metric("Estimated Score", f"{est_score}")
    b.write(
        f"**Key inputs:** On-time {on_time_pct:.0f}%, Utilization {util_pct:.0f}%, Age {avg_age_years} yrs, "
        f"Inquiries {inquiries_12m}, Open accts {open_accts}."
    )
    st.caption("This is a teaching visualization — not an actual FICO®/VantageScore®. Exact scoring methods are proprietary.")

    if show_breakdown:
        try:
            import matplotlib.pyplot as plt
            factors = ["Payment (35%)","Utilization (30%)","Length (15%)","New (10%)","Mix (10%)"]
            vals = [s_pay, s_util, s_len, s_new, s_mix]
            fig, ax = plt.subplots(figsize=(6.8, 3.0))
            ax.barh(factors, vals)
            ax.set_xlim(0,1)
            ax.set_xlabel("Normalized factor score (0–1)")
            ax.set_title("Factor Strength (Educational)")
            for i,v in enumerate(vals):
                ax.text(v+0.02, i, f"{v:.2f}", va="center")
            st.pyplot(fig)
        except Exception:
            st.info("Install matplotlib to see the factor bars: `pip install matplotlib`")

    st.subheader("Guidance (Educational)")
    tips = []
    if on_time_pct < 99:
        tips.append("Payment history: set **auto-pay for minimums** to protect on-time rate.")
    if util_pct > 30:
        tips.append("Utilization: aim to keep **credit use <30%** of total limit; <10% is excellent.")
    if avg_age_years < 3:
        tips.append("Length of credit: avoid closing older accounts; time builds score.")
    if inquiries_12m >= 2:
        tips.append("New credit: **limit hard pulls**; rate-shop within short windows.")
    if not (has_install and has_revolv):
        tips.append("Credit mix: having **both a card and an installment loan** can help (not worth debt just for score).")
    if not tips:
        tips.append("Great fundamentals! Keep utilization low and payments 100% on time.")

    for t in tips:
        st.write(f"- {t}")

    # Export
    st.subheader("Export")
    payload = {
        "inputs": {
            "on_time_pct": on_time_pct,
            "utilization_pct": util_pct,
            "avg_age_years": avg_age_years,
            "inquiries_12m": inquiries_12m,
            "open_accounts": open_accts,
            "has_installment": has_install,
            "has_revolving": has_revolv,
        },
        "normalized_factor_scores": {
            "payment": round(s_pay, 3),
            "utilization": round(s_util, 3),
            "length": round(s_len, 3),
            "new": round(s_new, 3),
            "mix": round(s_mix, 3),
        },
        "weighted_total_norm": round(total_norm, 3),
        "estimated_educational_score": est_score,
        "disclaimer": "Teaching tool — not an actual credit score.",
    }
    st.download_button(
        "⬇️ Download JSON (results)",
        data=json.dumps(payload, indent=2).encode("utf-8"),
        file_name="credit_score_simulator_results.json",
        mime="application/json",
    )

    txt = io.StringIO()
    txt.write("MFS Credit Score Impact Simulator (Educational)\n")
    txt.write("----------------------------------------------\n")
    txt.write(f"Estimated score: {est_score}\n")
    txt.write(f"On-time: {on_time_pct:.0f}% | Utilization: {util_pct:.0f}% | Age: {avg_age_years:.1f} yrs | ")
    txt.write(f"Inquiries: {inquiries_12m} | Open accounts: {open_accts}\n")
    st.download_button("⬇️ Download Text Summary", data=txt.getvalue(), file_name="credit_score_simulator_summary.txt", mime="text/plain")
else:
    st.info("Enter your current stats and click **Simulate** to see an educational score range and factor guidance.")