from functools import wraps
from sanic.response import json
from discordwebhook import Discord
import json as jsonModule 

def ratelimitCheck():
	def decorator(f):
		@wraps(f)
		async def decorated_function(request, *args, **kwargs):
			jsonValue = jsonModule.load(open("sources/ratelimit.json", "r"))

			# todo: remove "test" and put userName
			if jsonValue["test"] <= 20:
				jsonValue["test"] += 1
				jsonModule.dump(jsonValue, open("sources/ratelimit.json", "w"), indent = 2)
				response = await f(request, *args, **kwargs)
				return response
			else:
				jsonValue["test"] += 1
				jsonModule.dump(jsonValue, open("sources/ratelimit.json", "w"), indent = 2)
				if (jsonValue["test"] >= 50):
					if (jsonValue["test"] == 50):
						webhook = Discord(url = "https://discord.com/api/webhooks/849348454076907580/ZIMILeKyh6Aal2ooUGvPv188IonNNHh7eo7yC-N5cI1Q_24FhuPmNSCRtu52XGGEf-jg")
						webhook.post(content = "WARNING! test (yep, it's a test XD) maybe are trying to DDoS") 
					if (jsonValue["test"] >= 100):
						# todo: edit token to "banned"
						return json({ "SOTP": "okey, but now STOP! then i obbligated to ban you, you can try to contact fasmga staff to get unban" })
					return json({ "ddos": "Are you trying to DDoS our API? Asking for a friend :)" })
				return json({ "ratelimit": "You did >20 requests to the API in this minute. Wait a minute and try again." }, 403)
		return decorated_function
	return decorator