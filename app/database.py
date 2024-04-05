# Ravi Patel

import datetime
import logging
import os
import motor.motor_asyncio


def get_db_client() -> motor.motor_asyncio.AsyncIOMotorClient:
    """
    Get the database client.

    Returns:
        motor.motor_asyncio.AsyncIOMotorClient: The database client.
    """
    db_user = os.environ.get("MONGODB_USERNAME")
    db_password = os.environ.get("MONGODB_PASSWORD")
    client = motor.motor_asyncio.AsyncIOMotorClient(
        f"mongodb://{db_user}:{db_password}@mongodb:27017"
    )
    return client


async def initialize_database() -> None:
    """
    Initializes the database by creating collections and inserting initial data.

    This function connects to the database, checks if the 'demo' database exists,
    creates collections 'links' and 'host_data' if they don't exist, creates indexes
    on the collections, and inserts initial data into the 'links' collection.

    Returns:
        None
    """
    client = get_db_client()
    available_databases = await client.list_database_names()
    if "demo" not in available_databases:
        db = client["demo"]

        await db.create_collection("links")
        db["links"].create_index("type", unique=True)
        logging.info("Created links collection with index.")

        await db.create_collection("host_data")
        db["host_data"].create_index(["host_name","internal_ip"], unique=True)
        logging.info("Created host_data collection with index.")
        await db["links"].insert_one(
            {
                "link": "https://[update_me]/api/crowdstrike/hosts/get",
                "type": "crowdstrike",
                "last_checked": datetime.datetime(1970, 1, 1, 0, 0, 0, 0),
            }
        )
        await db["links"].insert_one(
            {
                "type": "qualys",
                "link": "https://[update_me]/api/qualys/hosts/get",
                "last_checked": datetime.datetime(1970, 1, 1, 0, 0, 0, 0),
            }
        )
        logging.info("Database initialized")
