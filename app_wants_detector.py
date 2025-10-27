import streamlit as st
import pandas as pd

st.set_page_config(page_title="Wants Detector | MFS", page_icon="🛍️")

st.title("🛍️ Wants Detector")
st.write("Sort through your recent spending to discover how much was based on need vs. want — and what you can change.")

# Form for user input
with st.form("spending_input_form"):
    item = st.text_input("What did you buy recently?")
    cost = st.number_input("How much did it cost?", min_value=1.0, value=20.0, step=1.0)
    reason = st.selectbox("Why did you buy it?", [
        "I needed it",
        "I felt pressured",
        "I was bored or stressed",
        "It was on sale",
        "Impulse / Emotion",
        "Planned treat",
        "Genuinely useful"
    ])
    submitted = st.form_submit_button("Add Purchase")

# Initialize state
if "spend_data" not in st.session_state:
    st.session_state["spend_data"] = []

# Add to state
if submitted and item:
    st.session_state["spend_data"].append({"Item": item, "Cost": cost, "Reason": reason})

# Display data
if st.session_state["spend_data"]:
    st.subheader("🧾 Your Spending Log")
    df = pd.DataFrame(st.session_state["spend_data"])

    # Categorize automatically
    df["Need vs. Want"] = df["Reason"].apply(lambda r: "Need" if r in ["I needed it", "Genuinely useful"] else "Want")
    df["% of Total"] = round(df["Cost"] / df["Cost"].sum() * 100, 1)

    st.dataframe(df, use_container_width=True)

    # Metrics
    wants_total = df[df["Need vs. Want"] == "Want"]["Cost"].sum()
    needs_total = df[df["Need vs. Want"] == "Need"]["Cost"].sum()

    col1, col2 = st.columns(2)
    col1.metric("Total Spent on Wants", f"${wants_total:,.2f}")
    col2.metric("Total Spent on Needs", f"${needs_total:,.2f}")

    st.divider()
    st.subheader("💡 Reflection")
    st.write("- Were you surprised by your % of spending on wants?")
    st.write("- What could you change next week?")
    st.write("- Are there habits here that could become financial leaks?")

else:
    st.info("Start logging your purchases above.")

st.caption("© Meridian Finance Solutions | Wants Detector Tool")