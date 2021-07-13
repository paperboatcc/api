from sanic import Sanic
from sanic.response import html
import asyncio
import random
import string

app = Sanic.get_app("api.fasmga")

def render_template(file, **args):
	template = app.ctx.jinja.get_template(str(file))
	htmlPage = template.render(args)
	return html(htmlPage)

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

async def tempBanRemove(token):
	await asyncio.sleep(600)
	await app.ctx.db.users.find_one_and_update({ "api_token": token }, { "$set": { "is_banned": False }})