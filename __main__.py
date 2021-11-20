from sanic import Sanic
from sanic.log import logger
from jinja2 import FileSystemLoader, Environment
from motor import motor_asyncio as motor
from discordwebhook import Discord
import asyncio
import dotenv
import glob
import importlib
import json
import os
import sys
import ssl

dotenv.load_dotenv()

#region Register sanic app

sllContex = ssl.create_default_context(purpose = ssl.Purpose.CLIENT_AUTH)
sllContex.load_cert_chain("/ssl/certificate.pem", keyfile = "/ssl/private-key.pem")

app = Sanic("api.fasmga")
app.ctx.argv = sys.argv[:]
app.ctx.webhook = Discord(url = os.getenv("DiscordWebHook"))
app.ctx.jinja = Environment(loader = FileSystemLoader(searchpath = "./html"))
app.config.update({
	"debug": os.environ.get("debug") == "true",
	"verbose": os.environ.get("verbose") == "true",
	"FORWARDED_SECRET": os.environ.get("FORWARDED_SECRET"),
})

#endregion

if not os.path.exists('sources/ratelimit.json'):
	ratelimitjson = open('sources/ratelimit.json', 'w')
	ratelimitjson.write("{}")
	ratelimitjson.close()

#region plug-in handling

if app.config.get("debug"): logger.warning("You are running into developer mode, make sure you don't are using this for run production!")
logger.info(f"Discovering plug-in for {app.name}!")
logger.info("-------------------------------------------------------")
for filename in [os.path.basename(f)[:-3] for f in glob.glob(os.path.join(os.path.dirname("./sources/plugin/"), "*.py")) if os.path.isfile(f)]:
	logger.info(f"Loading {filename}...")
	try:
		importlib.import_module(f"sources.plugin.{filename}")
	except Exception as error:
		logger.error(f"Error loading {filename}")
		if app.config.get("debug"): logger.error(error)
		else: logger.info("To see error set 'developer' env value to 'true'")
	else: 
		logger.info(f"{filename} loaded successfully!")
	logger.info("-------------------------------------------------------")
logger.info("Done!")

#endregion

#region Motor Setup

@app.listener("before_server_start")
def setupMotor(app, loop):
	logger.info("Opening motor connection to database")
	try:
		app.ctx.database = motor.AsyncIOMotorClient(os.getenv("MongoDB"), io_loop = loop, tls = False)
		app.ctx.db = app.ctx.database.fasmga
	except Exception as err:
		logger.error(f"Cannot connect to database, {err}")

@app.listener("before_server_stop")
def closingMotor(app, loop):
	logger.info("Closing motor connection")
	app.ctx.database.close()

#endregion

#region Ratelimit handling

async def ratelimitReset():
	while True:
		try:
			jsonFile = open("sources/ratelimit.json", 'r')
			jsonValues = json.load(jsonFile)
			jsonFile.close()
			for jsonValue in jsonValues:
				if jsonValue == 'anonymous':
					for ip in jsonValues[jsonValue]:
						jsonValues[jsonValue][ip] = 0
				else:
					jsonValues[jsonValue] = 0
			jsonFile = open("sources/ratelimit.json", 'w')
			json.dump(jsonValues, jsonFile, indent = 2, sort_keys = True)
			jsonFile.close()
			await asyncio.sleep(60)
		catch Exception as er:
			print("ERROR: FAILED TO PARSE JSON! RESTARTING...")
			exit(1)
			

@app.listener("before_server_start")
def creating_tasks(app, loop):
	global ratelimit_reset
	ratelimit_reset = loop.create_task(ratelimitReset())

@app.listener("before_server_stop")
def closing_tasks(app, loop):
	ratelimit_reset.cancel()
	if '--skip-privacy' in app.ctx.argv:
		logger.warning('Skipping delete of sources/ratelimit.json')
	else:
		logger.info('Deleting sources/ratelimit.json')
		os.remove('sources/ratelimit.json')


#endregion

__spec__ = ""

if __name__ == "__main__":
	app.run(host = "0.0.0.0", port = 2002, ssl = sllContex, debug = app.config.verbose, auto_reload = app.config.debug)