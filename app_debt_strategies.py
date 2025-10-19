# app_debt_strategies.py
# Streamlit app — compare Snowball (smallest balance first) vs. Avalanche (highest APR first).
# Accepts multiple debts, a total monthly budget, and simulates month-by-month until payoff.
# Outputs payoff time, total interest, timeline chart, detailed table, and exports.
#
# Educational approximation only.

import io
import json
from dataclasses import dataclass, asdict
from typing import List, Literal, Tuple
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Debt Snowball vs. Avalanche", page_icon="🧊⛰️", layout="centered")

st.title("🧊⛰️ Debt Payoff Planner — Snowball vs. Avalanche")
st.caption("Enter your debts and a monthly payoff budget to compare strategies. Educational estimate — real statements may vary.")
st.divider()

Strategy = Literal["Snowball (Smallest Balance First)", "Avalanche (Highest APR First)"]

@dataclass
class Debt:
    name: str
    balance: float
    apr_pct: float
    min_pay: float

def monthly_rate(apr_pct: float) -> float:
    return apr_pct / 100.0 / 12.0

def order_debts(debts: List[Debt], strategy: Strategy) -> List[int]:
    # return indices in the order to target extra payments
    if strategy.startswith("Snowball"):
        # smallest balance first
        return sorted(range(len(debts)), key=lambda i: debts[i].balance)
    else:
        # highest APR first
        return sorted(range(len(debts)), key=lambda i: debts[i].apr_pct, reverse=True)

def simulate(debts_in: List[Debt], monthly_budget: float, strategy: Strategy, extra_rollover: bool=True) -> Tuple[pd.DataFrame, dict]:
    # Deep copy debts to avoid mutation
    debts = [Debt(d.name, float(d.balance), float(d.apr_pct), float(d.min_pay)) for d in debts_in]
    n = len(debts)
    assert n > 0
    # Basic validation
    for d in debts:
        if d.balance < 0 or d.min_pay < 0 or d.apr_pct < 0:
            raise ValueError("Inputs must be non-negative.")
    if monthly_budget <= 0:
        raise ValueError("Monthly budget must be > 0.")

    # Pre-check: sum of minimums cannot exceed monthly budget
    min_sum = sum(d.min_pay for d in debts)
    if min_sum > monthly_budget:
        raise ValueError(f"Monthly budget (${monthly_budget:,.2f}) is less than total minimum payments (${min_sum:,.2f}).")

    # Setup
    order = order_debts(debts, strategy)
    month = 0
    rows = []
    total_interest = 0.0
    paid_off_month = {i: None for i in range(n)}

    # Continue until all balances are ~0
    while sum(d.balance > 0.005 for d in debts) > 0 and month < 1200:  # 100 years safety
        month += 1
        remaining_budget = monthly_budget

        # 1) Accrue interest first (most statements accrue then payment)
        interests = []
        for i, d in enumerate(debts):
            if d.balance <= 0:
                interests.append(0.0)
                continue
            r = monthly_rate(d.apr_pct)
            interest = d.balance * r
            d.balance += interest
            interests.append(interest)

        # 2) Pay minimums
        payments = [0.0] * n
        for i, d in enumerate(debts):
            if d.balance <= 0:
                continue
            pay = min(d.min_pay, d.balance)
            payments[i] += pay
            d.balance -= pay
            remaining_budget -= pay

        # 3) Direct all extra to current target debt (based on order)
        #    If target is paid off, move to next.
        if remaining_budget > 0:
            for idx in order:
                if debts[idx].balance > 0.005:
                    extra = min(remaining_budget, debts[idx].balance)
                    payments[idx] += extra
                    debts[idx].balance -= extra
                    remaining_budget -= extra
                    break

        # 4) Mark payoffs and (optionally) roll over freed minimums (implicitly handled each loop)
        for i, d in enumerate(debts):
            if d.balance <= 0.005 and paid_off_month[i] is None:
                paid_off_month[i] = month
                d.balance = 0.0

        # 5) Tally interest this month
        total_interest += sum(interests)

        # Record snapshot
        snapshot = {
            "Month": month,
            "Remaining Budget ($)": round(remaining_budget, 2),
            "Total Interest Accrued To Date ($)": round(total_interest, 2),
        }
        for i, d in enumerate(debts):
            snapshot[f"{d.name} — Balance ($)"] = round(d.balance, 2)
            snapshot[f"{d.name} — Paid This Month ($)"] = round(payments[i], 2)
        rows.append(snapshot)

    df = pd.DataFrame(rows)
    result = {
        "months": month,
        "total_interest": round(total_interest, 2),
        "paid_off_months": {debts[i].name: paid_off_month[i] for i in range(n)},
    }
    return df, result

