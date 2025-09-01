#!/bin/bash

#Start the FastAPI application in the background
uvicorn main:app --host 0.0.0.0 --port 8000 &

#Start the Streamlit UI in the foreground
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0