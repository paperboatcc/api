from sanic import Sanic, Request
from sanic.response import json
from sources.decorators import argsCheck, ratelimitCheck
from sources.utities import generateUrlID
import json as jsonModule
import hashlib
import validators

def plug_in():
	app = Sanic.get_app("api.fasmga")

	@app.get("/ratelimit")
	async def ratelimit(request: Request):
		userData = await app.ctx.db.users.find_one({ "api_token": request.headers.get("Authorization") })
		if not userData: return json({ "bad_request": "Token you provvided is invalid" }, 400)

		ratelimitJsonF = open("sources/ratelimit.json", "r")
		ratelimitJson = jsonModule.loads(ratelimitJsonF.read())
		ratelimitJsonF.close()

		current = 0

		if not userData["username"] in ratelimitJson: current = 0
		else: current = ratelimitJson[userData["username"]]

		return json({ "message": "You can use fasmga!" if current < 20 else "You are ratelimited", "remain": 20 - current if 20 - current >= 0 else 0 }, 200 if 20 - current >= 0 else 429)

	@app.get("/user")
	@ratelimitCheck()
	async def user_data(request: Request):
		userData = await app.ctx.db.users.find_one({ "api_token": request.headers.get("Authorization") })
		if not userData: return json({ "bad_request": "Token you provvided is invalid" }, 400)

		del userData["_id"]
		del userData["password"]
		del userData["login_token"]
		del userData["api_token"]
		del userData["totp"]

		return json(userData)

	@app.post("/testing/create")
	@argsCheck(["url", "nsfw"], ["url to short", bool])
	@ratelimitCheck()
	async def create_api(request: Request):
		if not "idtype" in request.json and not "id" in request.json: return json({ "error": 'Missing value is idtype', "types": "idtype is one from 'abcdefgh', 'abc12345' or 'aBCde'" }, 400)
		if not validators.url(request.json["url"]): return json({ "error": 'Value "url" is invalid', "types": "id is a valid http or https url" }, 400)
		if not "id" in request.json and "idtype" in request.json and not request.json["idtype"] in ["abcdefgh", "abc12345", "aBCde"] and not "id" in request.json: 
			return json({ "error": 'Value "idtype" is invalid', "types": "idtype is one from 'abcdefgh', 'abc12345' or 'aBCde'"  }, 400)

		blacklist = await app.ctx.db.config.find_one({ "type": "blacklist" })
		if request.json["url"] in blacklist["blacklist"]: return json({ "error": 'The URL you inserted as value in "url" is blacklisted.' }, 403)

		if "id" in request.json:
			urlID = request.json["id"]
			if len(urlID) > 30: return json({ "error": "The ID you provided is too long (>30)" }, 400)
			if any(bad_character in urlID for bad_character in ["?", "#", "/", "\\", "<", ">"]): return json({ "error": "This ID contains a prohibited character (?, #, \\, <, >" }, 400)
			if (await app.ctx.db.urls.find_one({ "ID": urlID })): return json({ "error": "An url with this ID alredy exist" }, 403)

		else:
			urlID = generateUrlID(request.json["idtype"])
			while await app.ctx.db.urls.find_one({ "ID": urlID }):
				urlID = generateUrlID(request.json["idtype"])
	
		userData = await app.ctx.db.users.find_one({ "api_token": request.headers.get("Authorization") })
		if "password" in request.json: password = hashlib.sha512((request.json["password"]).encode()).hexdigest() #TODO: Change ""encrypt"" method
		else: password = ""
		app.ctx.db.urls.insert_one(
			{
				"ID": urlID,
				"redirect_url": request.json["url"],
				"owner": userData["username"],
				"password": password,
				"nsfw": request.json["nsfw"],
				"clicks": 0,
				"captcha": False,
				"deletedate": 0,
				"editinfo": {},
				"unembedify": False
			}
		)
   
		return json({ "success": f"/{urlID}" })
