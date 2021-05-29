from sanic import Sanic
from sanic.response import file

def plug_in():
	app = Sanic.get_app("api.fasmga.org")

	@app.get("/favicon.ico")
	async def favicon(request): return await file("Public/favicon.ico")
