#!/bin/bash

# Start FastAPI server in the background on an internal port (e.g., 7070)
uvicorn fabric_api:app --host 0.0.0.0 --port 7070 &

# Start Streamlit on port 8700
streamlit run --server.address 0.0.0.0 --server.port 8700 ui.py