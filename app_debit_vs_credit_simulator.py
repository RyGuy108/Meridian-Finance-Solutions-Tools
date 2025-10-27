import streamlit as st
import pandas as pd

st.set_page_config(page_title="Debit vs. Credit Simulator | MFS", page_icon="💳")

st.title("💳 Debit vs. Credit Spending Simulator")
st.write("See how your spending decisions affect you differently when using a debit card vs. a credit card.")

# Sample transaction list
st.subheader("Enter Your Purchases")

with st.form("purchase_form"):
    purchase_name = st.text_input("Item/Description", "Groceries")
    purchase_amount = st.number_input("Amount ($)", min_value=1.0, value=50.0, step=1.0)
    submitted = st.form_submit_button("Add Purchase")

if "purchases" not in st.session_state:
    st.session_state["purchases"] = []

if submitted and purchase_name:
    st.session_state["purchases"].append({"Item": purchase_name, "Amount": purchase_amount})

if st.session_state["purchases"]:
    df = pd.DataFrame(st.session_state["purchases"])
    total_spent = df["Amount"].sum()
    
    st.subheader("🧾 Purchases List")
    st.dataframe(df, use_container_width=True)

    st.subheader("💡 Debit vs. Credit Impact")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 💳 Credit Card")
        st.write("- Charged to credit line")
        interest = 0.20
        months = 6
        future_debt = total_spent * ((1 + interest/12) ** months)
        st.metric("6-Month Cost (w/20% APR)", f"${future_debt:,.2f}")

    with col2:
        st.markdown("### 🏦 Debit Card")
        st.write("- Paid directly from your account")
        st.metric("Immediate Cost", f"${total_spent:,.2f}")

    st.divider()
    st.subheader("💬 Key Takeaways")
    st.write("- Credit can help build score **if** paid in full on time.")
    st.write("- Leaving balances unpaid adds interest — and grows your debt.")
    st.write("- Debit avoids debt, but offers less protection and no credit benefits.")

else:
    st.info("Add at least one purchase to compare debit vs. credit.")

st.caption("© Meridian Finance Solutions | Debit vs. Credit Spending Simulator")