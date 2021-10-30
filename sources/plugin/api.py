from sanic import Sanic, Request
from sanic.response import json
from sources.decorators import argsCheck, ratelimitCheck
from sources.utility import generateUrlID
import json as jsonModule
import hashlib
import validators
import pyotp
import uuid
import time

app = Sanic.get_app("api.fasmga")

@app.get("/ratelimit")
async def _ratelimit(request: Request):
	userData = await app.ctx.db.users.find_one({ "api_token": request.headers.get("Authorization") })
	if not userData: return json({ "bad_request": "Token you provided is invalid" }, 400)

	ratelimitJsonF = open("sources/ratelimit.json", "r") 
	ratelimitJson = jsonModule.loads(ratelimitJsonF.read())
	ratelimitJsonF.close()

	current = 0

	if not userData["username"] in ratelimitJson: current = 0
	else: current = ratelimitJson[userData["username"]]

	return json({ "message": "You can use fasmga!" if current < 20 else "You are ratelimited", "remain": 20 - current if 20 - current >= 0 else 0 }, 200 if 20 - current >= 0 else 429)

@app.get("/user")
@ratelimitCheck()
async def _user_data(request: Request):
	userData = await app.ctx.db.users.find_one({ "api_token": request.headers.get("Authorization") })
	if not userData: return json({ "bad_request": "Token you provided is invalid" }, 400)

	del userData["_id"]
	del userData["password"]
	del userData["login_token"]
	del userData["api_token"]
	del userData["totp"]

	return json(userData)

@app.post("/testing/create")
@argsCheck("required", ["url", "nsfw"], ["url to short", bool])
@ratelimitCheck()
async def _create_api(request: Request):
	if not "idtype" in request.json and not "id" in request.json: return json({ "error": 'Missing value is idtype', "types": "idtype is one from 'abcdefgh', 'abc12345' or 'aBCde'" }, 400)
	if not validators.url(request.json["url"]): return json({ "error": 'Value "url" is invalid', "types": "id is a valid http or https url" }, 400)
	if not "id" in request.json and "idtype" in request.json and not request.json["idtype"] in ["abcdefgh", "abc12345", "aBCde"] and not "id" in request.json: 
		return json({ "error": 'Value "idtype" is invalid', "types": "idtype is one from 'abcdefgh', 'abc12345' or 'aBCde'"  }, 400)

	if not request.json["url"].__class__.__name__ == "str": return json({ "error": "Invalid data type for 'url'", "types": "url is a str (or a string if you prefer) and it's the url to short" }, 400)
	if not request.json["nsfw"].__class__.__name__ == "bool": return json({ "error": "Invalid data type for 'nsfw'", "types": "nsfw is a bool (or a boolean if you prefer)" }, 400)

	blacklist = await app.ctx.db.config.find_one({ "type": "blacklist" })
	if request.json["url"] in blacklist["blacklist"]: return json({ "error": 'The URL you inserted is blacklisted.' }, 403)

	if "id" in request.json:
		urlID = request.json["id"]
		if not urlID.__class__.__name__ == "str": return json({ "error": "Invalid data type for 'id'", "types": "id is a str (or a string if you prefer) and it's id for the shorted url" }, 400)
		if len(urlID) > 30: return json({ "error": "The ID you provided is too long (>30)" }, 400)
		if any(bad_character in urlID for bad_character in ["?", "#", "/", "\\", "<", ">"]): return json({ "error": "This ID contains a prohibited character (?, #, \\, <, >" }, 400)
		if (await app.ctx.db.urls.find_one({ "ID": urlID })): return json({ "error": "An url with this ID already exist" }, 403)
	else:
		urlID = generateUrlID(request.json["idtype"])
		while await app.ctx.db.urls.find_one({ "ID": urlID }):
			urlID = generateUrlID(request.json["idtype"])

	if "captcha" in request.json:
		if not request.json["captcha"].__class__.__name__ == "bool": return json({ "error": "Invalid data type for 'captcha'", "types": "captcha is a bool (or a boolean if you prefer)" }, 400)
		captcha = request.json["captcha"]
	else:
		captcha = False

	if "unembedify" in request.json:
		if not request.json["unembedify"].__class__.__name__ == "bool": return json({ "error": "Invalid data type for 'unembedify'", "types": "unembedify is a bool (or a boolean if you prefer)" }, 400)
		unembedify = request.json["unembedify"]
	else:
		unembedify = False

	
	userData = await app.ctx.db.users.find_one({ "api_token": request.headers.get("Authorization") })
	if "password" in request.json: password = hashlib.sha512(str(request.json["password"]).encode()).hexdigest() #TODO: Change ""encrypt"" method
	else: password = ""
	app.ctx.db.urls.insert_one(
		{
			"ID": urlID,
			"redirect_url": request.json["url"],
			"owner": userData["username"],
			"password": password,
			"nsfw": request.json["nsfw"],
			"clicks": 0,
			"captcha": captcha,
			"deletedate": 0,
			"editinfo": {},
			"unembedify": unembedify, 
			"securitytype": "password" if not password == "" else "none",
			"securitytotp": pyotp.random_base32(),
			"qruuid1": uuid.uuid4().__str__(),
			"qruuid2": uuid.uuid4().__str__(),
			"creationdate": int(time.time())
		}
	)

	return json({ "success": f"/{urlID}" })

