from enum import Enum
import os

from bokeh.embed import server_document
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import panel as pn

from .plot.layout import chart_collection
from .utils.translation import load_translation


load_dotenv()

SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")
PANEL_PORT = int(os.getenv("PANEL_PORT"))
FASTAPI_PORT = int(os.getenv("FASTAPI_PORT"))
PROXY_PANEL_THROUGH_FASTAPI = (
    os.getenv("PROXY_PANEL_THROUGH_FASTAPI", "False").lower() == "true"
)
RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")


class Language(str, Enum):
    en = "en"
    de = "de"


app = FastAPI()
if PROXY_PANEL_THROUGH_FASTAPI:
    # Also serve statics from bokeh and panel directly
    app.mount(
        "/static/extensions/panel",
        StaticFiles(packages=[("panel", "dist")]),
        name="panelstatic",
    )
    app.mount(
        "/static",
        StaticFiles(directory="app/static", packages=[("bokeh", "server/static")]),
        name="static",
    )
else:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.add_middleware(GZipMiddleware)
templates = Jinja2Templates(directory="app/templates")


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
        server_base_path = (
            f"{request.url.scheme}://{SERVER_ADDRESS}:{FASTAPI_PORT}/panel"
        )
    else:
        server_base_path = f"{request.url.scheme}://{SERVER_ADDRESS}:{PANEL_PORT}"

    for key in chart_collection:
        request.app.extra[key] = server_document(f"{server_base_path}/{key}")

    script = server_document(f"{server_base_path}/app")
    response = templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "script": script,
            "translations": translations,
            "language_code": language_code,
        },
    )

    return response


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/static/favicon.ico")


def get_language_code(language: Language | str):
    return isinstance(language, str) and language[:2] or language.value


if PROXY_PANEL_THROUGH_FASTAPI:
    # Custom solution inspired by https://github.com/tiangolo/fastapi/discussions/7382
    # to be able to understand what is happening and adjust to bokeh specific protocol.
    # If one day broken, you may use and adapt this library
    # https://github.com/WSH032/fastapi-proxy-lib
    import asyncio
    from fastapi import WebSocket
    import httpx
    import logging
    from starlette.websockets import WebSocketDisconnect
    from starlette.requests import Request
    from starlette.responses import StreamingResponse
    from starlette.background import BackgroundTask
    import websockets
    from websockets.exceptions import ConnectionClosedOK

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)

    # Forward the websockets through a bridge
    @app.websocket("/panel/{plot_key}/ws")
    async def websocket_endpoint(ws_client: WebSocket, plot_key: str):
        # Check that the bokehJS client requests the expected subprotocol defined in
        # bokeh.server.views.ws.py in WSHandler.open()/select_subprotocol()
        subprotocols = ws_client.get("subprotocols")
        if (
            not subprotocols
            or not isinstance(subprotocols, list)
            or not len(subprotocols) == 2
            or not subprotocols[0] == "bokeh"
        ):
            logger.warning(f"Subprotocols {subprotocols} not of the awaited format")
        # Accept the Websocket, adding bokeh as subprotocol in the server response
        await ws_client.accept(subprotocol=subprotocols[0])

        # Connect internally to the bokeh server, adding the subprotocol list
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

            # Sync the upstream and downstream websockets through asyncio
            await asyncio.gather(listen_to_client(), listen_to_server())

    # Also stream/serve other panel specific content, especifically the autoload.js
    client = httpx.AsyncClient(base_url=f"http://{SERVER_ADDRESS}:{PANEL_PORT}")

    @app.api_route("/panel/{path_name:path}", methods=["GET"])
    async def _reverse_proxy(request: Request, path_name: str):
        url = httpx.URL(path=path_name, query=request.url.query.encode("utf-8"))
        rp_req = client.build_request(
            request.method,
            url,
            headers=request.headers.raw,
            content=await request.body(),
        )
        rp_resp = await client.send(rp_req, stream=True)
        return StreamingResponse(
            rp_resp.aiter_raw(),
            status_code=rp_resp.status_code,
            headers=rp_resp.headers,
            background=BackgroundTask(rp_resp.aclose),
        )


pn.config.css_files.append("static/css/main.css")


pn.serve(
    {key: chart_collection[key].servable() for key in chart_collection},
    port=PANEL_PORT,
    allow_websocket_origin=[
        f"{SERVER_ADDRESS}:{FASTAPI_PORT}",
        RENDER_EXTERNAL_HOSTNAME or SERVER_ADDRESS,
    ],
    address=SERVER_ADDRESS,
    show=False,
)
