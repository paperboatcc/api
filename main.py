from sanic import Sanic
from log_symbols import LogSymbols
import os, glob, importlib

app = Sanic("api.fasmga")

if (os.environ.get("developer") == "True"): print(f"{LogSymbols.WARNING.value} | You are running into developer mode, make sure you don't are using this for run production!")
print(f"{LogSymbols.INFO.value} | Discovering plug-in for {app.name}!")
print("-------------------------------------------------------")
for filename in [os.path.basename(f)[:-3] for f in glob.glob(os.path.join(os.path.dirname("./sources/plugin/"), "*.py")) if os.path.isfile(f)]:
	module = importlib.import_module(f"sources.plugin.{filename}")
	print(f"{LogSymbols.INFO.value} | Loading {filename}...")
	try:
		module.plug_in()
	except Exception as error:
		print(f"{LogSymbols.ERROR.value} | Error loading {filename}")
		print(error)
	else: 
		print(f"{LogSymbols.SUCCESS.value} | {filename} loaded successfully!")
	print("-------------------------------------------------------")
print("Done!")

if (os.environ.get("developer") == "True"): 
	app.run(debug = True, auto_reload = False)
else: 
	app.run()