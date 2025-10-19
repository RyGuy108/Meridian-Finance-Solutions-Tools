# app_risk_tolerance_quiz.py
# Streamlit app — short quiz to estimate investing risk comfort.
# Outputs a score, a risk profile, and an educational allocation suggestion.

import io
import json
import streamlit as st

st.set_page_config(page_title="Risk Tolerance Quiz", page_icon="🧪", layout="centered")

st.title("🧪 Risk Tolerance Quiz")
st.caption("A short, educational self-assessment to understand your comfort with investment risk. This is not financial advice.")
st.divider()

questions = [
    {
        "q": "1) When your investments drop 10% in a month, what do you most likely do?",
        "choices": [
            ("Sell to avoid more losses", 1),
            ("Hold and wait it out", 3),
            ("Buy more while it’s cheaper", 5),
        ],
    },
    {
        "q": "2) What’s your main goal for investing?",
        "choices": [
            ("Protect my money (stability first)", 1),
            ("Balance growth and stability", 3),
            ("Maximize long-term growth", 5),
        ],
    },
    {
        "q": "3) How long before you might need this money?",
        "choices": [
            ("0–3 years", 1),
            ("3–7 years", 3),
            ("7+ years", 5),
        ],
    },
    {
        "q": "4) How would you feel if your investments were volatile month-to-month?",
        "choices": [
            ("Very uncomfortable", 1),
            ("Okay as long as long-term is positive", 3),
            ("Totally fine — that’s opportunity", 5),
        ],
    },
    {
        "q": "5) Experience level with investing:",
        "choices": [
            ("Beginner (new to this)", 1),
            ("Some experience", 3),
            ("Experienced/comfortable", 5),
        ],
    },
    {
        "q": "6) If you could double your money in 10 years but it might be down 30% some years, you would:",
        "choices": [
            ("Avoid that — too risky", 1),
            ("Consider a smaller amount", 3),
            ("Be comfortable investing", 5),
        ],
    },
]

def profile_from_score(score: int):
    # 6 questions, each 1–5 → min 6, max 30
    if score <= 12:
        return "Conservative", "Focus on stability and lower volatility over growth."
    elif score <= 22:
        return "Moderate", "Balance growth potential with risk management."
    else:
        return "Aggressive", "Comfortable with volatility for higher long-term growth."

def suggested_mix(profile: str):
    # Educational-only illustrative mixes; not advice.
    mixes = {
        "Conservative": {"Stocks/Equities": 30, "Bonds": 60, "Cash": 10},
        "Moderate": {"Stocks/Equities": 60, "Bonds": 35, "Cash": 5},
        "Aggressive": {"Stocks/Equities": 85, "Bonds": 10, "Cash": 5},
    }
    return mixes[profile]

with st.form("risk_form"):
    total = 0
    answers = []
    for idx, q in enumerate(questions):
        st.write(f"**{q['q']}**")
        choice_labels = [c[0] for c in q["choices"]]
        default_idx = 1  # middle default
        pick = st.radio("", choice_labels, index=default_idx, key=f"q{idx}", horizontal=False)
        score = dict(q["choices"])[pick]
        answers.append((q["q"], pick, score))
        total += score
        st.markdown("---" if idx < len(questions)-1 else "")

    submitted = st.form_submit_button("Get My Profile")

if submitted:
    profile, desc = profile_from_score(total)
    st.subheader("Your Results")
    a, b, c = st.columns(3)
    a.metric("Score", f"{total} / 30")
    b.metric("Profile", profile)
    c.metric("Questions", f"{len(questions)}")

    st.info(f"**Interpretation:** {desc}")
    mix = suggested_mix(profile)

    # Simple bar text (no extra libs)
    st.subheader("Educational Mix (Illustrative)")
    st.write(
        f"- **Stocks/Equities:** {mix['Stocks/Equities']}%\n"
        f"- **Bonds:** {mix['Bonds']}%\n"
        f"- **Cash:** {mix['Cash']}%\n"
    )
    st.caption("These ranges are for learning only. Real portfolios depend on goals, time horizon, taxes, and personal circumstances.")

    # Export
    payload = {
        "score": total,
        "profile": profile,
        "description": desc,
        "educational_mix": mix,
        "answers": [{"question": q, "answer": a, "score": s} for (q, a, s) in answers],
        "disclaimer": "Educational only. Not financial advice.",
    }
    st.subheader("Export")
    st.download_button(
        "⬇️ Download JSON (results)",
        data=json.dumps(payload, indent=2).encode("utf-8"),
        file_name="risk_tolerance_results.json",
        mime="application/json",
    )

    txt = io.StringIO()
    txt.write("MFS Risk Tolerance Results (Educational)\n")
    txt.write("---------------------------------------\n")
    txt.write(f"Score: {total} / 30\n")
    txt.write(f"Profile: {profile}\n")
    txt.write(f"Interpretation: {desc}\n")
    txt.write("Suggested Educational Mix:\n")
    for k, v in mix.items():
        txt.write(f"  - {k}: {v}%\n")
    st.download_button("⬇️ Download Text Summary", data=txt.getvalue(), file_name="risk_tolerance_summary.txt", mime="text/plain")
else:
    st.info("Answer the 6 questions and click **Get My Profile** to see your results.")