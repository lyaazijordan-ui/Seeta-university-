import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import requests
import speech_recognition as sr
from gtts import gTTS
import tempfile
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet

from auth import login, signup
from db import save_user_data, load_user_data
from ai import chat_with_ai

st.set_page_config(page_title="Intellectual Titan", layout="wide")

# ---------- UI ----------
st.markdown("""
<style>
.stApp {background: radial-gradient(circle,#020617,#000); color:white;}
.block-container {background: rgba(255,255,255,0.05); border-radius:20px; padding:2rem;}
</style>
""", unsafe_allow_html=True)

# ---------- VOICE ----------
def speak(text):
    tts = gTTS(text)
    file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(file.name)
    st.audio(open(file.name, "rb").read())

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        audio = r.listen(source)
    try:
        return r.recognize_google(audio)
    except:
        return "Couldn't hear you"

# ---------- LIVE DATA ----------
def get_crypto():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
    return requests.get(url).json()

# ---------- AI INSIGHTS ----------
def analyze(df):
    summary = df.describe().to_string()
    return chat_with_ai([{"role":"user","content":f"Analyze this data:\n{summary}"}])

# ---------- SESSION ----------
if "page" not in st.session_state:
    st.session_state.page="Login"
if "user" not in st.session_state:
    st.session_state.user=None

# ---------- LOGIN ----------
if st.session_state.page=="Login":
    st.title("⚡ Intellectual Titan")

    mode = st.radio("",["Login","Sign Up"])
    email = st.text_input("Email")
    password = st.text_input("Password",type="password")

    if st.button("Enter"):
        if mode=="Login":
            if login(email,password):
                st.session_state.user=email
                st.session_state.page="Dashboard"
                st.rerun()
        else:
            signup(email,password)
            st.success("Account created")

# ---------- SIDEBAR ----------
if st.session_state.user:
    st.sidebar.title("⚡ Titan")
    st.session_state.page = st.sidebar.radio(
        "Menu",
        ["Dashboard","Live Market","3D","AI","Reports","Logout"]
    )

# ---------- DASHBOARD ----------
if st.session_state.page=="Dashboard":
    st.title("📊 Command Center")

    file = st.file_uploader("Upload CSV")

    if file:
        df = pd.read_csv(file)
        save_user_data(st.session_state.user,"data",df.to_dict())
    else:
        data = load_user_data(st.session_state.user,"data")
        df = pd.DataFrame(data) if data else None

    if df is not None:
        st.dataframe(df.head())

        nums = df.select_dtypes(include=np.number).columns
        if len(nums)>0:
            x = st.selectbox("X",df.columns)
            y = st.selectbox("Y",nums)

            fig = px.line(df,x=x,y=y)
            st.plotly_chart(fig)

            if st.button("🧠 Analyze"):
                result = analyze(df)
                st.write(result)
                speak(result)

# ---------- LIVE MARKET ----------
if st.session_state.page=="Live Market":
    st.title("📡 Crypto Live")

    data = get_crypto()

    btc = data["bitcoin"]["usd"]
    eth = data["ethereum"]["usd"]

    st.metric("Bitcoin", f"${btc}")
    st.metric("Ethereum", f"${eth}")

# ---------- 3D ----------
if st.session_state.page=="3D":
    data = load_user_data(st.session_state.user,"data")
    if data:
        df = pd.DataFrame(data)
        nums = df.select_dtypes(include=np.number).columns
        if len(nums)>=3:
            fig = px.scatter_3d(df,x=nums[0],y=nums[1],z=nums[2])
            st.plotly_chart(fig)

# ---------- AI ----------
if st.session_state.page=="AI":
    st.title("🤖 Jarvis")

    msg = st.text_input("Ask")

    if st.button("Send"):
        reply = chat_with_ai([{"role":"user","content":msg}])
        st.write(reply)
        speak(reply)

    if st.button("🎤 Speak"):
        voice = listen()
        reply = chat_with_ai([{"role":"user","content":voice}])
        st.write(reply)
        speak(reply)

# ---------- REPORT ----------
if st.session_state.page=="Reports":
    data = load_user_data(st.session_state.user,"data")
    if data:
        df = pd.DataFrame(data)

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()

        elements=[Paragraph("Report",styles["Title"])]
        elements.append(Table([df.columns.tolist()]+df.values.tolist()))

        doc.build(elements)
        buffer.seek(0)

        st.download_button("Download PDF",buffer)

# ---------- LOGOUT ----------
if st.session_state.page=="Logout":
    st.session_state.clear()
    st.rerun()
