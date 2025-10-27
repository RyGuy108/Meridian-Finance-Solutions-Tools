import streamlit as st

st.set_page_config(page_title="Loan vs. Scholarship Decision Helper | MFS", page_icon="🎓")

st.title("🎓 Loan vs. Scholarship Decision Helper")
st.write("Compare the long-term costs and benefits of taking student loans versus waiting or applying for scholarships.")

# --- Input Section ---
st.header("Your Education Details")

col1, col2 = st.columns(2)

with col1:
    tuition = st.number_input("Total Tuition Cost ($)", min_value=1000.0, value=20000.0, step=1000.0)
    scholarship_amount = st.number_input("Scholarship or Aid Amount ($)", min_value=0.0, value=5000.0, step=500.0)
    wait_time = st.slider("If waiting to apply for scholarships, how many months delay?", 0, 24, 6)

with col2:
    loan_interest = st.number_input("Student Loan Interest Rate (%)", min_value=0.0, value=5.0, step=0.5)
    repayment_years = st.slider("Loan Repayment Period (Years)", 1, 30, 10)
    expected_salary = st.number_input("Expected Starting Salary ($)", min_value=20000.0, value=60000.0, step=1000.0)

# --- Calculations ---
loan_needed = tuition - scholarship_amount
loan_interest_decimal = loan_interest / 100
monthly_rate = loan_interest_decimal / 12
months = repayment_years * 12

if loan_needed > 0:
    monthly_payment = loan_needed * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
    total_paid = monthly_payment * months
    total_interest = total_paid - loan_needed
else:
    monthly_payment = 0
    total_paid = 0
    total_interest = 0

# --- Output Section ---
st.header("📊 Results Comparison")

col1, col2 = st.columns(2)
col1.metric("Loan Needed", f"${loan_needed:,.2f}")
col2.metric("Total Interest Paid", f"${total_interest:,.2f}")

st.write("---")

st.subheader("📈 Loan Summary")
st.write(f"- **Monthly Payment:** ${monthly_payment:,.2f}")
st.write(f"- **Total Repayment:** ${total_paid:,.2f} over {repayment_years} years")
st.write(f"- **Estimated Starting Salary:** ${expected_salary:,.2f}")

st.divider()

st.subheader("💡 Reflection")
st.write(f"- If you delay school by {wait_time} months to earn more scholarships, how much could you save in interest?")
st.write("- Is the time worth the financial savings?")
st.write("- Could part-time work or early scholarship research reduce your loan need?")

st.caption("© Meridian Finance Solutions | Loan vs. Scholarship Decision Helper")