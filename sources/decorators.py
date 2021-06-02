from functools import wraps
from sanic import Sanic
from sanic.response import json
from discordwebhook import Discord
import json as jsonModule 

app = Sanic.get_app("api.fasmga")
webhook = Discord(url = "https://discord.com/api/webhooks/849348454076907580/ZIMILeKyh6Aal2ooUGvPv188IonNNHh7eo7yC-N5cI1Q_24FhuPmNSCRtu52XGGEf-jg")

def ratelimitCheck():
	def decorator(f):
		@wraps(f)
		async def decorated_function(request, *args, **kwargs):
			if not request.form.get("token"): 
				return json({ "bad_request": "You must do a request with token value!" }, 400)
			userData = await app.ctx.db.users.find_one({ "login_token": request.form.get("token") })
			user = userData["username"]# seha massi z
			if not userData:
				return json({ "bad_request": "Token you provvided is invalid" }, 400)
			if (userData["is_banned"] == True): 
				return json({ "banned": "You are banned from api, you can try to contact fasmga staff to get unbam" }, 401)

			jsonValue = jsonModule.load(open("sources/ratelimit.json", "r"))
			if not user in jsonValue: jsonValue[user] = 0
			if jsonValue[user] <= 20:
				jsonValue[user] += 1
				jsonModule.dump(jsonValue, open("sources/ratelimit.json", "w"), indent = 2)
				response = await f(request, *args, **kwargs)
				return response
			else:
				jsonValue[user] += 1
				jsonModule.dump(jsonValue, open("sources/ratelimit.json", "w"), indent = 2)
				if (jsonValue[user] >= 50):
					if (jsonValue[user] == 50):
						webhook.post(content = f"⚠️ | Warning, {user} done 50 request in less than a minute") 
					if (jsonValue[user] == 100):
						await app.ctx.db.users.find_one_and_update({ "login_token": request.form.get("token") }, { "$set": { "is_banned": True }})
						webhook.post(content = f"ℹ️ | Just for information, I banned {user} because it did 100 requests in less than a minute")
						return json({ "SOTP": "okey, but now STOP! then i obbligated to ban you, you can try to contact fasmga staff to get unban" }, 401)
					return json({ "ddos": "Are you trying to DDoS our API? Asking for a friend :)" }, 429)
				return json({ "ratelimit": "You did >20 requests to the API in this minute. Wait a minute and try again." }, 429)
		return decorated_function
	return decorator