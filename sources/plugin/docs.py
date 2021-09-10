from sanic import Sanic
from sources.utities import render_template

def plug_in():
	app = Sanic.get_app("api.fasmga")

	@app.get("/")
	async def main(request): return render_template("main.html", 200)
