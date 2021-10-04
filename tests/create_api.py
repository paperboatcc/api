import aiohttp
import asyncio
import os
import dotenv
import sys

dotenv.load_dotenv()

url = "https://fasmvps.ga:2002/create"
data = {
	"token": os.environ.get("TOKEN"),
	"id": "xaydzajb",
	"password": "",
	"url": "https://example.com", 
	"idtype": "abcdefgh", 
	"nsfw": False,
}

# Se il file e importato da un altro file
async def module() -> list:
	UseSSL = "--useSLL" in sys.argv or "-ssl" in sys.argv 
	results = []

	del data["id"] # gli id presettati non possono essere testati, perche dovrei cancellarli subito dopo che li uso
	del data["password"]
	data["nsfw"] = True
	data["idtype"] = "abcdefgh"
	results.append(await do_request(url, data, UseSSL)) #? nsfw, no password, idtype abcdefgh

	data["idtype"] = "abc12345"
	results.append(await do_request(url, data, UseSSL)) #? nsfw, no password, idtype abc12345

	data["idtype"] = "aBCde"
	results.append(await do_request(url, data, UseSSL)) #? nsfw, no password, idtype aBCde

	data["idtype"] = "abcdefgh"
	data["password"] = "unsecurepassword!"
	results.append(await do_request(url, data, UseSSL)) #? nsfw, password, idtype abcdefgh

	data["idtype"] = "abc12345"
	results.append(await do_request(url, data, UseSSL)) #? nsfw, password, idtype abc12345

	data["idtype"] = "aBCde"
	results.append(await do_request(url, data, UseSSL)) #? nsfw, password, idtype aBCde

	data["nsfw"] = False
	data["idtype"] = "abcdefgh"
	results.append(await do_request(url, data, UseSSL)) #? no nsfw, no password, idtype abcdefgh

	data["idtype"] = "abc12345"
	results.append(await do_request(url, data, UseSSL)) #? no nsfw, no password, idtype abc12345

	data["idtype"] = "aBCde"
	results.append(await do_request(url, data, UseSSL)) #? no nsfw, no password, idtype aBCde

	data["idtype"] = "abcdefgh"
	data["password"] = "unsecurepassword!"
	results.append(await do_request(url, data, UseSSL)) #? no nsfw, password, idtype abcdefgh

	data["idtype"] = "abc12345"
	results.append(await do_request(url, data, UseSSL)) #? no nsfw, password, idtype abc12345

	data["idtype"] = "aBCde"
	results.append(await do_request(url, data, UseSSL)) #? no nsfw, password, idtype aBCde

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