import aiohttp
import asyncio
import sys
import json

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
	try: doWhile = sys.argv[1] == "--loop" or sys.argv[1] == "-l"
	except: doWhile = False

	if doWhile:
		async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
			while True:
				async with session.post(url = url, data = data) as response:
					print(f"Status: {response.status}")
					print(f"Content-type: {response.headers['content-type']}\n")
					html = await response.text()
					print(f"Result: {html}\n\n")
	else:
		async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
			async with session.post(url = url, data = data) as response:
				print(f"Status: {response.status}")
				print(f"Content-type: {response.headers['content-type']}\n")
				html = await response.text()
				print(f"Result: {html}\n\n")
				print(json.loads(html))
				print(json.loads(html)["success"])

loop = asyncio.get_event_loop()
loop.run_until_complete(main())