import streamlit as st

st.set_page_config(page_title="Side Hustle Profitability Analyzer | MFS", page_icon="💼")

st.title("💼 Side Hustle Profitability Analyzer")
st.write("Compare potential side hustles and see which one gives you the best return on your time and money.")

# --- Input section ---
st.header("Enter Your Hustle Details")

col1, col2 = st.columns(2)

with col1:
    hustle_name = st.text_input("Side Hustle Name", "Example: Tutoring, Reselling, Freelance Design")
    hours_per_week = st.number_input("Hours per Week", min_value=1, max_value=80, value=10)
    hourly_income = st.number_input("Average Hourly Income ($)", min_value=0.0, value=20.0, step=1.0)

with col2:
    startup_cost = st.number_input("Startup Costs ($)", min_value=0.0, value=100.0, step=10.0)
    weekly_expenses = st.number_input("Weekly Expenses ($)", min_value=0.0, value=20.0, step=1.0)
    weeks_per_year = st.slider("Weeks Worked per Year", 1, 52, 48)

# --- Calculations ---
annual_income = hourly_income * hours_per_week * weeks_per_year
annual_expenses = (weekly_expenses * weeks_per_year) + startup_cost
annual_profit = annual_income - annual_expenses

roi = ((annual_profit - startup_cost) / startup_cost * 100) if startup_cost > 0 else 0
roi = max(roi, 0)

# --- Output section ---
st.header("📊 Results")

st.metric(label="Estimated Annual Income", value=f"${annual_income:,.2f}")
st.metric(label="Estimated Annual Expenses", value=f"${annual_expenses:,.2f}")
st.metric(label="Estimated Annual Profit", value=f"${annual_profit:,.2f}")
st.metric(label="Return on Investment (ROI)", value=f"{roi:.1f}%")

if roi >= 100:
    st.success("🔥 This side hustle looks very profitable!")
elif roi >= 50:
    st.info("💡 This side hustle is promising — keep your costs in check.")
else:
    st.warning("⚠️ Profit margin seems low. Try reducing expenses or charging more.")

# --- Notes ---
st.markdown("---")
st.subheader("💬 Reflection Questions")
st.write("- How much time are you willing to commit consistently?")
st.write("- Are there upfront costs you could reduce?")
st.write("- Could this side hustle grow into a long-term business?")

st.caption("© Meridian Finance Solutions | Side Hustle Analyzer Tool")