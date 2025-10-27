import streamlit as st

st.set_page_config(page_title="Budget Style Recommender | MFS", page_icon="🧠")

st.title("🧠 Budget Style Recommender")
st.write("Answer a few quick questions and discover a budgeting method that fits your personality and lifestyle.")

# Form
with st.form("budget_quiz"):
    st.subheader("🔍 Budgeting Personality Questions")

    q1 = st.radio("When you get money, you usually…", [
        "Save a portion immediately", 
        "Spend impulsively but try to catch up later", 
        "Plan every dollar before spending"
    ])

    q2 = st.radio("Which describes your money tracking habits?", [
        "I track everything with an app or spreadsheet", 
        "I check my bank account sometimes", 
        "I don’t track unless there’s a problem"
    ])

    q3 = st.radio("What motivates you most to save?", [
        "Freedom and flexibility", 
        "Avoiding financial stress", 
        "Reaching specific goals"
    ])

    q4 = st.radio("You’re more likely to…", [
        "Set broad spending limits (e.g., $300 for fun)", 
        "Stick to strict weekly spending plans", 
        "Use cash so I don’t overspend"
    ])

    submitted = st.form_submit_button("Find My Budget Style")

# Output
if submitted:
    st.header("💡 Your Recommended Budgeting System")

    if q1 == "Plan every dollar before spending" and q2 == "I track everything with an app or spreadsheet":
        st.success("✅ Recommended: **Zero-Based Budgeting**")
        st.write("This method helps you assign every dollar to a purpose. Great for detail-oriented planners who want total control.")
    elif q4 == "Use cash so I don’t overspend":
        st.success("✅ Recommended: **Cash Envelope System**")
        st.write("Helps prevent overspending by giving physical limits to categories. Ideal for those who overspend digitally.")
    elif q1 == "Save a portion immediately" and q3 == "Freedom and flexibility":
        st.success("✅ Recommended: **50/30/20 Rule**")
        st.write("Simple and effective: 50% needs, 30% wants, 20% savings. Great for people new to budgeting or who like flexibility.")
    else:
        st.success("✅ Recommended: **Weekly or Category-Based Budgeting**")
        st.write("Assign weekly limits or budget by category. A balanced method for those still building money discipline.")

    st.markdown("---")
    st.write("💬 Want to try a different result? Change your answers above.")

st.caption("© Meridian Finance Solutions | Budget Style Recommender")