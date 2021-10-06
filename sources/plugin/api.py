from sanic import Sanic
from sanic.response import json
from sources.decorators import ratelimitCheck
from sources.utities import generateUrlID
import distutils.util
import hashlib
import validators

def plug_in():
	app = Sanic.get_app("api.fasmga")

	@app.post("/ratelimit")
	@ratelimitCheck()
	async def _ratelimit(request):
		return json({ "authorized": True, "message": "You can use fasmga!" })

	@app.post("/create")
	@ratelimitCheck()
	async def api_create(request):
		if not request.form.get("url"): return json({ "error": 'Missing "url" value into the request' }, 400)
		if not request.form.get("idtype"): return json({ "error": 'Missing "idtype" value into the request' }, 400)
		if not request.form.get("nsfw"): return json({ "error": 'Missing "nsfw" value into the request' }, 400)
		if not validators.url(request.form.get("url")): return json({ "error": 'Value "url" is invalid' }, 400)
		if not request.form.get("idtype") in ["abcdefgh", "abc12345", "aBCde"]: return json({ "error": 'Value "idtype" is invalid' }, 400)
		try: nsfw = distutils.util.strtobool(request.form.get("nsfw").lower())
		except: return json({ "error": 'Value "nsfw" is invalid' }, 400)
		if nsfw == 1: nsfw = True
		else: nsfw = False
		blacklist = await app.ctx.db.config.find_one({ "type": "blacklist" })
		if request.form.get("url") in blacklist["blacklist"]: return json({ "error": 'The URL you inserted as value in "url" is blacklisted.' }, 403)
		if request.form.get("id"):
			urlID = request.form.get("id")
			if len(urlID) > 30: return json({ "error": "The ID you provided is too long (>30)" }, 400)
			if any(bad_character in urlID for bad_character in ["?", "#", "/", "\\", "<", ">"]): return json({ "error": "This ID contains a prohibited character (?, #, \\, <, >" }, 400)
			if (await app.ctx.db.urls.find_one({ "ID": urlID })): return json({ "error": "An url with this ID alredy exist" }, 403)
		else:
			urlID = generateUrlID(request.form.get("idtype"))
			while await app.ctx.db.urls.find_one({ "ID": urlID }):
				urlID = generateUrlID(request.form.get("idtype"))
		userData = await app.ctx.db.users.find_one({ "api_token": request.form.get("token") })
		if request.form.get("password"): password = hashlib.sha512((request.form.get("password")).encode()).hexdigest() #TODO: Change ""encrypt"" method
		else: password = ""
		app.ctx.db.urls.insert_one(
			{
				"ID": urlID,
				"redirect_url": request.form.get("url"),
				"owner": userData["username"],
				"password": password,
				"nsfw": nsfw,
				"clicks": 0
			}
		)
   
		return json({ "success": f"/{urlID}" })

	@app.post("/edit")
	@ratelimitCheck()
	async def api_edit(request):
		if not request.form.get("id"): return json({ "error": 'Missing "id" value into the request' }, 400)
		if not (request.form.get("id") or request.form.get("password") or request.form.get("nsfw")): return json({ "error": 'Missing "url" or "password" or "nsfw" value(s) into the request' }, 400)
		if request.form.get("url") and not validators.url(request.form.get("url")): return json({ "error": 'Value "url" is invalid' }, 400)
		if request.form.get("nsfw"):
			try: nsfw = distutils.util.strtobool(request.form.get("nsfw").lower())
			except: return json({ "error": 'Value "nsfw" is invalid' }, 400)
			if nsfw == 1: nsfw = True
			else: nsfw = False
		else:
			nsfw = None
		urlDocument =  await app.ctx.db.urls.find_one({ "ID": request.form.get("id") })
		if not urlDocument: return json({ "error": 'Value "id" is invalid' }, 400)
		userDocument = await app.ctx.db.users.find_one({ "api_token": request.form.get("token") })
		if not userDocument["username"] == urlDocument["owner"]: return json({ "error": "This url is not yours" }, 403)
		if request.form.get("password"): password = hashlib.sha512((request.form.get("password")).encode()).hexdigest() #TODO: Change ""encrypt"" method
		else: password = ""
		if nsfw == None: nsfw = urlDocument["nsfw"]
		await app.ctx.db.urls.find_one_and_update({ "ID": request.form.get("id") }, 
			{
				"$set": {
					"redirect_url": request.form.get("url") or urlDocument["redirect_url"],
					"password": password or urlDocument["password"],
					"nsfw": nsfw
				}
			}
		)
		return json({ "success": "success" })
 
	@app.post("/list")
	@ratelimitCheck()
	async def api_list(request):
		userData = await app.ctx.db.users.find_one({ "api_token": request.form.get("token") })
		userUrls = []
		async for urlDocument in app.ctx.db.urls.find({ "owner": userData["username"] }):
			del urlDocument["_id"]
			userUrls.append(urlDocument)

		return json(userUrls)

	@app.post("/delete")
	@ratelimitCheck()
	async def api_delete(request):
		if not request.form.get("id"): return json({ "error": 'Missing "id" value into the request' }, 400)
		urlDocument =  await app.ctx.db.urls.find_one({ "ID": request.form.get("id") })
		if not urlDocument: return json({ "error": 'Value "id" is invalid' }, 400)
		userDocument = await app.ctx.db.users.find_one({ "api_token": request.form.get("token") })
		if not userDocument["username"] == urlDocument["owner"]: return json({ "error": "This url is not yours" }, 403)
		await app.ctx.db.urls.find_one_and_delete({ "ID": request.form.get("id") })
		return json({ "success": "success" })

	
