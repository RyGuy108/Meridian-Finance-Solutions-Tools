import streamlit as st

st.set_page_config(page_title="First Paycheck Simulator | MFS", page_icon="🧾")

st.title("🧾 First Paycheck Simulator")
st.write("Get a realistic estimate of what your first paycheck will look like after taxes and deductions.")

# Inputs
st.header("Enter Your Job Info")
wage = st.number_input("Hourly Wage ($)", min_value=7.0, value=15.0, step=0.5)
hours = st.number_input("Hours Worked per Week", min_value=1, value=20)
state_tax = st.slider("Estimated State Tax (%)", 0, 10, 4)
federal_tax = 10  # fixed for simplicity
social_security = 6.2
medicare = 1.45

# Calculations
gross_pay = wage * hours
total_tax = gross_pay * (federal_tax + state_tax + social_security + medicare) / 100
net_pay = gross_pay - total_tax

# Output
st.header("📊 Your Estimated Paycheck")
col1, col2 = st.columns(2)
col1.metric("Gross Pay (Before Taxes)", f"${gross_pay:.2f}")
col2.metric("Net Pay (Take-Home)", f"${net_pay:.2f}")

# Breakdown
st.subheader("🔍 Deductions Breakdown")
st.write(f"- Federal Tax (10%): ${gross_pay * 0.10:.2f}")
st.write(f"- State Tax ({state_tax}%): ${gross_pay * (state_tax/100):.2f}")
st.write(f"- Social Security (6.2%): ${gross_pay * 0.062:.2f}")
st.write(f"- Medicare (1.45%): ${gross_pay * 0.0145:.2f}")

st.divider()
st.subheader("💬 Reflection")
st.write("- Did you expect to take home less than your total pay?")
st.write("- How will this affect your budgeting for things like food, gas, or saving?")
st.write("- Could increasing hours or wage make a big difference — or would taxes increase too?")

st.caption("© Meridian Finance Solutions | First Paycheck Simulator")