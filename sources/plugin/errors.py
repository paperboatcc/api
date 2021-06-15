from sanic import Sanic
from sanic.exceptions import NotFound
from sources.utities import render_template

def plug_in():
	app = Sanic.get_app("api.fasmga")

	@app.exception(NotFound)
	async def error_404(request, exception): return render_template("error.html", code = "404", text = "Not found")