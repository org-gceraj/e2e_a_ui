import streamlit as st
import requests
import os
import time
import threading
from prometheus_client import CollectorRegistry, Counter, Histogram, make_wsgi_app
from wsgiref.simple_server import make_server

# ---------------------------------------------------------
# Create registry + metrics ONCE using cache_resource
# ---------------------------------------------------------
@st.cache_resource
def init_metrics():
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

    return registry, PREDICTION_REQUESTS, PREDICTION_ERRORS, PREDICTION_LATENCY


# ---------------------------------------------------------
# Start metrics server ONCE — no registry argument needed
# ---------------------------------------------------------
@st.cache_resource
def start_metrics_server():
    registry, *_ = init_metrics()
    app = make_wsgi_app(registry)
    server = make_server('', 8501, app)

    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    return True


# Initialize everything once
registry, PREDICTION_REQUESTS, PREDICTION_ERRORS, PREDICTION_LATENCY = init_metrics()
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

