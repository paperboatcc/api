from sanic import Sanic
from sanic.response import json
from sources.decorators import internalRoute, ratelimitCheck
from sources.utities import generateUrlID
import validators
import distutils.util
import hashlib

def plug_in():
	app = Sanic.get_app("api.fasmga")

	@app.post("/internal/create")
	@ratelimitCheck()
	@internalRoute()
	async def internal_create(request):
		if not request.form.get("url"): return json({ "error": "Missing \"url\" value into the request" }, 400)
		if not request.form.get("idtype"): return json({ "error": "Missing \"idtype\" value into the request" }, 400)
		if not request.form.get("idtype") in ["abcdefgh", "abc12345", "aBCde"]: return json({ "error": "Value \"idtype\" is invalid" }, 400)
		if not request.form.get("nsfw"): return json({ "error": "Missing \"nsfw\" value into the request" }, 400)
		if not validators.url(request.form.get("url")): return json({ "error": "Value \"url\" is invalid" }, 400)
		try: nsfw = distutils.util.strtobool(request.form.get("nsfw").lower())
		except: return json({ "error": "Value \"nsfw\" is invalid" }, 400)
		if nsfw == 1: nsfw = True
		else: nsfw = False
		blacklist = await app.ctx.db.config.find_one({ "type": "blacklist" })
		if request.form.get("url") in blacklist["blacklist"]: return json({ "error": "Value \"url\" contains an url blacklisted" }, 403)
		urlID = generateUrlID(request.form.get("idtype"))
		while await app.ctx.db.urls.find_one({ "ID": urlID }):
			urlID = generateUrlID(request.form.get("idtype"))
		userData = await app.ctx.db.users.find_one({ "api_token": request.form.get("token") })
		app.ctx.db.urls.insert_one(
			{
				"ID": urlID,
				"redirect_url": request.form.get("url"),
				"owner": userData["username"],
				"password": hashlib.sha512((request.form.get("password") or "").encode()).hexdigest(),
				"nsfw": nsfw
			}
		)

		return json({ "success": f"/{urlID}" })