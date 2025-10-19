# app_budget_503020.py
# Streamlit app — 50/30/20 (or custom) budget splitter with a pie chart, table, and export.

import json
import io
import pandas as pd
import streamlit as st

st.set_page_config(page_title="50/30/20 Budget Splitter", page_icon="💸", layout="centered")

st.title("💸 50/30/20 Budget Splitter")
st.caption("Educational tool: use your **take-home** (after-tax) income. You can keep the default 50/30/20 split or enter your own percentages that add up to 100%.")
st.divider()

with st.form("budget_form"):
    col1, col2 = st.columns([1,1])
    with col1:
        income = st.number_input("Monthly take-home income ($)", min_value=0.0, value=800.0, step=50.0, help="This is your net pay after taxes.")
    with col2:
        use_custom = st.checkbox("Use custom split?", value=False, help="If checked, enter custom percentages below that total 100%.")
    
    if use_custom:
        c1, c2, c3 = st.columns(3)
        with c1:
            p_needs = st.number_input("Needs %", min_value=0.0, max_value=100.0, value=50.0, step=1.0)
        with c2:
            p_wants = st.number_input("Wants %", min_value=0.0, max_value=100.0, value=30.0, step=1.0)
        with c3:
            p_saving = st.number_input("Saving %", min_value=0.0, max_value=100.0, value=20.0, step=1.0)
    else:
        p_needs, p_wants, p_saving = 50.0, 30.0, 20.0

    submitted = st.form_submit_button("Calculate")

if submitted:
    pct_total = p_needs + p_wants + p_saving
    if abs(pct_total - 100.0) > 1e-9:
        st.error(f"Custom percentages must add to 100%. Current total = {pct_total:.1f}%.")
        st.stop()

    needs_amt = round(income * p_needs / 100.0, 2)
    wants_amt = round(income * p_wants / 100.0, 2)
    saving_amt = round(income * p_saving / 100.0, 2)

    st.subheader("Your Monthly Plan")
    st.metric("Needs", f"${needs_amt:,.2f}", f"{p_needs:.0f}%")
    st.metric("Wants", f"${wants_amt:,.2f}", f"{p_wants:.0f}%")
    st.metric("Saving/Investing", f"${saving_amt:,.2f}", f"{p_saving:.0f}%")

    # Pie (simple altair-like via Streamlit's built-in chart? We'll use dataframe + plotly if available)
    # Keep dependencies light: use st.pyplot with matplotlib
    try:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(4.5, 4.5))
        labels = [f"Needs ({p_needs:.0f}%)", f"Wants ({p_wants:.0f}%)", f"Saving ({p_saving:.0f}%)"]
        ax.pie([needs_amt, wants_amt, saving_amt], labels=labels, autopct="%1.0f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)
    except Exception:
        st.info("Install matplotlib for the pie chart: `pip install matplotlib`")

    df = pd.DataFrame(
        {
            "Category": ["Needs", "Wants", "Saving/Investing"],
            "Percent": [p_needs, p_wants, p_saving],
            "Amount ($)": [needs_amt, wants_amt, saving_amt],
        }
    )
    st.dataframe(df, use_container_width=True)

    # Export options
    st.write("**Export**")
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", data=csv_bytes, file_name="budget_split_503020.csv", mime="text/csv")

    payload = {
        "income": income,
        "split_percent": {"needs": p_needs, "wants": p_wants, "saving": p_saving},
        "split_amounts": {"needs": needs_amt, "wants": wants_amt, "saving": saving_amt},
    }
    json_bytes = json.dumps(payload, indent=2).encode("utf-8")
    st.download_button("⬇️ Download JSON", data=json_bytes, file_name="budget_split_503020.json", mime="application/json")

    # Simple printable summary
    summary = io.StringIO()
    summary.write("MFS 50/30/20 Budget Splitter Summary\n")
    summary.write("-----------------------------------\n")
    summary.write(f"Monthly Income: ${income:,.2f}\n")
    summary.write(f"Needs: {p_needs:.0f}% -> ${needs_amt:,.2f}\n")
    summary.write(f"Wants: {p_wants:.0f}% -> ${wants_amt:,.2f}\n")
    summary.write(f"Saving/Investing: {p_saving:.0f}% -> ${saving_amt:,.2f}\n")
    st.download_button("⬇️ Download Text Summary", data=summary.getvalue(), file_name="budget_split_503020.txt", mime="text/plain")
else:
    st.info("Enter your income and click **Calculate** to see your split.")