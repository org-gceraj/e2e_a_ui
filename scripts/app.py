import streamlit as st
import requests
import os
from prometheus_client import CollectorRegistry, Counter, Histogram
import time

from prometheus_client import make_wsgi_app
from wsgiref.simple_server import make_server
import threading

registry = CollectorRegistry()

PREDICTION_REQUESTS = Counter(
    "streamlit_prediction_requests_total",
    "Total number of prediction requests",
    registry=registry
)

PREDICTION_ERRORS = Counter(
    "streamlit_prediction_errors_total",
    "Total number of prediction errors",
    registry=registry
)

PREDICTION_LATENCY = Histogram(
    "streamlit_prediction_latency_seconds",
    "Latency of prediction requests",
    registry=registry
)



def start_metrics_server():
    app = make_wsgi_app(registry)
    server = make_server('', 8000, app)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

start_metrics_server()



# -----------------------------
# Your existing logic
# -----------------------------
ip = requests.get("https://api.ipify.org").text
IP_URL = "http://" + ip + ":30080"

ENV_API_URL = os.getenv("ENV_API_URL", IP_URL)
API_URL = ENV_API_URL + "/predict"

st.title("Sentiment Analysis")

text = st.text_area("Enter feedback")

if st.button("Predict"):
    if not text.strip():
        st.warning("Please enter some text")
    else:
        PREDICTION_REQUESTS.inc()  # increment counter

        start_time = time.time()

        try:
            response = requests.post(API_URL, json={"text": text}, timeout=3)
            response.raise_for_status()

            latency = time.time() - start_time
            PREDICTION_LATENCY.observe(latency)

            st.success(response.json())

        except requests.exceptions.ConnectionError:
            PREDICTION_ERRORS.inc()
            st.error("🚨 API is not running. Start FastAPI first.")

        except Exception as e:
            PREDICTION_ERRORS.inc()
            st.error(f"Error: {e}")

