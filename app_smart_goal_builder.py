# app_smart_goal_builder.py
# Streamlit app — builds a SMART savings goal, checks feasibility, and outputs a step-by-step plan.

import io
import json
from datetime import date, timedelta
import math
import streamlit as st

st.set_page_config(page_title="SMART Goal Builder", page_icon="🧠", layout="centered")

st.title("🧠 SMART Goal Builder")
st.caption("Turn a money goal into a Specific, Measurable, Achievable, Relevant, Time-bound plan. Educational tool.")
st.divider()

with st.form("smart_form"):
    st.subheader("Your Goal")
    goal_name = st.text_input("Goal name", value="Emergency Laptop Fund")
    goal_desc = st.text_area("Why this matters (your 'why')", value="I need a reliable laptop for school and projects.")
    col1, col2 = st.columns(2)
    with col1:
        goal_amount = st.number_input("Goal amount ($)", min_value=1.0, value=1200.0, step=50.0)
        starting_balance = st.number_input("Starting balance ($)", min_value=0.0, value=100.0, step=25.0)
    with col2:
        target_date = st.date_input("Target date (deadline)", value=(date.today() + timedelta(days=180)))
        monthly_contrib = st.number_input("Planned monthly contribution ($)", min_value=0.0, value=150.0, step=10.0)

    # Optional assumption: interest on savings
    annual_yield = st.number_input("Annual yield (%) (optional)", min_value=0.0, value=0.5, step=0.1)
    submitted = st.form_submit_button("Build SMART Plan")

def months_between(d1: date, d2: date) -> int:
    """Rough month difference (floor)."""
    if d2 <= d1: return 0
    return (d2.year - d1.year) * 12 + (d2.month - d1.month) - (0 if d2.day >= d1.day else 1)

def future_balance_months(start, monthly_add, months, annual_yield_pct):
    """Monthly contribution with monthly effective compounding."""
    r_m = ((1 + annual_yield_pct / 100.0) ** (1/12)) - 1
    bal = start
    for _ in range(months):
        bal += monthly_add
        bal += bal * r_m
    return bal

def required_monthly_for_deadline(start, goal, months, annual_yield_pct):
    """Solve for monthly contribution to reach goal in 'months' with monthly compounding."""
    if months <= 0:
        return float('inf') if start < goal else 0.0
    r_m = ((1 + annual_yield_pct / 100.0) ** (1/12)) - 1
    if abs(r_m) < 1e-9:
        return max(0.0, (goal - start) / months)
    # Future value with contributions at period end: FV = start*(1+r)^m + p*(((1+r)^m - 1)/r)
    # Solve p = (FV - start*(1+r)^m) * r / ((1+r)^m - 1)
    fv_needed = max(goal, 0.0)
    growth = (1 + r_m) ** months
    numerator = (fv_needed - start * growth) * r_m
    denom = (growth - 1)
    if denom <= 0:
        return float('inf') if start < goal else 0.0
    p = numerator / denom
    return max(0.0, p)

