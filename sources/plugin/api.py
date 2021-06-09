from sanic import Sanic
from sanic.response import json
from sources.decorators import ratelimitCheck
import json as jsonModule
import asyncio

def plug_in():
	app = Sanic.get_app("api.fasmga")

	async def ratelimitReset():
		while True:
			jsonValues = jsonModule.load(open("sources/ratelimit.json"))
			for jsonValue in jsonValues:
				jsonValues[jsonValue] = 0
			jsonModule.dump(jsonValues, open("sources/ratelimit.json", "w"), indent = 2, sort_keys = True)
			await asyncio.sleep(60)

	app.add_task(ratelimitReset())

	@app.post("/ratelimit")
	@ratelimitCheck()
	async def _ratelimit(request):
		return json({ "authorized": True, "message": "You can continue to use fasmga!" })

	