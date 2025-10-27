import streamlit as st
import pandas as pd

st.set_page_config(page_title="Chapter Impact Dashboard | MFS", page_icon="📈")

st.title("📈 Chapter Impact Dashboard")
st.write("Track your chapter’s growth, outreach, and impact in real time. Perfect for internal reporting or competitions.")

# Form
with st.form("impact_log"):
    st.subheader("📋 Log New Event or Outreach")

    event_name = st.text_input("Event or Outreach Name", "Financial Literacy Workshop")
    date = st.date_input("Date")
    people_reached = st.number_input("People Reached", min_value=0, value=25)
    organization = st.text_input("School/Partner Org", "East High School")
    notes = st.text_area("Quick Notes (optional)")
    submitted = st.form_submit_button("Log Entry")

# Store data
if "impact_data" not in st.session_state:
    st.session_state["impact_data"] = []

if submitted and event_name:
    st.session_state["impact_data"].append({
        "Date": date,
        "Event": event_name,
        "People Reached": people_reached,
        "Partner": organization,
        "Notes": notes
    })

# Display Dashboard
if st.session_state["impact_data"]:
    df = pd.DataFrame(st.session_state["impact_data"])

    st.subheader("📊 Logged Events")
    st.dataframe(df, use_container_width=True)

    st.subheader("📌 Totals So Far")
    total_events = len(df)
    total_people = df["People Reached"].sum()
    unique_partners = df["Partner"].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Events", total_events)
    col2.metric("People Reached", total_people)
    col3.metric("Partner Orgs", unique_partners)

    st.markdown("---")
    st.subheader("💬 Tips")
    st.write("- Keep this updated after each outreach event.")
    st.write("- Use metrics for competitions, newsletters, or social posts.")
else:
    st.info("Start logging your first event above!")

st.caption("© Meridian Finance Solutions | Chapter Dashboard Tool")