# ---- UI ----
with st.form("debts_form"):
    st.subheader("Your Debts")
    st.caption("Add each debt with balance, APR, and minimum. Then set your total monthly payoff budget.")

    # Default 3 rows; allow user to change count
    count = st.number_input("How many debts?", min_value=1, max_value=12, value=3, step=1)
    names, bals, aprs, mins = [], [], [], []
    for i in range(int(count)):
        c1, c2, c3, c4 = st.columns([2,1,1,1])
        with c1:
            names.append(st.text_input(f"Debt #{i+1} name", value=f"Debt {i+1}", key=f"name{i}"))
        with c2:
            bals.append(st.number_input("Balance ($)", min_value=0.0, value=1500.0 if i==0 else 800.0 if i==1 else 400.0, step=50.0, key=f"bal{i}"))
        with c3:
            aprs.append(st.number_input("APR (%)", min_value=0.0, value=19.9 if i==0 else 12.5 if i==1 else 8.9, step=0.1, key=f"apr{i}"))
        with c4:
            mins.append(st.number_input("Min Pay ($/mo)", min_value=0.0, value=45.0 if i==0 else 30.0 if i==1 else 25.0, step=5.0, key=f"min{i}"))

    st.markdown("---")
    colA, colB = st.columns([1,1])
    with colA:
        monthly_budget = st.number_input("Total monthly payoff budget ($)", min_value=0.0, value=250.0, step=10.0)
        strategy_choice: Strategy = st.selectbox("Strategy", ["Snowball (Smallest Balance First)", "Avalanche (Highest APR First)"], index=0)
    with colB:
        show_table = st.checkbox("Show monthly detail table", value=False)
        show_chart = st.checkbox("Show payoff chart", value=True)

    submitted = st.form_submit_button("Compare Strategy")

if submitted:
    try:
        debts_list = [Debt(n, b, a, m) for n, b, a, m in zip(names, bals, aprs, mins)]
        # Simulate chosen strategy
        df_chosen, res_chosen = simulate(debts_list, monthly_budget, strategy_choice)
        # Simulate the other strategy for comparison
        other_strategy: Strategy = "Avalanche (Highest APR First)" if strategy_choice.startswith("Snowball") else "Snowball (Smallest Balance First)"
        df_other, res_other = simulate(debts_list, monthly_budget, other_strategy)

        st.subheader("Summary")
        c1, c2 = st.columns(2)
        c1.metric(f"{strategy_choice} — Months", f"{res_chosen['months']}")
        c1.metric(f"{strategy_choice} — Total Interest", f"${res_chosen['total_interest']:,.2f}")
        c2.metric(f"{other_strategy} — Months", f"{res_other['months']}")
        c2.metric(f"{other_strategy} — Total Interest", f"${res_other['total_interest']:,.2f}")

        # Chart
        if show_chart:
            try:
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots(figsize=(6.8, 3.6))
                # Plot total remaining balance over time
                def total_balance(df):
                    cols = [c for c in df.columns if c.endswith("— Balance ($)")]
                    return df[cols].sum(axis=1)

                ax.plot(df_chosen["Month"], total_balance(df_chosen), label=strategy_choice, linewidth=2)
                ax.plot(df_other["Month"], total_balance(df_other), label=other_strategy, linewidth=2, linestyle="--")
                ax.set_xlabel("Month")
                ax.set_ylabel("Total Remaining Balance ($)")
                ax.set_title("Debt Paydown Timeline")
                ax.grid(True, alpha=0.25)
                ax.legend()
                st.pyplot(fig)
            except Exception:
                st.info("Install matplotlib to see the payoff chart: `pip install matplotlib`")

        if show_table:
            st.subheader("Monthly Detail (Chosen Strategy)")
            st.dataframe(df_chosen, use_container_width=True)

        # Exports
        st.subheader("Export")
        payload = {
            "inputs": {
                "debts": [asdict(d) for d in debts_list],
                "monthly_budget": monthly_budget,
            },
            "chosen_strategy": {
                "name": strategy_choice,
                "months": res_chosen["months"],
                "total_interest": res_chosen["total_interest"],
                "paid_off_months": res_chosen["paid_off_months"],
            },
            "other_strategy": {
                "name": other_strategy,
                "months": res_other["months"],
                "total_interest": res_other["total_interest"],
                "paid_off_months": res_other["paid_off_months"],
            },
            "disclaimer": "Educational estimate; ignores fees, changing rates, and statement timing nuances.",
        }
        st.download_button(
            "⬇️ Download JSON (comparison summary)",
            data=json.dumps(payload, indent=2).encode("utf-8"),
            file_name="debt_payoff_comparison.json",
            mime="application/json",
        )
        st.download_button(
            "⬇️ Download CSV (chosen strategy monthly detail)",
            data=df_chosen.to_csv(index=False).encode("utf-8"),
            file_name="debt_payoff_chosen_strategy.csv",
            mime="text/csv",
        )

    except ValueError as e:
        st.error(str(e))
else:
    st.info("Enter your debts, budget, and strategy, then click **Compare Strategy**.")