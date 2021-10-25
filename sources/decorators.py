from functools import wraps
import traceback
from sanic import Request, Sanic
from sanic.response import json
from sanic.log import logger
from sources.utility import tempBanRemove
import json as jsonModule

app = Sanic.get_app("api.fasmga")

def ratelimitCheckLegacy(): #? This will be deleted when testing api are stabile
	def decorator(f):
		@wraps(f)
		async def decorated_function(request: Request, *args, **kwargs):
			client_ip = request.forwarded.get('for')
			if not request.form.get("token"): 
				return json({ "bad_request": "You must do a request with token value!" }, 400)
			userData = await app.ctx.db.users.find_one({ "api_token": request.form.get("token") })
			if not userData:
				return json({ "bad_request": "Token you provided is invalid" }, 400)
			user = userData["username"]
			if (userData["is_banned"] == True): 
				logger.warning(f"{userData['username']} e bannato e sta tentando di accedere ({client_ip})")
				return json({ "banned": "You are banned from api, you can try to contact fasmga staff to get unban" }, 401)

			jsonFile = open("sources/ratelimit.json", "r")
			jsonValue = jsonModule.load(jsonFile)
			jsonFile.close()
			if user == 'anonymous':
				if not 'anonymous' in jsonValue: jsonValue['anonymous'] = {}
				if not client_ip in jsonValue['anonymous']: jsonValue['anonymous'][client_ip] = 0
				if jsonValue['anonymous'][client_ip] <= 20:
					jsonValue['anonymous'][client_ip] += 1
					jsonw = open("sources/ratelimit.json", "w")
					jsonModule.dump(jsonValue, jsonw, indent = 2, sort_keys = True)
					jsonw.close()
					response = await f(request, *args, **kwargs)
					return response
				else:
					jsonValue['anonymous'][client_ip] += 1
					jsonw = open("sources/ratelimit.json", "w")
					jsonModule.dump(jsonValue, jsonw, indent = 2, sort_keys = True)
					jsonw.close()
					if (jsonValue['anonymous'][client_ip] >= 50):
						if (jsonValue['anonymous'][client_ip] == 50): app.ctx.webhook.post(content = f"⚠️ | Warning, {client_ip} done 50 request in less than a minute") 
						if (jsonValue['anonymous'][client_ip] == 100):
							logger.warning(f"{client_ip} e bannato e sta tentando di accedere")
							app.ctx.webhook.post(content = f"ℹ️ | Just for information, I can't ban {client_ip} but he / she did 100 requests in less than a minute")
						if (jsonValue['anonymous'][client_ip] >= 100): 
							return json({ "STOP": "okay, but now SOTP!" }, 401)
						return json({ "ddos": "Are you trying to DDoS our API? Asking for a friend :)" }, 429)
					if (jsonValue['anonymous'][client_ip] == 20): app.ctx.webhook.post(content = f"ℹ️ | {client_ip} has ben ratelimited")
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
						if (jsonValue[user] == 50): app.ctx.webhook.post(content = f"⚠️ | Warning, {user} done 50 request in less than a minute") 
						if (jsonValue[user] == 100):
							logger.warning(f"{user} e bannato e sta tentando di accedere ({client_ip})")
							app.ctx.webhook.post(content = f"ℹ️ | Just for information, I banned {user} because it did 100 requests in less than a minute")
						if (jsonValue[user] >= 100):
							await app.ctx.db.users.find_one_and_update({ "api_token": request.form.get("token") }, { "$set": { "is_banned": True }})
							logger.warning(f"{user} e bannato e sta tentando di accedere ({client_ip})")
							return json({ "STOP": "okay, but now SOTP! then i obbligated to ban you, you can try to contact fasmga staff to get unban" }, 401)
						return json({ "ddos": "Are you trying to DDoS our API? Asking for a friend :)" }, 429)
					if (jsonValue[user] == 20): app.ctx.webhook.post(content = f"ℹ️ | {user} has ben ratelimited")
					return json({ "ratelimit": "You did >20 requests to the API in this minute. Wait a minute and try again." }, 429)
		return decorated_function
	return decorator

