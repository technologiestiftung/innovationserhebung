from enum import Enum

from bokeh.embed import server_document
from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import panel as pn
from sliders.pn_app import chart_collection
from utils.translation import load_translation


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

    server_base_path = f"http://127.0.0.1:5000"

    for key in plot_keys:
        request.app.extra[key] = server_document(f"{server_base_path}/{key}")

    script = server_document(f"{server_base_path}/app")
    response = templates.TemplateResponse("index.html", {
        "request": request, "script": script, "translations": translations, "language_code": language_code})

    return response


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("favicon.ico")


def get_language_code(language: Language | str):
    return type(language) is str and language[:2] or language.value

pn.config.css_files.append("static/css/main.css")


pn.serve({f"{key}": chart_collection[key].servable() for key in plot_keys},
         port=5000,
         allow_websocket_origin=["127.0.0.1:8000", "0.0.0.0:8000"],
         address="127.0.0.1",
         show=False)
