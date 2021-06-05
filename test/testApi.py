import aiohttp
import asyncio

async def main():
	#while True:
		async with aiohttp.ClientSession() as session:
			async with session.post("http://localhost:8000/internal/create", data= {"token": "test", "password": "", "url": "https://noice.link", "idtype": "abcdefgh", "nsfw": "y"} ) as response:
				print(f"Status: {response.status}")
				print(f"Content-type: {response.headers['content-type']}\n")
				html = await response.text()
				print(f"Result: {html}\n\n")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())