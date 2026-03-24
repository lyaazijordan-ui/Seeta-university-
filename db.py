import streamlit as st
from supabase import create_client
import json
import pandas as pd

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

TABLE = "user_data"

def save_user_data(user, key, value):
    clean = pd.DataFrame(value).fillna("").to_dict()
    supabase.table(TABLE).upsert({
        "email": user,
        key: json.dumps(clean)
    }).execute()

def load_user_data(user, key):
    res = supabase.table(TABLE).select(key).eq("email", user).execute()
    if res.data and res.data[0][key]:
        return json.loads(res.data[0][key])
    return None
