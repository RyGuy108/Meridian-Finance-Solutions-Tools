import streamlit as st
import random

st.set_page_config(page_title="Financial Literacy Quiz | MFS", page_icon="💡")

st.title("💡 Financial Literacy Quiz")
st.write("Test your personal finance knowledge and see where you stand!")

# --- Questions bank ---
questions = [
    {
        "question": "What is the purpose of a budget?",
        "options": ["To restrict spending", "To plan and track income and expenses", "To increase debt"],
        "answer": "To plan and track income and expenses"
    },
    {
        "question": "Which of the following builds credit?",
        "options": ["Paying bills on time", "Avoiding credit cards completely", "Maxing out a credit card"],
        "answer": "Paying bills on time"
    },
    {
        "question": "What does 'pay yourself first' mean?",
        "options": ["Spend before saving", "Save a portion of your income before other expenses", "Pay all bills immediately"],
        "answer": "Save a portion of your income before other expenses"
    },
    {
        "question": "What is an emergency fund for?",
        "options": ["Vacations", "Unexpected expenses", "Online shopping"],
        "answer": "Unexpected expenses"
    },
    {
        "question": "What happens if you only make the minimum payment on a credit card?",
        "options": ["You avoid interest", "You pay more in interest over time", "Your score increases immediately"],
        "answer": "You pay more in interest over time"
    }
]

# --- Shuffle questions ---
random.shuffle(questions)
score = 0

# --- Quiz Loop ---
for i, q in enumerate(questions, start=1):
    st.subheader(f"Question {i}: {q['question']}")
    user_answer = st.radio("Select one:", q["options"], key=f"q{i}")
    if user_answer == q["answer"]:
        score += 1

# --- Results ---
if st.button("Submit Quiz"):
    st.success(f"✅ You got {score} out of {len(questions)} correct!")

    if score == len(questions):
        st.balloons()
        st.write("💪 Excellent! You’re financially sharp.")
    elif score >= 3:
        st.write("⚡ Good job — you’re on your way to mastering financial literacy.")
    else:
        st.write("🧠 Keep learning — check out MFS resources to strengthen your money skills.")

st.markdown("---")
st.caption("© Meridian Finance Solutions | Financial Literacy Tool")