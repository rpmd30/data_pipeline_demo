# Ravi Patel

import asyncio
from dataclasses import asdict
import logging
from typing import Dict
from database import get_db_client
from model import Model

NORMALIZATION_MAP = {"crowdstrike": Model.from_crowdstrike, "qualys": Model.from_qualys}


class Serializer:
    """Serializer
    Serializes payloads and saves them to the database.
    """

    def __init__(self, serializer_queue: asyncio.Queue):
        client = get_db_client()
        self.db = client["demo"]
        self.serializer_queue: asyncio.Queue = serializer_queue
        self.stop: bool = False

    async def run(self):
        """
        Run the serializer process.

        This method continuously retrieves payloads from the serializer queue and processes them.
        If the payload type is known, it normalizes the payload and inserts the resulting models into the database.
        If the payload type is unknown, it logs an error message and continues to the next payload.

        Returns:
            None
        """
        while not self.stop:
            payload = await self.serializer_queue.get()
            payload_type = payload["type"]
            if payload_type not in NORMALIZATION_MAP:
                # We should save the payload and type so we can handle this later.
                logging.error(f"Unknown payload type: {payload_type}")
                continue
            models = NORMALIZATION_MAP[payload_type](payload)
            for model in models:
                model_dict = asdict(model)
                old_host_data = await self.db["host_data"].find_one(
                    {"host_name": model.host_name, "external_ip": model.external_ip}
                )
                if old_host_data:
                    logging.info(
                        f"Old host data:{old_host_data['data_source']}: {str(old_host_data)[:100]}"
                    )
                    logging.info(
                        f"New host data:{model_dict['data_source']}: {str(model_dict)[:100]}"
                    )
                    if (
                        old_host_data["recent_raw_hash"]
                        == model_dict["recent_raw_hash"]
                    ):
                        logging.info("No changes detected, skipping")
                        continue
                    model_dict = merge_models(old_host_data, model_dict)
                    await self.db["host_data"].update_one(
                        {"host_name": model.host_name}, {"$set": model_dict}
                    )
                    continue
                # Inserting one at a time because we don't want to lose all of our data if one insert fails.
                insert_result = await self.db["host_data"].insert_one(model_dict)
                logging.info(f"Inserted {insert_result}")
            logging.info("Serializer waiting for more work")


def merge_models(left: Dict, right: Dict) -> Dict:
    """
    Merge two models by combining their attributes.

    Args:
        left (dict): The left model to merge.
        right (dict): The right model to merge.

    Returns:
        dict: The merged model.

    """
    for key in left:
        if key == "raw_payloads":
            left[key].append(right[key])
        if key in right and right[key]:
            left[key] = right[key]
    return left