if submitted:
    today = date.today()
    months_to_deadline = months_between(today, target_date)
    target_balance = goal_amount
    current_gap = max(0.0, target_balance - starting_balance)

    # Check feasibility: balance by deadline vs. target; and required monthly if underfunded.
    projected = future_balance_months(starting_balance, monthly_contrib, months_to_deadline, annual_yield)
    required_monthly = required_monthly_for_deadline(starting_balance, target_balance, months_to_deadline, annual_yield)

    achievable = projected + 1e-6 >= target_balance  # allow tiny tolerance

    st.subheader("SMART Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Goal Amount", f"${target_balance:,.2f}")
    c2.metric("Deadline", target_date.strftime("%b %d, %Y"))
    c3.metric("Months to go", f"{months_to_deadline}")

    st.write("**Specific**: ", f"{goal_name} — {goal_desc}")
    st.write("**Measurable**: ", f"Target ${target_balance:,.2f}; Starting ${starting_balance:,.2f}; Gap ${current_gap:,.2f}")
    st.write("**Time-bound**: ", f"Deadline is {target_date.strftime('%b %d, %Y')} ({months_to_deadline} months)")

    if achievable:
        st.success(f"**Achievable**: Yes — at ${monthly_contrib:,.2f}/mo you project to reach ~${projected:,.0f} by the deadline.")
    else:
        st.warning(f"**Achievable**: Not yet — at ${monthly_contrib:,.2f}/mo you project to reach ~${projected:,.0f}. "
                   f"Required/month to hit ${target_balance:,.0f} by the deadline: **${required_monthly:,.2f}**.")

    st.write("**Relevant**: ", "Explain how this aligns with your priorities (school, work, stability, health, etc.).")

    # Simple milestone plan
    st.subheader("Milestones")
    if months_to_deadline <= 0:
        st.info("Deadline is now/past. Pick a future date to generate milestones.")
    else:
        quarter = max(1, months_to_deadline // 3)
        m1 = today + timedelta(days=int(quarter*30))
        m2 = today + timedelta(days=int(2*quarter*30))
        m3 = target_date
        st.write(f"- **Milestone 1 ({m1.strftime('%b %d')}):** Aim for ~33% funded → ${target_balance*0.33:,.0f}")
        st.write(f"- **Milestone 2 ({m2.strftime('%b %d')}):** Aim for ~66% funded → ${target_balance*0.66:,.0f}")
        st.write(f"- **Final ({m3.strftime('%b %d')}):** Reach ${target_balance:,.0f}")

    # Export
    st.subheader("Export")
    payload = {
        "inputs": {
            "goal_name": goal_name,
            "goal_description": goal_desc,
            "goal_amount": target_balance,
            "starting_balance": starting_balance,
            "deadline": target_date.isoformat(),
            "monthly_contribution": monthly_contrib,
            "annual_yield_pct": annual_yield,
        },
        "computed": {
            "months_to_deadline": months_to_deadline,
            "projected_balance_by_deadline": round(projected, 2),
            "required_monthly_to_hit_goal": None if math.isinf(required_monthly) else round(required_monthly, 2),
            "achievable_at_current_plan": bool(achievable),
        },
        "smart": {
            "specific": f"{goal_name} — {goal_desc}",
            "measurable": {
                "target": round(target_balance, 2),
                "starting": round(starting_balance, 2),
                "gap": round(current_gap, 2),
            },
            "achievable": "Yes" if achievable else "No",
            "relevant_prompt": "Explain how this goal supports your priorities.",
            "time_bound": target_date.isoformat(),
        },
        "disclaimer": "Educational estimate. Adjust numbers to your real situation.",
    }
    st.download_button(
        "⬇️ Download JSON (SMART plan)",
        data=json.dumps(payload, indent=2).encode("utf-8"),
        file_name="smart_goal_plan.json",
        mime="application/json",
    )

    txt = io.StringIO()
    txt.write("MFS SMART Goal Plan\n")
    txt.write("-------------------\n")
    txt.write(f"Goal: {goal_name}\n")
    txt.write(f"Why: {goal_desc}\n")
    txt.write(f"Target: ${target_balance:,.2f} by {target_date.strftime('%b %d, %Y')} ({months_to_deadline} months)\n")
    txt.write(f"Starting: ${starting_balance:,.2f} | Monthly: ${monthly_contrib:,.2f} | Yield: {annual_yield:.2f}%\n")
    txt.write(f"Projected at current plan: ${projected:,.2f}\n")
    if math.isinf(required_monthly):
        txt.write("Required monthly (to hit by deadline): n/a\n")
    else:
        txt.write(f"Required monthly (to hit by deadline): ${required_monthly:,.2f}\n")
    st.download_button("⬇️ Download Text Summary", data=txt.getvalue(), file_name="smart_goal_plan.txt", mime="text/plain")
else:
    st.info("Fill in your goal details and click **Build SMART Plan**.")