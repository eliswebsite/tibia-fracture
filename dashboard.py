import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
from supabase import create_client
import plotly.graph_objects as go
import os

URL = "https://sojkgoaefkgtnxmhkptz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNvamtnb2FlZmtndG54bWhrcHR6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ2MTYxMjIsImV4cCI6MjA5MDE5MjEyMn0.Ev1EmLOpdcVzj6Jcpsuv9m7z_3ybYowodU2yc7abpyQ"
supabase = create_client(URL, KEY)

st.set_page_config(page_title="Precision Tibia Case Matcher", layout="wide", initial_sidebar_state="collapsed")

if "page" not in st.session_state:
    st.session_state.page = "landing"

if st.session_state.page == "landing":

    st.markdown("""
    <style>
    #MainMenu, header, footer { display: none !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    .main .block-container { padding-top: 0 !important; }
    [data-testid="stAppViewContainer"] { background: #FAFAF8 !important; }
    section[data-testid="stSidebar"] { display: none !important; }
    div[data-testid="stButton"] { display: flex; justify-content: center; margin-top: 20px; margin-bottom: 40px; }
    div[data-testid="stButton"] > button { background: #111 !important; color: white !important; border: none !important; border-radius: 100px !important; padding: 18px 56px !important; font-size: 17px !important; font-weight: 500 !important; cursor: pointer !important; }
    div[data-testid="stButton"] > button:hover { background: #2563EB !important; }
    </style>
    """, unsafe_allow_html=True)

    html_path = os.path.join(os.path.dirname(__file__), "landing.html")
    with open(html_path, "r") as f:
        landing_html = f.read()

    components.html(landing_html, height=1900, scrolling=True)

    if st.button("🚀  Launch Tool  →", key="launch"):
        st.session_state.page = "app"
        st.rerun()
