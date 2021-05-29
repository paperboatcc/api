from sanic import Sanic
from sanic.response import empty
import os, glob, importlib, time

app = Sanic("api.fasmga.org")

@app.route("/")
async def main(request): return empty()

if (os.environ.get("developer") == "True"): print("Warning! You are running into a developer mode, make sure you don't are using this for run production!")
print(f"Discovering plug-in for {app.name}!")
print("-------------------------------------------------------")
for filename in [os.path.basename(f)[:-3] for f in glob.glob(os.path.join(os.path.dirname("./Sources/Python/"), "*.py")) if os.path.isfile(f)]:
	module = importlib.import_module(f"Sources.Python.{filename}")
	print(f"Loading plug-in for the {filename}...")
	try:
		module.plug_in()
	except Exception as error:
		print(f"Loading {filename} i encontered an error")
		print(error)
	else: 
		print(f"I successfully loaded {filename}!")
	print("-------------------------------------------------------")
print("Done!")

if (os.environ.get("developer") == "True"): 
	app.run(debug=True, auto_reload=False)
else: 
	app.run()