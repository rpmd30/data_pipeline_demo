# Ravi Patel
# data pipeline demo
# Objective:
#   Data Fetching - You will implement API clients to fetch raw hosts from a third party vendor (Qualys / Crowdstrike).
#   Data Normalization - You will implement logic to normalize the hosts (which are in different formats) into a unified format (that you'll define)
#   Data Deduping - You will implement logic to determine and merge duplicate hosts

import asyncio
import argparse
import os
import logging
import sys
from database import initialize_database
from fetcher import Fetcher
from producer import Producer
from serializer import Serializer

logging.basicConfig(stream=sys.stdout, encoding="utf-8", level=logging.DEBUG)

DEBUG = os.environ.get("DEMO_DEBUG", False)


async def main(num_producers: int, num_fetchers: int, num_serializers: int):
    """Main function that creates producer, fetcher, and serializer workers.

    Args:
        num_producers (int): Number of producer workers to create.
        num_fetchers (int): Number of fetcher workers to create.
        num_serializers (int): Number of serializer workers to create.
    """
    logging.info(f"Starting with {num_producers} producers")
    logging.info(f"Starting with {num_fetchers} fetchers")
    logging.info(f"Starting with {num_serializers} serializers")
    await initialize_database()

    fetcher_queue = asyncio.Queue()
    serializer_queue = asyncio.Queue()

    producers = [Producer(fetcher_queue) for _ in range(num_producers)]
    producer_tasks = [asyncio.create_task(producer.run()) for producer in producers]

    fetchers = [
        Fetcher(fetcher_queue=fetcher_queue, serializer_queue=serializer_queue)
        for _ in range(num_fetchers)
    ]
    fetcher_tasks = [asyncio.create_task(fetcher.run()) for fetcher in fetchers]

    serializers = [
        Serializer(serializer_queue=serializer_queue) for _ in range(num_serializers)
    ]
    serializer_tasks = [
        asyncio.create_task(serializer.run()) for serializer in serializers
    ]

    await asyncio.gather(*producer_tasks, *fetcher_tasks, *serializer_tasks)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Fetcher", description="Fetch apis, normalize data, and save to database."
    )
    parser.add_argument("-p", "--num_producers", default=1, type=int)
    parser.add_argument("-f", "--num_fetchers", default=1, type=int)
    parser.add_argument("-s", "--num_serializers", default=1, type=int)
    args = parser.parse_args()

    producers = args.num_producers
    fetchers = args.num_fetchers
    serializers = args.num_serializers
    asyncio.run(
        main(
            num_producers=producers, num_fetchers=fetchers, num_serializers=serializers
        ),
        debug=DEBUG,
    )
