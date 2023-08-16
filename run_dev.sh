#!/bin/bash

# Start the FastAPI app from the app folder
cd app
uvicorn main:app --reload &

cd ..
# Start the Tailwind CSS watcher from the app/tailwindcss folder
tailwindcss -i app/styles/main.css -o app/static/css/main.css --watch
