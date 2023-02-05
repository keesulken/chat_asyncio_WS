import os

import aiohttp
from aiohttp import web


async def wshandler(request: web.Request):
    resp = web.WebSocketResponse(autoping=True, heartbeat=10.0)
    available = resp.can_prepare(request)
    if not available:
        with open('websocket.html', "rb") as fp:
            return web.Response(body=fp.read(), content_type="text/html")

    await resp.prepare(request)

    await resp.send_str("Welcome!!!")

    try:
        print("Someone joined.")
        for ws in request.app["sockets"]:
            await ws.send_str("Someone joined")
        request.app["sockets"].append(resp)

        async for msg in resp:
            if msg.type == web.WSMsgType.TEXT:
                if (msg.data[:4] == 'news') and (" " in msg.data):
                    cat = msg.data.split(' ')[1]
                    data = None
                    if cat in ['sports', 'cars', 'food', 'music']:
                        data = cat
                    if data:
                        async with aiohttp.ClientSession() as session:
                            async with session.post('http://localhost:8080/news', data=data) as cl_resp:
                                news_str = await cl_resp.text()
                        for ws in request.app["sockets"]:
                            if ws is not resp:
                                await ws.send_str(msg.data)
                            await ws.send_str(news_str)
                    else:
                        for ws in request.app["sockets"]:
                            if ws is not resp:
                                await ws.send_str(msg.data)
                            await ws.send_str(f'Incorrect request: {msg.data}')
                else:
                    for ws in request.app["sockets"]:
                        if ws is not resp:
                            await ws.send_str(msg.data)
            else:
                return resp
        return resp

    finally:
        request.app["sockets"].remove(resp)
        print("Someone disconnected.")
        for ws in request.app["sockets"]:
            await ws.send_str("Someone disconnected.")


async def news_handler(request):
    news_db = {
        'sports': "Jamie Carragher backs Jurgen Klopp to lead Liverpool rebuild | 'Four or five players needed'",
        'cars': 'Feds Revise EV Tax Credit Rules So More Vehicles Can Be Called SUVs',
        'food': 'Scientists uncover why chocolate feels so good to eat - and how it could be made healthier',
        'music': 'Jack White to perform on ‘Saturday Night Live’ later this month',
    }
    text = news_db[await request.text()]
    return web.Response(text=text)


async def on_shutdown(app: web.Application):
    for ws in app["sockets"]:
        await ws.close()


def init():
    app = web.Application()
    app["sockets"] = []
    app.router.add_routes([web.get("/", wshandler),
                           web.post('/news', news_handler)
                           ])
    app.on_shutdown.append(on_shutdown)
    return app


web.run_app(init())