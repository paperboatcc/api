import aiohttp
import asyncio

async def main():
	while True:
		async with aiohttp.ClientSession() as session:
			async with session.post("http://localhost:8000/ratelimit", data= {"token": "test", "testtt": "value2"} ) as response:
				print(f"Status: {response.status}")
				print(f"Content-type: {response.headers['content-type']}\n")
				html = await response.text()
				print(f"Result: {html}\n\n")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())