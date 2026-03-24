import requests
import streamlit as st

API_KEY = st.secrets["OPENROUTER_API_KEY"]

def chat_with_ai(messages):
    try:
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": messages
            }
        )
        data = res.json()
        if "choices" not in data:
            return "AI unavailable."
        return data["choices"][0]["message"]["content"]
    except:
        return "AI error."
