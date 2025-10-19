# app_emergency_fund.py
# Streamlit app — emergency fund target (3–6 months), time-to-target projection with monthly compounding, chart, and exports.

import math
import io
import json
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Emergency Fund Target", page_icon="🛟", layout="centered")

st.title("🛟 Emergency Fund Target Calculator")
st.caption("Figure out how much to save for emergencies and how long it may take to reach your goal. Educational estimates only.")

st.divider()
with st.form("ef_form"):
    c1, c2 = st.columns(2)
    with c1:
        monthly_expenses = st.number_input("Essential monthly expenses ($)", min_value=0.0, value=1200.0, step=50.0,
                                           help="Rent, food, transportation, utilities, minimum debt payments, etc.")
        months_cover = st.slider("Months of coverage (goal)", min_value=1, max_value=12, value=3,
                                 help="Common guidance is 3–6 months.")
        annual_yield = st.number_input("Annual interest/yield (%)", min_value=0.0, value=0.5, step=0.1,
                                       help="High-yield savings may earn ~0.5%–5% depending on market conditions.")
    with c2:
        current_savings = st.number_input("Current emergency savings ($)", min_value=0.0, value=100.0, step=50.0)
        monthly_contrib = st.number_input("Monthly contribution ($)", min_value=0.0, value=150.0, step=25.0)
        max_months = st.number_input("Projection limit (months)", min_value=1, value=120, step=12,
                                     help="How far to simulate for time-to-goal.")
    submitted = st.form_submit_button("Calculate")

def simulate_time_to_target(start, monthly_add, target, r_annual_pct, max_months=120):
    """Returns (months_needed, history_df). Compounds monthly: balance = balance*(1+r_m) + monthly_add."""
    r_m = r_annual_pct / 100.0 / 12.0
    bal = start
    history = []
    for m in range(0, max_months + 1):
        history.append({"Month": m, "Balance": round(bal, 2)})
        if bal >= target:
            return m, pd.DataFrame(history)
        # next month
        bal = bal * (1 + r_m) + monthly_add
    # If not reached in the horizon:
    return None, pd.DataFrame(history)

if submitted:
    target_amount = round(monthly_expenses * months_cover, 2)
    shortfall = max(0.0, target_amount - current_savings)

    st.subheader("Your Target")
    colA, colB, colC = st.columns(3)
    colA.metric("Target Amount", f"${target_amount:,.2f}", f"{months_cover} months")
    colB.metric("Current Savings", f"${current_savings:,.2f}")
    colC.metric("Shortfall", f"${shortfall:,.2f}")

    # Quick reference for 3 and 6 months
    st.write("**Common Benchmarks (for reference):**")
    c1, c2 = st.columns(2)
    c1.info(f"3 months: ${monthly_expenses * 3:,.2f}")
    c2.info(f"6 months: ${monthly_expenses * 6:,.2f}")

    # Time-to-target simulation
    months_needed, hist = simulate_time_to_target(
        start=current_savings,
        monthly_add=monthly_contrib,
        target=target_amount,
        r_annual_pct=annual_yield,
        max_months=int(max_months),
    )

    if months_needed is None:
        st.warning(f"With the current plan, you won't reach the target within {int(max_months)} months. Try increasing your monthly contribution.")
    else:
        st.success(f"Estimated time to target: **{months_needed} month(s)** at ${monthly_contrib:,.2f}/mo with {annual_yield:.2f}% annual yield.")

    # Chart
    try:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(6.2, 3.6))
        ax.plot(hist["Month"], hist["Balance"], linewidth=2)
        ax.axhline(y=target_amount, color="tab:red", linestyle="--", label="Target")
        ax.set_xlabel("Month")
        ax.set_ylabel("Balance ($)")
        ax.set_title("Emergency Fund Growth Projection")
        ax.legend()
        ax.grid(True, alpha=0.25)
        st.pyplot(fig)
    except Exception:
        st.info("Install matplotlib to see the projection chart: `pip install matplotlib`")

    # Table & exports
    st.dataframe(hist, use_container_width=True, hide_index=True)

    payload = {
        "inputs": {
            "monthly_expenses": monthly_expenses,
            "months_cover": months_cover,
            "annual_yield_pct": annual_yield,
            "current_savings": current_savings,
            "monthly_contribution": monthly_contrib,
            "projection_limit_months": int(max_months),
        },
        "outputs": {
            "target_amount": target_amount,
            "shortfall": shortfall,
            "months_needed": months_needed,
        },
    }

    st.write("**Export**")
    st.download_button(
        "⬇️ Download CSV (projection)",
        data=hist.to_csv(index=False).encode("utf-8"),
        file_name="emergency_fund_projection.csv",
        mime="text/csv",
    )
    st.download_button(
        "⬇️ Download JSON (summary)",
        data=json.dumps(payload, indent=2).encode("utf-8"),
        file_name="emergency_fund_summary.json",
        mime="application/json",
    )

    # Text summary
    summary = io.StringIO()
    summary.write("MFS Emergency Fund Summary\n")
    summary.write("--------------------------\n")
    summary.write(f"Monthly expenses: ${monthly_expenses:,.2f}\n")
    summary.write(f"Goal coverage: {months_cover} months\n")
    summary.write(f"Target amount: ${target_amount:,.2f}\n")
    summary.write(f"Current savings: ${current_savings:,.2f}\n")
    summary.write(f"Monthly contribution: ${monthly_contrib:,.2f}\n")
    summary.write(f"Annual yield: {annual_yield:.2f}%\n")
    if months_needed is None:
        summary.write(f"Time to target: > {int(max_months)} months (increase contributions to reach target sooner)\n")
    else:
        summary.write(f"Estimated time to target: {months_needed} month(s)\n")
    st.download_button("⬇️ Download Text Summary", data=summary.getvalue(), file_name="emergency_fund_summary.txt", mime="text/plain")
else:
    st.info("Enter your expenses, goal, and saving plan, then click **Calculate**.")