import aiohttp
import asyncio
import sys

url = "https://fasmvps.ga:2002/create"
data = {
	"token": "kixIegOjXWmOoWAEbaoBfFDqYRaCKNHBKiWTEHPrhVWJDJECoDkDtgVngPorLgJKA",
	#"id": "xaydzajb",
	"password": "",
	"url": "https://example.com", 
	"idtype": "abcdefgh", 
	"nsfw": False,
	#"login": True
}

async def main():
	doWhile = "--loop" in sys.argv or "-l" in sys.argv
	UseSSL = "--useSLL" in sys.argv or "-ssl" in sys.argv 

	await do_request(doWhile, UseSSL, url, data) #TODO: fare i test per tutti i tipi

async def do_request(doWhile: bool, UseSSL: bool, url: str, data: dict) -> None:
	if not (doWhile or UseSSL or url or data): raise ValueError("Missing value(s) to do the request!")

	async with aiohttp.ClientSession(connector = aiohttp.TCPConnector(ssl = UseSSL)) as session:
		while True:
			async with session.post(url = url, data = data) as response:
				html = await response.text()
				print(f"Status: {response.status}")
				print(f"Content-type: {response.headers['content-type']}")
				print(f"Request data: {data}\n")
				print(f"Result: {html}\n\n")
				if doWhile == False: break 

loop = asyncio.get_event_loop()
loop.run_until_complete(main())