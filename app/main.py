from bokeh.embed import server_document
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
import panel as pn
from sliders.pn_app import grids
from utils.translation import load_translation
from enum import Enum


class Language(str, Enum):
    en = "en"
    de = "de"


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(GZipMiddleware)
templates = Jinja2Templates(directory="templates")

# TODO: After fixing the BubblePlotter and InteractiveLinePlotter, I can get this list from the config
plot_keys = [
    "fue_pie_interactive",
    "shares_pie_interactive",
    "base_chart",
    "base_chart_ger",
    "base_chart_ber",
    "growth_bubble",
    "coop_partner_bar_interactive",
]

@app.get("/")
@app.get("/{language}/")
async def bkapp_page(request: Request, language: Language = None):
    if language is None:
        language = request.headers.get("accept-language", "de")
    language_code = get_language_code(language)
    # translations = load_translation(language_code)
    translations = load_translation("de")

    for key in plot_keys:
        request.app.extra[key] = server_document(f"http://127.0.0.1:5000/{key}")

    script = server_document("http://127.0.0.1:5000/app")
    response = templates.TemplateResponse("index.html", {
        "request": request, "script": script, "translations": translations, "language_code": language_code})

    return response


def get_language_code(language: Language | str):
    return type(language) is str and language[:2] or language.value


pn.serve({f"{key}": grids[key].servable() for key in plot_keys},
         port=5000, allow_websocket_origin=["127.0.0.1:8000"], address="127.0.0.1", show=False
         )
