# app_compound_interest.py
# Streamlit app — visualizes growth from principal + monthly contributions with compound interest.
# Outputs a growth chart, contributions vs. interest breakdown, table, and exports.

import io
import json
import math
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Compound Interest Visualizer", page_icon="📈", layout="centered")

st.title("📈 Compound Interest Visualizer")
st.caption("See how your money can grow over time with monthly contributions and compounding. Educational estimates only.")
st.divider()

with st.form("ci_form"):
    c1, c2 = st.columns(2)
    with c1:
        principal = st.number_input("Starting amount ($)", min_value=0.0, value=500.0, step=50.0)
        monthly_contrib = st.number_input("Monthly contribution ($)", min_value=0.0, value=100.0, step=10.0)
        years = st.number_input("Years to invest", min_value=1, max_value=60, value=10, step=1)
    with c2:
        annual_rate = st.number_input("Annual interest rate (%)", min_value=0.0, max_value=50.0, value=7.0, step=0.1)
        compounds_per_year = st.selectbox("Compounding frequency", ["Monthly (12)", "Quarterly (4)", "Annually (1)"], index=0)
        show_table = st.checkbox("Show detailed table", value=False)

    submitted = st.form_submit_button("Calculate")

def simulate_growth(principal, monthly_contrib, annual_rate_pct, years, n_compounds):
    """Return month-by-month history DataFrame with contributions, interest, and balance.
       Assumes contributions made monthly; interest compounds n_compounds/year."""
    months = int(years * 12)
    r = annual_rate_pct / 100.0
    r_per = r / n_compounds  # periodic rate for compounding
    history = []
    balance = principal
    total_contrib = principal
    total_interest = 0.0

    for m in range(0, months + 1):
        # record at the start of month m
        history.append({
            "Month": m,
            "Year": m / 12.0,
            "Contributions ($)": round(total_contrib, 2),
            "Interest Earned ($)": round(total_interest, 2),
            "Balance ($)": round(balance, 2),
        })

        if m == months:  # stop after recording last point
            break

        # Add monthly contribution at end of month
        balance += monthly_contrib
        total_contrib += monthly_contrib

        # Apply compounding for the month:
        # Convert monthly flow to equivalent periodic compounding
        # We simulate within the month as: if compounding monthly (12),
        # then 1 compound per month; if quarterly, approximate 1/3 per month, etc.
        # For simplicity, we compound once per month at rate r/12 (effective approx).
        # To honor n_compounds more closely, use effective monthly rate from nominal APR:
        r_month_eff = (1 + r / n_compounds) ** (n_compounds / 12.0) - 1
        interest = balance * r_month_eff
        balance += interest
        total_interest += interest

    return pd.DataFrame(history)

if submitted:
    n_map = {"Monthly (12)": 12, "Quarterly (4)": 4, "Annually (1)": 1}
    n_compounds = n_map[compounds_per_year]

    hist = simulate_growth(
        principal=principal,
        monthly_contrib=monthly_contrib,
        annual_rate_pct=annual_rate,
        years=years,
        n_compounds=n_compounds,
    )

    final_row = hist.iloc[-1]
    final_balance = float(final_row["Balance ($)"])
    total_contrib = float(final_row["Contributions ($)"])
    total_interest = float(final_row["Interest Earned ($)"])

    st.subheader("Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Final Balance", f"${final_balance:,.2f}")
    col2.metric("Total Contributed", f"${total_contrib:,.2f}")
    col3.metric("Total Interest Earned", f"${total_interest:,.2f}")

    # Chart
    try:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(6.5, 3.8))
        ax.plot(hist["Month"], hist["Balance ($)"], label="Balance", linewidth=2)
        ax.plot(hist["Month"], hist["Contributions ($)"], label="Contributions", linewidth=2)
        ax.fill_between(hist["Month"], hist["Contributions ($)"], hist["Balance ($)"], alpha=0.15, label="Interest Area")
        ax.set_xlabel("Month")
        ax.set_ylabel("Amount ($)")
        ax.set_title("Growth Over Time")
        ax.grid(True, alpha=0.25)
        ax.legend()
        st.pyplot(fig)
    except Exception:
        st.info("Install matplotlib to see the growth chart: `pip install matplotlib`")

    # Optional table
    if show_table:
        st.dataframe(hist, use_container_width=True, hide_index=True)

    # Export
    st.write("**Export**")
    st.download_button(
        "⬇️ Download CSV (history)",
        data=hist.to_csv(index=False).encode("utf-8"),
        file_name="compound_interest_history.csv",
        mime="text/csv",
    )
    payload = {
        "inputs": {
            "principal": principal,
            "monthly_contribution": monthly_contrib,
            "annual_rate_pct": annual_rate,
            "years": years,
            "compounding": n_compounds,
        },
        "outputs": {
            "final_balance": round(final_balance, 2),
            "total_contributed": round(total_contrib, 2),
            "total_interest": round(total_interest, 2),
        },
    }
    st.download_button(
        "⬇️ Download JSON (summary)",
        data=json.dumps(payload, indent=2).encode("utf-8"),
        file_name="compound_interest_summary.json",
        mime="application/json",
    )

    # Text summary
    summary = io.StringIO()
    summary.write("MFS Compound Interest Summary\n")
    summary.write("-----------------------------\n")
    summary.write(f"Principal: ${principal:,.2f}\n")
    summary.write(f"Monthly contribution: ${monthly_contrib:,.2f}\n")
    summary.write(f"APR: {annual_rate:.2f}% | Years: {years}\n")
    summary.write(f"Compounding periods/year: {n_compounds}\n")
    summary.write(f"Final balance: ${final_balance:,.2f}\n")
    summary.write(f"Total contributed: ${total_contrib:,.2f}\n")
    summary.write(f"Total interest: ${total_interest:,.2f}\n")
    st.download_button("⬇️ Download Text Summary", data=summary.getvalue(), file_name="compound_interest_summary.txt", mime="text/plain")
else:
    st.info("Enter your inputs and click **Calculate** to visualize growth.")