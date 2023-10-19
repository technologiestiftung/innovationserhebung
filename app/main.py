from bokeh.embed import server_document
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
import panel as pn
from sliders.pn_app import get_base_chart, get_fue_chart, get_shares_chart
from utils.translation import load_translation
from enum import Enum
# import logging

# logging.basicConfig(level=logging.INFO)

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
    language_code = get_language_code(language)
    # translations = load_translation(language_code)
    translations = load_translation("de")

    # "key" in request.app.extra["key"] has to be the same value as the chart.id in de.json
    request.app.extra["fue"] = server_document('http://127.0.0.1:5000/fue_chart')
    request.app.extra["shares"] = server_document('http://127.0.0.1:5000/shares_chart')
    request.app.extra["base"] = server_document('http://127.0.0.1:5000/base_chart')

    script = server_document('http://127.0.0.1:5000/app')
    return templates.TemplateResponse("index.html", {"request": request, "script": script, "translations": translations, "language_code": language_code})

def get_language_code(language: Language | str):
    return type(language) is str and language[:2] or language.value

pn.serve({
    '/fue_chart': get_fue_chart, 
    '/shares_chart': get_shares_chart, 
    '/base_chart': get_base_chart, 
    },
        port=5000, allow_websocket_origin=["127.0.0.1:8000"],
         address="127.0.0.1", show=False)
