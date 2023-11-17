from enum import Enum

from bokeh.embed import server_document
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import panel as pn
from sliders.pn_app import chart_collection
from utils.translation import load_translation

load_dotenv()

SERVER_ADDRESS = os.getenv('SERVER_ADDRESS')
PANEL_PORT = int(os.getenv('PANEL_PORT'))
FASTAPI_PORT = int(os.getenv('FASTAPI_PORT'))
PROXY_PANEL_THROUGH_FASTAPI = os.getenv('PROXY_PANEL_THROUGH_FASTAPI', 'False').lower() == 'true'
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')


class Language(str, Enum):
    en = "en"
    de = "de"


app = FastAPI()
if PROXY_PANEL_THROUGH_FASTAPI:
    # Also serve statics from bokeh and panel directly
    app.mount("/static/extensions/panel", StaticFiles(packages=[('panel', 'dist')]), name="panelstatic")
    app.mount("/static", StaticFiles(directory="static", packages=[('bokeh', 'server/static')]), name="static")
else:
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

    if RENDER_EXTERNAL_HOSTNAME:
        server_base_path = f"{request.url.scheme}://{RENDER_EXTERNAL_HOSTNAME}/panel"
    elif PROXY_PANEL_THROUGH_FASTAPI:
        server_base_path = f"{request.url.scheme}://{SERVER_ADDRESS}:{FASTAPI_PORT}/panel"
    else:
        server_base_path = f"{request.url.scheme}://{SERVER_ADDRESS}:{PANEL_PORT}"

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

if PROXY_PANEL_THROUGH_FASTAPI:
    # Forward the websockets through a bridge
    from fastapi import WebSocket
    import websockets
    import asyncio
    from starlette.websockets import WebSocketDisconnect
    from websockets.exceptions import ConnectionClosedOK

    @app.websocket("/panel/{plot_key}/ws")
    async def websocket_endpoint(ws_client: WebSocket, plot_key: str):
        await ws_client.accept()
        subprotocols = ws_client.headers['sec-websocket-protocol'].split(', ')
        uri = f"ws://{SERVER_ADDRESS}:{PANEL_PORT}/{plot_key}/ws"
        async with websockets.connect(uri, subprotocols=subprotocols) as ws_server:

            async def listen_to_client():
                try:
                    while True:
                        data = await ws_client.receive_text()
                        await ws_server.send(data)
                except WebSocketDisconnect:
                    await ws_server.close()

            async def listen_to_server():
                try:
                    while True:
                        data = await ws_server.recv()
                        await ws_client.send_text(data)
                except ConnectionClosedOK:
                    pass

            await asyncio.gather(listen_to_client(), listen_to_server())

    # Also stream/serve other panel specific content, especifically the autoload.js
    from starlette.requests import Request
    from starlette.responses import StreamingResponse
    from starlette.background import BackgroundTask

    import httpx

    client = httpx.AsyncClient(base_url=f"http://{SERVER_ADDRESS}:{PANEL_PORT}")

    async def _reverse_proxy(request: Request):
        # remove /panel from path
        url_path = request.url.path.removeprefix('/panel')
        url = httpx.URL(path=url_path, query=request.url.query.encode("utf-8"))
        rp_req = client.build_request(request.method, url,
                                    headers=request.headers.raw,
                                    content=await request.body())
        rp_resp = await client.send(rp_req, stream=True)
        return StreamingResponse(
            rp_resp.aiter_raw(),
            status_code=rp_resp.status_code,
            headers=rp_resp.headers,
            background=BackgroundTask(rp_resp.aclose),
        )

    app.add_route("/panel/{path:path}", _reverse_proxy, ["GET", "POST"])


pn.config.css_files.append("static/css/main.css")


pn.serve({key: chart_collection[key].servable() for key in plot_keys},
         port=PANEL_PORT,
         allow_websocket_origin=[f"{SERVER_ADDRESS}:{FASTAPI_PORT}", RENDER_EXTERNAL_HOSTNAME or SERVER_ADDRESS],
         address=SERVER_ADDRESS,
         show=False)
