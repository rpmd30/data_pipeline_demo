# Ravi Patel

import asyncio
import aiohttp
import os
import logging

AUTH_TOKEN = os.environ.get("AUTH_KEY", None)

class Fetcher:
    """
    Fetcher
    Retrieves item from fetcher_queue, requests data from link, and pushes results to serializer_queue
    """

    def __init__(self, fetcher_queue: asyncio.Queue, serializer_queue: asyncio.Queue):
        self.stop: bool = False
        self.fetcher_queue: asyncio.Queue = fetcher_queue
        self.serializer_queue: asyncio.Queue = serializer_queue


    async def run(self):
            """
            Executes the fetcher's main loop, continuously fetching data from the fetcher_queue,
            making HTTP POST requests, and putting the response body into the serializer_queue.

            Returns: None
            """
            while not self.stop:
                payload = await self.fetcher_queue.get()
                params = {"limit": 2, "skip": payload["skip"]}
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        payload["link"],
                        params=params,
                        headers={"token": AUTH_TOKEN},
                    ) as response:
                        if response.status == 200:
                            body = await response.json()
                            await self.serializer_queue.put(
                                {"type": payload["type"], "body": body}
                            )
                logging.info("Fetcher waiting for more work")
