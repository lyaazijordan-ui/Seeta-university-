import streamlit as st
from supabase import create_client

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

def signup(email, password):
    try:
        supabase.auth.sign_up({"email": email, "password": password})
        return True
    except:
        return False

def login(email, password):
    try:
        supabase.auth.sign_in_with_password({"email": email, "password": password})
        return True
    except:
        return False
