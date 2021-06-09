import asyncio
import random
import string
import json

def generateUrlID(idtype):
	if idtype == "abcdefgh":
		urlid = str().join(random.choice(string.ascii_lowercase) for i in range(8))
		return urlid
	elif idtype == "abc12345":
		urlid = str().join(random.choice(string.ascii_lowercase) for i in range(3)) + str(random.randint(10000, 99999))
		return urlid
	elif idtype == "aBCde":
		urlid = str().join(random.choice(string.ascii_letters) for i in range(5))
		return urlid

async def tempBanRemove(app, token):
	await asyncio.sleep(600)
	await app.ctx.db.users.find_one_and_update({ "api_token": token }, { "$set": { "is_banned": False }})