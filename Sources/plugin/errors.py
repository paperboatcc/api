from sanic import Sanic
from sanic.exceptions import NotFound
from sanic.response import html

def plug_in():
	app = Sanic.get_app("api.fasmga")

	@app.exception(NotFound)
	async def error_404(request, exception): return html(open("Sources/main.html").read())