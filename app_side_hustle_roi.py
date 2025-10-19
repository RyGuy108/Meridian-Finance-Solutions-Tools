# app_side_hustle_roi.py
# Streamlit app — evaluate a side hustle: revenue, costs, net profit, break-even weeks, and hourly rate.
# Includes cumulative profit chart and export options.

import io
import json
import math
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Side Hustle ROI", page_icon="🚀", layout="centered")

st.title("🚀 Side Hustle ROI Calculator")
st.caption("Estimate profitability, break-even time, and effective hourly rate for a side hustle or micro-business. Educational tool for planning.")

st.divider()

with st.form("roi_form"):
    st.subheader("Inputs")
    c1, c2 = st.columns(2)
    with c1:
        price_per_unit = st.number_input("Price per unit/service ($)", min_value=0.0, value=25.0, step=1.0)
        units_per_week = st.number_input("Expected units per week", min_value=0.0, value=10.0, step=1.0)
        hours_per_week = st.number_input("Hours worked per week", min_value=0.0, value=8.0, step=0.5)
        startup_cost = st.number_input("One-time startup cost ($)", min_value=0.0, value=200.0, step=10.0,
                                       help="Equipment, licenses, initial supplies.")
    with c2:
        variable_cost_per_unit = st.number_input("Variable cost per unit ($)", min_value=0.0, value=5.0, step=0.5,
                                                 help="Materials, transaction fees per sale.")
        weekly_fixed_costs = st.number_input("Weekly fixed costs ($)", min_value=0.0, value=15.0, step=1.0,
                                             help="Subscriptions, transportation, booth fees, etc.")
        weeks_projection = st.number_input("Projection horizon (weeks)", min_value=4, value=26, step=1)
        show_table = st.checkbox("Show weekly detail table", value=False)

    submitted = st.form_submit_button("Calculate")

def compute_weekly(price, units, var_cost, fixed_cost):
    revenue = price * units
    variable_total = var_cost * units
    gross_profit = revenue - variable_total
    net_profit = gross_profit - fixed_cost
    return revenue, variable_total, gross_profit, net_profit

def build_projection(startup_cost, price, units, var_cost, fixed_cost, weeks):
    rows = []
    cumulative = -startup_cost
    for w in range(1, weeks + 1):
        revenue, variable_total, gross_profit, net_profit = compute_weekly(price, units, var_cost, fixed_cost)
        cumulative += net_profit
        rows.append({
            "Week": w,
            "Revenue ($)": round(revenue, 2),
            "Variable Costs ($)": round(variable_total, 2),
            "Fixed Costs ($)": round(fixed_cost, 2),
            "Net Profit ($)": round(net_profit, 2),
            "Cumulative Profit ($)": round(cumulative, 2),
        })
    df = pd.DataFrame(rows)
    # Break-even: first week cumulative >= 0
    be_week = int(df.loc[df["Cumulative Profit ($)"] >= 0, "Week"].min()) if (df["Cumulative Profit ($)"] >= 0).any() else None
    return df, be_week

if submitted:
    revenue_wk, var_total_wk, gross_profit_wk, net_profit_wk = compute_weekly(
        price_per_unit, units_per_week, variable_cost_per_unit, weekly_fixed_costs
    )
    effective_hourly = (net_profit_wk / hours_per_week) if hours_per_week > 0 else 0.0

    proj, break_even_week = build_projection(
        startup_cost=startup_cost,
        price=price_per_unit,
        units=units_per_week,
        var_cost=variable_cost_per_unit,
        fixed_cost=weekly_fixed_costs,
        weeks=int(weeks_projection),
    )

    st.subheader("Weekly Summary")
    a, b, c, d = st.columns(4)
    a.metric("Revenue / week", f"${revenue_wk:,.2f}")
    b.metric("Net Profit / week", f"${net_profit_wk:,.2f}")
    c.metric("Eff. Hourly Rate", f"${effective_hourly:,.2f}/hr")
    if break_even_week is None:
        d.metric("Break-even", "Not reached", f"{weeks_projection} wks horizon")
    else:
        d.metric("Break-even", f"Week {break_even_week}")

    # Chart: cumulative profit
    try:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(6.5, 3.8))
        ax.plot(proj["Week"], proj["Cumulative Profit ($)"], linewidth=2)
        ax.axhline(0, color="tab:red", linestyle="--", label="Break-even line")
        ax.set_xlabel("Week")
        ax.set_ylabel("Cumulative Profit ($)")
        ax.set_title("Cumulative Profit Projection")
        ax.grid(True, alpha=0.25)
        ax.legend()
        st.pyplot(fig)
    except Exception:
        st.info("Install matplotlib to see the cumulative profit chart: `pip install matplotlib`")

    if show_table:
        st.dataframe(proj, use_container_width=True, hide_index=True)

    # Export
    st.write("**Export**")
    st.download_button(
        "⬇️ Download CSV (projection)",
        data=proj.to_csv(index=False).encode("utf-8"),
        file_name="side_hustle_projection.csv",
        mime="text/csv",
    )
    payload = {
        "inputs": {
            "price_per_unit": price_per_unit,
            "units_per_week": units_per_week,
            "hours_per_week": hours_per_week,
            "startup_cost": startup_cost,
            "variable_cost_per_unit": variable_cost_per_unit,
            "weekly_fixed_costs": weekly_fixed_costs,
            "weeks_projection": int(weeks_projection),
        },
        "outputs": {
            "revenue_per_week": round(revenue_wk, 2),
            "net_profit_per_week": round(net_profit_wk, 2),
            "effective_hourly_rate": round(effective_hourly, 2),
            "break_even_week": break_even_week,
        },
    }
    st.download_button(
        "⬇️ Download JSON (summary)",
        data=json.dumps(payload, indent=2).encode("utf-8"),
        file_name="side_hustle_roi_summary.json",
        mime="application/json",
    )

    txt = io.StringIO()
    txt.write("MFS Side Hustle ROI Summary\n")
    txt.write("---------------------------\n")
    txt.write(f"Price/unit: ${price_per_unit:,.2f}\n")
    txt.write(f"Units/week: {units_per_week}\n")
    txt.write(f"Variable cost/unit: ${variable_cost_per_unit:,.2f}\n")
    txt.write(f"Fixed costs/week: ${weekly_fixed_costs:,.2f}\n")
    txt.write(f"Startup cost: ${startup_cost:,.2f}\n")
    txt.write(f"Revenue/week: ${revenue_wk:,.2f}\n")
    txt.write(f"Net profit/week: ${net_profit_wk:,.2f}\n")
    txt.write(f"Effective hourly rate: ${effective_hourly:,.2f}/hr\n")
    txt.write(f"Break-even week: {break_even_week if break_even_week is not None else 'Not reached in horizon'}\n")
    st.download_button("⬇️ Download Text Summary", data=txt.getvalue(), file_name="side_hustle_roi_summary.txt", mime="text/plain")
else:
    st.info("Enter your pricing, costs, and time, then click **Calculate**.")