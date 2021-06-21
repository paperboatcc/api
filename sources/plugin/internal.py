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
		try: login = distutils.util.strtobool(request.form.get("login").lower())
		except: return json({ "error": 'Value "nsfw" is invalid' }, 400)
		if login == 1: nsfw = True
		else: login = False
		if not request.form.get("url"): return json({ "error": 'Missing "url" value into the request' }, 400)
		if not request.form.get("idtype"): return json({ "error": 'Missing "idtype" value into the request' }, 400)
		if not request.form.get("nsfw"): return json({ "error": 'Missing "nsfw" value into the request' }, 400)
		if not request.form.get("login"): return json({ "error": 'Missing "login" value into the request' }, 400)
		if not validators.url(request.form.get("url")): return json({ "error": 'Value "url" is invalid' }, 400)
		if not request.form.get("idtype") in ["abcdefgh", "abc12345", "aBCde"]: return json({ "error": 'Value "idtype" is invalid' }, 400)
		try: nsfw = distutils.util.strtobool(request.form.get("nsfw").lower())
		except: return json({ "error": 'Value "nsfw" is invalid' }, 400)
		if nsfw == 1: nsfw = True
		else: nsfw = False
		try: login = distutils.util.strtobool(request.form.get("login").lower())
		except: return json({ "error": 'Value "login" is invalid' }, 400)
		if login == 1: login = True
		else: login = False
		blacklist = await app.ctx.db.config.find_one({ "type": "blacklist" })
		if request.form.get("url") in blacklist["blacklist"]: return json({ "error": 'Value "url" contains an url blacklisted' }, 403)
		if login == True and request.form.get("id"):
			urlID = request.form.get("id")
		else:
			urlID = generateUrlID(request.form.get("idtype"))
			while await app.ctx.db.urls.find_one({ "ID": urlID }):
				urlID = generateUrlID(request.form.get("idtype"))
		userData = await app.ctx.db.users.find_one({ "api_token": request.form.get("token") })
		if request.form.get("password"): password = hashlib.sha512((request.form.get("password")).encode()).hexdigest()
		else: password = ""
		if login:
			app.ctx.db.urls.insert_one(
				{
					"ID": urlID,
					"redirect_url": request.form.get("url"),
					"owner": userData["username"],
					"password": password,
					"nsfw": nsfw
				}
			)
		else:
			app.ctx.db.urls.insert_one(
				{
					"ID": urlID,
					"redirect_url": request.form.get("url"),
					"owner": "anonymous",
					"password": password,
					"nsfw": nsfw
				}
			)
   
		return json({ "success": f"/{urlID}" })

	@app.post("/internal/edit")
	@ratelimitCheck()
	@internalRoute()
	async def internal_edit(request):
		try: login = distutils.util.strtobool(request.form.get("login").lower())
		except: return json({ "error": 'Value "nsfw" is invalid' }, 400)
		if login == 1: nsfw = True
		else: login = False
		if not login == True: return json({ "error": "You need to be logged in" }, 401)
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
		if not userDocument["username"] == urlDocument["owner"]: return json({ "error": "This url is not your" }, 403)
		if request.form.get("password"): password = hashlib.sha512((request.form.get("password")).encode()).hexdigest()
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
 
	@app.post("/internal/list")
	@ratelimitCheck()
	@internalRoute()
	async def internal_list(request):
		try: login = distutils.util.strtobool(request.form.get("login").lower())
		except: return json({ "error": 'Value "nsfw" is invalid' }, 400)
		if login == 1: nsfw = True
		else: login = False
		if not login == True: return json({ "error": "You need to be logged in" }, 401)
		userData = await app.ctx.db.users.find_one({ "api_token": request.form.get("token") })
		userUrls = []
		async for urlDocument in app.ctx.db.urls.find({ "owner": userData["username"] }):
			del urlDocument["_id"]
			userUrls.append(urlDocument)

		return json(userUrls)

	@app.post("/internal/delete")
	@ratelimitCheck()
	@internalRoute()
	async def internal_delete(request):
		try: login = distutils.util.strtobool(request.form.get("login").lower())
		except: return json({ "error": 'Value "nsfw" is invalid' }, 400)
		if login == 1: nsfw = True
		else: login = False
		if not login == True: return json({ "error": "You need to be logged in" }, 401)
		if not request.form.get("id"): return json({ "error": 'Missing "id" value into the request' }, 400)
		urlDocument =  await app.ctx.db.urls.find_one({ "ID": request.form.get("id") })
		if not urlDocument: return json({ "error": 'Value "id" is invalid' }, 400)
		userDocument = await app.ctx.db.users.find_one({ "api_token": request.form.get("token") })
		if not userDocument["username"] == urlDocument["owner"]: return json({ "error": "This url is not your" }, 403)
		await app.ctx.db.urls.find_one_and_delete({ "ID": request.form.get("id") })
		return json({ "success": "success" })
