from sanic import Sanic
from sanic.exceptions import NotFound, MethodNotSupported
from sanic.response import json
from sources.utities import render_template

def plug_in():
	app = Sanic.get_app("api.fasmga")

	@app.exception(NotFound)
	async def error_404(request, exception):
		if request.method == "GET":
			return render_template("error.html", 404, code = "404", text = "Not found")
		else:
			return json({ "error": "Not Found" })
 
	@app.exception(MethodNotSupported)
	async def error_405(request, exception): 
		return json({ "error": f"Method {request.method} not allowed" }, 405)