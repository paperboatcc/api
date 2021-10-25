from sanic import Sanic
from sanic.response import file


app = Sanic.get_app("api.fasmga")

@app.get("/favicon.ico")
async def favicon(request): return await file("assets/favicon.ico")
