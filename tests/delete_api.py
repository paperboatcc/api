import aiohttp
import asyncio
import os
import dotenv
import sys

dotenv.load_dotenv()

url = "https://fasmvps.ga:2002/delete"
data = {
	"token": os.environ.get("TOKEN"),
	"id": ""
}

# Se il file e importato da un altro file
async def module(ids: list) -> list:
	UseSSL = "--useSLL" in sys.argv or "-ssl" in sys.argv 
	results = []

	for id in ids:
		if "success" in id: data["id"] = id["success"].replace("/", "")
		elif "ID" in id: data["id"] = id["ID"]
		else: data["id"] = "ERROR"

		if data["id"] == "ERROR": raise ValueError("[delete] Un id era 'ERROR', quindi ho bloccato il test per sicurezza")

		results.append(await do_request(url, data, UseSSL))

	return results

# Se il file e runnato direttamente ad python
async def main():
	UseSSL = "--useSLL" in sys.argv or "-ssl" in sys.argv 

	del data["id"]
	del data["login"]

	await do_request(url, data, UseSSL)

async def do_request(url: str, data: dict, UseSSL: bool) -> dict:
	if not (UseSSL or UseSSL or data): raise ValueError("Missing value(s) to do the request!")
	result = {}

	async with aiohttp.ClientSession(connector = aiohttp.TCPConnector(ssl = UseSSL)) as session:
		async with session.post(url = url, data = data) as response:
			result = await response.json()
			print(f"Status: {response.status}")
			print(f"Content-type: {response.headers['content-type']}")
			print(f"Request data: {data}\n")
			print(f"Result: {result}\n\n")

	return result

if __name__ == "__main__": 
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())