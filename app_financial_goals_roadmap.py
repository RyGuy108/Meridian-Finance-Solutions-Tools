import streamlit as st

st.set_page_config(page_title="Financial Goals Roadmap Builder | MFS", page_icon="📅")

st.title("📅 Financial Goals Roadmap Builder")
st.write("Build a plan to achieve your short-, medium-, and long-term money goals with realistic timelines and action steps.")

# Inputs
st.header("🎯 Step 1: Set Your Goals")

short_goal = st.text_input("Short-Term Goal (within 6 months)", "Save $200 for new headphones")
medium_goal = st.text_input("Medium-Term Goal (6–18 months)", "Buy a used car")
long_goal = st.text_input("Long-Term Goal (2+ years)", "Start investing or save for college")

# Targets
st.header("💰 Step 2: Financial Targets")
col1, col2, col3 = st.columns(3)

with col1:
    short_amt = st.number_input("Short-Term Amount ($)", min_value=0.0, value=200.0)
with col2:
    med_amt = st.number_input("Medium-Term Amount ($)", min_value=0.0, value=3000.0)
with col3:
    long_amt = st.number_input("Long-Term Amount ($)", min_value=0.0, value=5000.0)

# Timeline
st.header("📆 Step 3: Timeline for Each Goal")
short_months = st.slider("Months to Reach Short-Term Goal", 1, 6, 3)
med_months = st.slider("Months to Reach Medium-Term Goal", 6, 18, 12)
long_months = st.slider("Months to Reach Long-Term Goal", 24, 60, 36)

# Calculate saving per month
short_save = short_amt / short_months
med_save = med_amt / med_months
long_save = long_amt / long_months

# Output
st.header("🧭 Roadmap Output")
st.write("Here’s what you need to save each month:")

col1, col2, col3 = st.columns(3)
col1.metric("Short-Term", f"${short_save:.2f}/mo")
col2.metric("Medium-Term", f"${med_save:.2f}/mo")
col3.metric("Long-Term", f"${long_save:.2f}/mo")

st.markdown("---")
st.subheader("📝 Next Steps")
st.write("- Add these amounts to your budget.")
st.write("- Consider setting calendar reminders to check your progress.")
st.write("- Celebrate when you hit a milestone!")

st.caption("© Meridian Finance Solutions | Financial Goals Planner")