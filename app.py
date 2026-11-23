import os

import streamlit as st
from dotenv import load_dotenv

# בודקים שיש מפתח לפני שמייבאים את הסוכנים (הם יוצרים חיבור ל-OpenAI כבר בייבוא)
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY is missing. Copy .env.example to .env and fill in your key.")
    st.stop()

from agent_api import QUESTION
from agent_api import run_agent as run_api
from agent_sdk import run_agent as run_sdk
from shop_tools import PRICES


# הפונקציה מציגה את התוצאה של סוכן אחד.
# מקבלת: title - כותרת (API או SDK), result - המילון ש-run_agent מחזירה.
# מחזירה: כלום (רק מציגה על המסך).
def show_result(title, result):
    st.subheader(title)
    st.markdown(result["answer"] or "_No final answer_")

    # טבלת הקריאות: שורה לכל קריאה למודל
    rows = [
        {"call": c["call"], "tools": ", ".join(c["tools"]) or "-", "tokens": c["tokens"]}
        for c in result["calls"]
    ]
    st.dataframe(rows, hide_index=True)

    left, right = st.columns(2)
    left.metric("Model calls", result["num_calls"])
    right.metric("Total tokens", result["total_tokens"])


st.title("Shopping agent: API vs SDK")

# כפתור לדף המוצרים: רשימת המוצרים מוצגת רק כאן, ולא בפלט של הסוכן
with st.popover("Products"):
    st.dataframe([{"item": name, "price": price} for name, price in PRICES.items()], hide_index=True)

question = st.text_input("Question", value=QUESTION)
mode = st.radio("Run with", ["API", "SDK", "Both"], horizontal=True)

if st.button("Run", type="primary"):
    if mode == "API":
        with st.spinner("Running API agent..."):
            show_result("API", run_api(question))

    elif mode == "SDK":
        with st.spinner("Running SDK agent..."):
            show_result("SDK", run_sdk(question))

    else:
        # שתי עמודות: משמאל API, מימין SDK
        col_api, col_sdk = st.columns(2)
        with col_api, st.spinner("Running API agent..."):
            show_result("API", run_api(question))
        with col_sdk, st.spinner("Running SDK agent..."):
            show_result("SDK", run_sdk(question))
