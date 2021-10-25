from sanic import Sanic
from sources.utility import render_template

app = Sanic.get_app("api.fasmga")

@app.get("/")
async def main(request): return render_template("main.html", 200)
