from bokeh.embed import server_document
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
import panel as pn
from sliders.pn_app import create_base_chart, get_base_chart_ber, get_base_chart_ger, get_funky_bubble_chart, get_pizza_chart, create_app
from utils.translation import load_translation
from enum import Enum
import logging

base_chart_ber, base_chart_ger = create_base_chart()

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
    # translations = load_translation(language)
    translations = load_translation("de")

    request.app.extra["pizza_chart"] = server_document('http://127.0.0.1:5000/pizza_chart')
    request.app.extra["base_chart_ger"] = server_document('http://127.0.0.1:5000/base_chart_ger')
    request.app.extra["base_chart_ber"] = server_document('http://127.0.0.1:5000/base_chart_ber')
    request.app.extra["funky_bubble_chart"] = server_document('http://127.0.0.1:5000/funky_bubble_chart')

    script = server_document('http://127.0.0.1:5000/app')
    return templates.TemplateResponse("index.html", {"request": request, "script": script, "translations": translations})



pn.serve({
    '/app': create_app, 
    '/pizza_chart': get_pizza_chart, 
    '/base_chart_ger': get_base_chart_ger,
    '/base_chart_ber': get_base_chart_ber,
    # TODO: By replacing the commented out lines with the two above, both graphs of the base_chart are sharing the same filter module. However, they don't change the displayed data and the terminal throws a callback error
    # '/base_chart_ger': base_chart_ger,
    # '/base_chart_ber': base_chart_ber,
    '/funky_bubble_chart': get_funky_bubble_chart
    },
        port=5000, allow_websocket_origin=["127.0.0.1:8000"],
         address="127.0.0.1", show=False)
