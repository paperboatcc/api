# Main file for the "test suite" for the api
#? si mi sono stufato di fare 85 richieste a mano

import dotenv
import asyncio
import create_api
import list_api
import delete_api

dotenv.load_dotenv()

async def main():

	UrlList = await create_api.module()

	print(f"Il test della creazione degli url ha restituito: {UrlList}")
	print("Waiting 60 to don't get ratelimited!")
	await asyncio.sleep(60) # per non essere ratelimitato

	FetchedUrlList = await list_api.module()

	print(f"Il test del fetch di tutti gli url del token ha restituito: {FetchedUrlList}")
	await asyncio.sleep(5) # per vedere qualcosa

	Deleted = await delete_api.module(UrlList)

	print(f"Il test della cancellazione degli url ha restituito: {Deleted}")
	print("Waiting 60 to don't get ratelimited!")
	await asyncio.sleep(60) # per non essere ratelimitato

	FetchedUrlList2 = await list_api.module()

	print(f"Il test del fetch di tutti gli url del token ha restituito (dopo la cancellazione di quelli creati per il test): {FetchedUrlList2}")

	#TODO: fare l'edit


if __name__ == "__main__":
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())
