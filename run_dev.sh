#!/bin/bash

# Start the FastAPI app
uvicorn app.main:app --reload &

python -m webbrowser -t "http://127.0.0.1:8000" &

# Start the Tailwind CSS watcher using the npm script
npm run dev:tailwind

