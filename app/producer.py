# Ravi Patel

import asyncio
from datetime import datetime, timedelta
import logging

from database import get_db_client

class Producer:
    """
    Producer
    Populates fetcher queue with links and type
    """

    def __init__(self, fetcher_queue: asyncio.Queue):
        self.stop: bool = False
        self.fetcher_queue: asyncio.Queue = fetcher_queue

    async def run(self):
            """
            Runs the producer, continuously fetching links from the database and adding them to the fetcher queue.
            
            Returns: None
            """
            client = get_db_client()
            db = client["demo"]
            while not self.stop:
                # Query for links from the last hour
                async with await client.start_session() as s:
                    async with s.start_transaction():
                        # Get current time
                        now = datetime.utcnow()
                        # Get time one hour ago
                        one_hour_ago = now - timedelta(hours=1)
                        links = db['links'].find({"last_checked": {"$lte": one_hour_ago}})
                        async for link in links:
                            for skip in range(1, 10):
                                # we'll pull the maximum limit of 2
                                await self.fetcher_queue.put(
                                    {"type": link["type"], "link": link["link"], "skip": skip}
                                )
                                logging.info(f"added {link['type']}")
                            # Update last_checked
                            await db['links'].update_one(
                                {"_id": link["_id"]},
                                {"$set": {"last_checked": now}}
                            )
                # Update hourly
                await asyncio.sleep(3600)
