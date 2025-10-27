import streamlit as st
import pandas as pd

st.set_page_config(page_title="Bill & Subscription Tracker | MFS", page_icon="💳")

st.title("💳 Bill & Subscription Tracker")
st.write("Track your monthly subscriptions and recurring expenses to see how much they really cost over time.")

# --- Input Form ---
st.header("Add Your Subscriptions")

with st.form("add_subscription_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Subscription Name", placeholder="Spotify, Netflix, Gym, etc.")
    with col2:
        cost = st.number_input("Monthly Cost ($)", min_value=0.0, value=10.0, step=1.0)
    with col3:
        category = st.selectbox("Category", ["Entertainment", "Education", "Utilities", "Fitness", "Other"])
    submitted = st.form_submit_button("Add Subscription")

# --- Session State ---
if "subscriptions" not in st.session_state:
    st.session_state["subscriptions"] = []

if submitted and name:
    st.session_state["subscriptions"].append({"Name": name, "Cost": cost, "Category": category})

# --- Display Current List ---
if st.session_state["subscriptions"]:
    st.header("📅 Your Monthly Subscriptions")
    df = pd.DataFrame(st.session_state["subscriptions"])
    df["Annual Cost ($)"] = df["Cost"] * 12
    st.dataframe(df, use_container_width=True)

    total_monthly = df["Cost"].sum()
    total_annual = df["Annual Cost ($)"].sum()

    col1, col2 = st.columns(2)
    col1.metric("Total Monthly Cost", f"${total_monthly:,.2f}")
    col2.metric("Total Annual Cost", f"${total_annual:,.2f}")

    st.divider()

    st.subheader("💡 Reflection")
    st.write("- Are there subscriptions you rarely use but still pay for?")
    st.write("- What could you do with that money if you cut one or two?")
else:
    st.info("Add your first subscription above to start tracking!")

st.caption("© Meridian Finance Solutions | Bill & Subscription Tracker")