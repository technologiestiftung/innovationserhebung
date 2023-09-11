from bokeh.embed import server_document
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
import panel as pn
from sliders.pn_app import create_app
from utils.translation import load_translation
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)

class Language(str, Enum):
    en = "en"
    de = "de"

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(GZipMiddleware)
templates = Jinja2Templates(directory="templates")

@app.get("/")
@app.get("/{language}/")
async def bkapp_page(request: Request, language: Language = None):
    if language is None:
        language = request.headers.get("accept-language", "de")
    translations = load_translation(language)
    script = server_document('http://127.0.0.1:5000/app')
    return templates.TemplateResponse("index.html", {"request": request, "script": script, "translations": translations})



pn.serve({'/app': create_app},
        port=5000, allow_websocket_origin=["127.0.0.1:8000"],
         address="127.0.0.1", show=False)