@app.get("/testing/get")
@ratelimitCheck()
async def _get_api(request: Request):
	userData = await app.ctx.db.users.find_one({ "api_token": request.headers.get("Authorization") })
	userUrls = []
	async for urlDocument in app.ctx.db.urls.find({ "owner": userData["username"] }):
		del urlDocument["_id"]
		del urlDocument["password"]
		del urlDocument["qruuid1"]
		del urlDocument["qruuid2"]
		del urlDocument["securitytotp"]

		userUrls.append(urlDocument)

	return json(userUrls)

@app.delete("/testing/delete")
@ratelimitCheck()
async def delete_api(request: Request):
	if not request.args.get("id"): return json({ "error": "Missing value is url", "type": "id is the id of the url to delete (PS. on args, not on body!)" }, 400)
	if len(request.args["id"]) > 1: return json({ "status": "I'm a teapot!", "error": "You you kidding me? You think i'm dumb?" }, 418)
	urlDocument =  await app.ctx.db.urls.find_one({ "ID": request.args.get("id") })
	if not urlDocument: return json({ "error": 'Value "id" is invalid' }, 400)

	userDocument = await app.ctx.db.users.find_one({ "api_token": request.headers.get("Authorization") })
	if not userDocument["username"] == urlDocument["owner"]: return json({ "error": "This url is not yours" }, 403)

	await app.ctx.db.urls.find_one_and_delete({ "ID": request.args.get("id") })

	return json({ "success": "success" })

@app.patch("/testing/edit")
@argsCheck("optional", ["password", "nsfw", "captcha", "unembedify"], ["password of the url (use #remove# to remove password)", bool, bool, bool])
@ratelimitCheck()
async def _edit_api(request: Request):
	if not request.args.get("id"): return json({ "error": "Missing value is url", "type": "id is the id of the url to delete (PS. on args, not on body!)" }, 400)
	if len(request.args["id"]) > 1: return json({ "status": "I'm a teapot!", "error": "You you kidding me? You think i'm dumb?" }, 418)

	urlDocument =  await app.ctx.db.urls.find_one({ "ID": request.args.get("id") })
	if not urlDocument: return json({ "error": 'Value "id" is invalid' }, 400)

	password = request.json["password"] if "password" in request.json else urlDocument["password"]
	securitytype = urlDocument["securitytype"]
	nsfw = request.json["nsfw"] if "nsfw" in request.json else urlDocument["nsfw"]
	captcha = request.json["captcha"] if "captcha" in request.json else urlDocument["captcha"]
	unembedify = request.json["unembedify"] if "unembedify" in request.json else urlDocument["unembedify"]

	if not password.__class__.__name__ == "str": return json({ "error": "Invalid data type for 'password'", "types": "password is a str (or a string if you prefer) and it's the password for the url" }, 400)
	if not nsfw.__class__.__name__ == "bool": return json({ "error": "Invalid data type for 'nsfw'", "types": "nsfw is a bool (or a boolean if you prefer)" }, 400)
	if not captcha.__class__.__name__ == "bool": return json({ "error": "Invalid data type for 'captcha'", "types": "captcha is a bool (or a boolean if you prefer)" }, 400)
	if not unembedify.__class__.__name__ == "bool": return json({ "error": "Invalid data type for 'unembedify'", "types": "unembedify is a bool (or a boolean if you prefer)" }, 400)

	if password == "#remove#": 
		password = ""
		securitytype = "none"
	elif "password" in request.json: 
		password = hashlib.sha512((password).encode()).hexdigest() #TODO: Change ""encrypt"" method
		securitytype = "password"

	userDocument = await app.ctx.db.users.find_one({ "api_token": request.headers.get("Authorization") })
	if not userDocument["username"] == urlDocument["owner"]: return json({ "error": "This url is not yours" }, 403)

	await app.ctx.db.urls.find_one_and_update({ "ID": request.args.get("id") }, 
		{
			"$set": {
				"password": password,
				"nsfw": nsfw,
				"captcha": captcha,
				"unembedify": unembedify,
				"securitytype": securitytype,
			}
		}
	)

	return json({ "success": "success" })
