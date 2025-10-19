# app_savings_goal_tracker.py
# Streamlit app — calculates time to reach a savings goal with monthly contributions and optional interest.
# Shows timeline chart, month-by-month table, and export options.

import io
import json
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Savings Goal Tracker", page_icon="🎯", layout="centered")

st.title("🎯 Savings Goal Tracker")
st.caption("How long will it take to hit your savings goal? Change contributions and see the timeline update. Educational estimates only.")
st.divider()

with st.form("sg_form"):
    c1, c2 = st.columns(2)
    with c1:
        goal_amount = st.number_input("Goal amount ($)", min_value=1.0, value=2000.0, step=50.0)
        starting_balance = st.number_input("Starting balance ($)", min_value=0.0, value=200.0, step=25.0)
        monthly_contrib = st.number_input("Monthly contribution ($)", min_value=0.0, value=150.0, step=25.0)
    with c2:
        annual_yield = st.number_input("Annual interest/yield (%)", min_value=0.0, value=1.0, step=0.1,
                                       help="Optional — if funds are in a savings account that earns interest.")
        max_months = st.number_input("Projection limit (months)", min_value=1, value=120, step=12)
        show_table = st.checkbox("Show detailed table", value=False)

    submitted = st.form_submit_button("Calculate")

def simulate_to_goal(start, monthly_add, goal, r_annual_pct, max_months=120):
    """Simulate monthly contributions + monthly effective compounding until goal or horizon.
       Returns (months_needed or None, DataFrame with Month/Balance/Contrib/Interest)."""
    r_month_eff = (1 + (r_annual_pct / 100.0) / 12.0) ** 1 - 1  # nominal to monthly effective
    bal = start
    history = []
    for m in range(0, max_months + 1):
        history.append({"Month": m, "Balance ($)": round(bal, 2)})
        if bal >= goal:
            return m, pd.DataFrame(history)

        # add monthly contribution
        bal += monthly_add
        # apply monthly interest
        interest = bal * r_month_eff
        bal += interest
    return None, pd.DataFrame(history)

if submitted:
    months_needed, hist = simulate_to_goal(
        start=starting_balance,
        monthly_add=monthly_contrib,
        goal=goal_amount,
        r_annual_pct=annual_yield,
        max_months=int(max_months),
    )

    shortfall = max(0.0, goal_amount - starting_balance)

    st.subheader("Summary")
    cA, cB, cC = st.columns(3)
    cA.metric("Goal", f"${goal_amount:,.2f}")
    cB.metric("Starting", f"${starting_balance:,.2f}")
    cC.metric("Shortfall", f"${shortfall:,.2f}")

    if months_needed is None:
        st.warning(f"With the current plan, you won't reach the goal within {int(max_months)} months. Try increasing the monthly contribution.")
    else:
        st.success(f"Estimated time to reach your goal: **{months_needed} month(s)** at ${monthly_contrib:,.2f}/mo with {annual_yield:.2f}% annual yield.")

    # Chart
    try:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(6.2, 3.6))
        ax.plot(hist["Month"], hist["Balance ($)"], linewidth=2)
        ax.axhline(y=goal_amount, color="tab:red", linestyle="--", label="Goal")
        ax.set_xlabel("Month")
        ax.set_ylabel("Balance ($)")
        ax.set_title("Savings Progress Projection")
        ax.grid(True, alpha=0.25)
        ax.legend()
        st.pyplot(fig)
    except Exception:
        st.info("Install matplotlib to see the projection chart: `pip install matplotlib`")

    if show_table:
        st.dataframe(hist, use_container_width=True, hide_index=True)

    # Exports
    st.write("**Export**")
    st.download_button(
        "⬇️ Download CSV (projection)",
        data=hist.to_csv(index=False).encode("utf-8"),
        file_name="savings_goal_projection.csv",
        mime="text/csv",
    )
    payload = {
        "inputs": {
            "goal_amount": goal_amount,
            "starting_balance": starting_balance,
            "monthly_contribution": monthly_contrib,
            "annual_yield_pct": annual_yield,
            "projection_limit_months": int(max_months),
        },
        "outputs": {
            "months_needed": months_needed,
        },
    }
    st.download_button(
        "⬇️ Download JSON (summary)",
        data=json.dumps(payload, indent=2).encode("utf-8"),
        file_name="savings_goal_summary.json",
        mime="application/json",
    )

    summary = io.StringIO()
    summary.write("MFS Savings Goal Summary\n")
    summary.write("------------------------\n")
    summary.write(f"Goal amount: ${goal_amount:,.2f}\n")
    summary.write(f"Starting balance: ${starting_balance:,.2f}\n")
    summary.write(f"Monthly contribution: ${monthly_contrib:,.2f}\n")
    summary.write(f"Annual yield: {annual_yield:.2f}%\n")
    if months_needed is None:
        summary.write(f"Time to goal: > {int(max_months)} months (increase contribution to reach sooner)\n")
    else:
        summary.write(f"Estimated time to goal: {months_needed} month(s)\n")
    st.download_button("⬇️ Download Text Summary", data=summary.getvalue(), file_name="savings_goal_summary.txt", mime="text/plain")
else:
    st.info("Enter your goal and plan, then click **Calculate** to see your timeline.")