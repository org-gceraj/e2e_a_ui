import streamlit as st
import requests
import os

ip = requests.get("https://api.ipify.org").text
IP_URL = "http://"+ip+":30080"

ENV_API_URL = os.getenv("ENV_API_URL", IP_URL)
API_URL=ENV_API_URL+"/predict"

st.title("Sentiment Analysis")

text = st.text_area("Enter feedback")

if st.button("Predict"):
    if not text.strip():
        st.warning("Please enter some text")
    else:
        try:
            response = requests.post(API_URL, json={"text": text}, timeout=3)
            response.raise_for_status()
            st.success(response.json())
        except requests.exceptions.ConnectionError:
            st.error("🚨 API is not running. Start FastAPI first.")
        except Exception as e:
            st.error(f"Error: {e}")

