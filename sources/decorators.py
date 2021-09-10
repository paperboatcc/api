from functools import wraps
from sanic import Sanic
from sanic.response import json
from sanic.log import logger
from sources.utities import tempBanRemove
import json as jsonModule

app = Sanic.get_app("api.fasmga")

def ratelimitCheck():
	def decorator(f):
		@wraps(f)
		async def decorated_function(request, *args, **kwargs):
			if not request.form.get("token"): 
				return json({ "bad_request": "You must do a request with token value!" }, 400)
			userData = await app.ctx.db.users.find_one({ "api_token": request.form.get("token") })
			if not userData:
				return json({ "bad_request": "Token you provvided is invalid" }, 400)
			user = userData["username"]
			if (userData["is_banned"] == True): 
				logger.warning(f"{userData['username']} e bannato e sta tentando di accedere ({request.ip})")
				return json({ "banned": "You are banned from api, you can try to contact fasmga staff to get unban" }, 401)

			jsonFile = open("sources/ratelimit.json", "r")
			jsonValue = jsonModule.load(jsonFile)
			jsonFile.close()
			if user == 'anonymous':
				if not 'anonymous' in jsonValue: jsonValue['anonymous'] = {}
				if not request.ip in jsonValue['anonymous']: jsonValue['anonymous'][request.ip] = 0
				if jsonValue['anonymous'][request.ip] <= 20:
					jsonValue['anonymous'][request.ip] += 1
					jsonw = open("sources/ratelimit.json", "w")
					jsonModule.dump(jsonValue, jsonw, indent = 2, sort_keys = True)
					jsonw.close()
					response = await f(request, *args, **kwargs)
					return response
				else:
					jsonValue['anonymous'][request.ip] += 1
					jsonw = open("sources/ratelimit.json", "w")
					jsonModule.dump(jsonValue, jsonw, indent = 2, sort_keys = True)
					jsonw.close()
					if (jsonValue['anonymous'][request.ip] >= 50):
						if (jsonValue['anonymous'][request.ip] == 50):
							app.ctx.webhook.post(content = f"⚠️ | Warning, {request.ip} done 50 request in less than a minute") 
						if (jsonValue['anonymous'][request.ip] == 100):
							app.ctx.webhook.post(content = f"ℹ️ | Just for information, I can't ban {request.ip} but he / she did 100 requests in less than a minute")
							logger.warning(f"{request.ip} e bannato e sta tentando di accedere")
							return json({ "SOTP": "okey, but now STOP! then i obbligated to ban you, you can try to contact fasmga staff to get unban" }, 401)
						return json({ "ddos": "Are you trying to DDoS our API? Asking for a friend :)" }, 429)
					return json({ "ratelimit": "You did >20 requests to the API in this minute. Wait a minute and try again." }, 429)
			else:
				if not user in jsonValue: jsonValue[user] = 0
				if jsonValue[user] <= 20:
					jsonValue[user] += 1
					jsonw = open("sources/ratelimit.json", "w")
					jsonModule.dump(jsonValue, jsonw, indent = 2, sort_keys = True)
					jsonw.close()
					response = await f(request, *args, **kwargs)
					return response
				else:
					jsonValue[user] += 1
					jsonw = open("sources/ratelimit.json", "w")
					jsonModule.dump(jsonValue, jsonw, indent = 2, sort_keys = True)
					jsonw.close()
					if (jsonValue[user] >= 50):
						if (jsonValue[user] == 50):
							app.ctx.webhook.post(content = f"⚠️ | Warning, {user} done 50 request in less than a minute") 
						if (jsonValue[user] == 100):
							await app.ctx.db.users.find_one_and_update({ "api_token": request.form.get("token") }, { "$set": { "is_banned": True }})
							app.ctx.webhook.post(content = f"ℹ️ | Just for information, I banned {user} because it did 100 requests in less than a minute")
							logger.warning(f"{user} e bannato e sta tentando di accedere ({request.ip})")
							return json({ "SOTP": "okey, but now STOP! then i obbligated to ban you, you can try to contact fasmga staff to get unban" }, 401)
						return json({ "ddos": "Are you trying to DDoS our API? Asking for a friend :)" }, 429)
					return json({ "ratelimit": "You did >20 requests to the API in this minute. Wait a minute and try again." }, 429)
		return decorated_function
	return decorator

def internalRoute():
	def decorator(f):
		@wraps(f)
		async def decorated_function(request, *args, **kwargs):
			userData = await app.ctx.db.users.find_one({ "api_token": request.form.get("token") })
			if not userData:
				return json({ "bad_request": "Token you provvided is invalid" }, 400)
			user = userData['username']
			if userData["is_banned"]:
				logger.warning(f"{user} e bannato e sta tentando di accedere ({request.ip})")
				return json({ "banned": "You are banned from api, you can try to contact fasmga staff to get unban" }, 401)
			if not request.ip == "127.0.0.1":
				await app.ctx.db.users.find_one_and_update({ "api_token": request.form.get("token") }, { "$set": { "is_banned": True }})
				app.add_task(tempBanRemove(request.form.get("token")))
				app.ctx.webhook.post(content = f"⚠️ | Warning, {user} is trying to access to internal APIs", username = "Fasm.ga Iternal")
				logger.warning(f"{userData['username']} e stato temp bannato ({request.ip})")
				return json({ "unauthorized": "You can't access to internal APIs, use normal APIs instead, for security reason you are temp-banned for 10 minutes" }, 401)
			response = await f(request, *args, **kwargs)
			return response
		return decorated_function
	return decorator