def ratelimitCheck():
	def decorator(f):
		@wraps(f)
		async def decorated_function(request: Request, *args, **kwargs):
			if not request.headers.get("Authorization"): return json({ "bad_request": "You must do a request with Authorization header!" }, 400)
			userData = await app.ctx.db.users.find_one({ "api_token": request.headers.get("Authorization") })
			if not userData: return json({ "bad_request": "Token you provided is invalid" }, 400)

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
				if jsonValue['anonymous'][request.ip] < 20:
					jsonValue['anonymous'][request.ip] += 1
					jsonw = open("sources/ratelimit.json", "w")
					jsonModule.dump(jsonValue, jsonw, indent = 2, sort_keys = True)
					jsonw.close()
					return await f(request, *args, **kwargs)
				else:
					jsonValue['anonymous'][request.ip] += 1
					jsonw = open("sources/ratelimit.json", "w")
					jsonModule.dump(jsonValue, jsonw, indent = 2, sort_keys = True)
					jsonw.close()
					if (jsonValue['anonymous'][request.ip] >= 50):
						if (jsonValue['anonymous'][request.ip] == 50): app.ctx.webhook.post(content = f"⚠️ | Warning, {request.ip} done 50 request in less than a minute") 
						if (jsonValue['anonymous'][request.ip] == 100):
							logger.warning(f"{request.ip} e bannato e sta tentando di accedere")
							app.ctx.webhook.post(content = f"ℹ️ | Just for information, I can't ban {request.ip} but he / she did 100 requests in less than a minute")
						if (jsonValue['anonymous'][request.ip] >= 100): 
							return json({ "SOTP": "okay, but now STOP!" }, 401)
						return json({ "ddos": "Are you trying to DDoS our API? Asking for a friend :)" }, 429)
					if (jsonValue['anonymous'][request.ip] == 20): app.ctx.webhook.post(content = f"ℹ️ | {request.ip} has ben ratelimited")
					return json({ "ratelimit": "You did >20 requests to the API in this minute. Wait a minute and try again." }, 429)

			else:

				if not user in jsonValue: jsonValue[user] = 0
				if jsonValue[user] < 20:
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
						if (jsonValue[user] == 50): app.ctx.webhook.post(content = f"⚠️ | Warning, {user} done 50 request in less than a minute") 
						if (jsonValue[user] == 100):
							logger.warning(f"{user} e bannato e sta tentando di accedere ({request.ip})")
							app.ctx.webhook.post(content = f"ℹ️ | Just for information, I banned {user} because it did 100 requests in less than a minute")
						if (jsonValue[user] >= 100):
							await app.ctx.db.users.find_one_and_update({ "api_token": request.headers.get("Authorization") }, { "$set": { "is_banned": True }})
							logger.warning(f"{user} e bannato e sta tentando di accedere ({request.ip})")
							return json({ "STOP": "okay, but now SOTP! then i obbligated to ban you, you can try to contact fasmga staff to get unban" }, 401)
						return json({ "ddos": "Are you trying to DDoS our API? Asking for a friend :)" }, 429)
					if (jsonValue[user] == 20): app.ctx.webhook.post(content = f"ℹ️ | {user} has ben ratelimited")
					return json({ "ratelimit": "You did >20 requests to the API in this minute. Wait a minute and try again." }, 429)

		return decorated_function

	return decorator

def internalRouteLegacy(): #? This will be deleted when testing api are stabile
	def decorator(f):
		@wraps(f)
		async def decorated_function(request: Request, *args, **kwargs):
			client_ip = request.forwarded.get('for')
			userData = await app.ctx.db.users.find_one({ "api_token": request.form.get("token") })
			if not userData:
				return json({ "bad_request": "Token you provided is invalid" }, 400)
			user = userData['username']
			if userData["is_banned"]:
				logger.warning(f"{user} e bannato e sta tentando di accedere ({client_ip})")
				return json({ "banned": "You are banned from api, you can try to contact fasmga staff to get unban" }, 401)
			if not client_ip == "127.0.0.1":
				await app.ctx.db.users.find_one_and_update({ "api_token": request.form.get("token") }, { "$set": { "is_banned": True }})
				app.add_task(tempBanRemove(request.form.get("token")))
				app.ctx.webhook.post(content = f"⚠️ | Warning, {user} is trying to access to internal APIs", username = "Fasm.ga Internal")
				logger.warning(f"{userData['username']} e stato temp bannato ({client_ip})")
				return json({ "unauthorized": "You can't access to internal APIs, use normal APIs instead, for security reason you are temp-banned for 10 minutes" }, 401)
			response = await f(request, *args, **kwargs)
			return response
		return decorated_function
	return decorator

def argsCheck(mode = "required", values: list = [], expected_type: list = []):
	def decorator(f):
		@wraps(f)
		async def decorated_function(request: Request, *args, **kwargs):
			if values == []:
				try:
					raise Exception("You want to check a list of 0 values? \N{neutral face}")
				except Exception:
					traceback.print_exc()
					return json({ "teapot": "Did you want some tea?", "error": "There is an 500 status code in the server, but i want to ask you if you want some tea" }, 418)
			requestData = request.json
			if not requestData:
				requestData = {}
			types = not expected_type == [] and len(values) == len(expected_type)

			missing = []

			for value in values:
				if not value in requestData:
					_list = [value]
					if types:
						_list.append(expected_type[values.index(value)])
					missing.append(_list)

			x = 's are' if len(missing) > 1 else ' is'
			response = { "error": f"{f'Missing value{x}' if mode == 'required' else f'Missing at least one of the value:'} " }

			for missingValue in missing:
				response["error"] += f"{missingValue[0]}{', ' if not len(missing) - 1 == missing.index(missingValue) else '.'}"

			if types:
				response["types"] = ""
				for missingValue in missing:
					if missingValue[1].__class__.__name__ == "str":
						response["types"] += f"{missingValue[0]} is a {missingValue[1]}{'; ' if not missing[-1] == missing[missing.index(missingValue)] else '.'}"
					else:
						response["types"] += f"{missingValue[0]} is a {missingValue[1].__name__}{'; ' if not missing[-1] == missing[missing.index(missingValue)] else '.'}"

			if len(missing) > 0 and mode == "required":
				return json(response, 400)
			elif len(missing) == len(values) and mode == "optional":
				return json(response, 400)

			return await f(request, *args, **kwargs)

		return decorated_function
	return decorator
