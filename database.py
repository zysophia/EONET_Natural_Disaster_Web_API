import logging
import pymongo
import pandas as pd
import expiringdict

import utils

client = pymongo.MongoClient()
logger = logging.Logger(__name__)
utils.setup_logger(logger, 'db.log')
RESULT_CACHE_EXPIRATION = 10             # seconds


def upsert_dis(df):
    """
    Update MongoDB database `disaster` and collection `disasters` with the given `DataFrame`.
    """
    db = client.get_database("disaster")
    collection = db.get_collection("disasters")
    update_count = 0
    for record in df.to_dict('records'):
        print(record)
        result = collection.replace_one(
            filter=record,    # locate the document if exists
            replacement=record,                         # latest document
            upsert=True)                                # update if exists, insert if not
        if result.matched_count > 0:
            update_count += 1
    logger.info("rows={}, update={}, ".format(df.shape[0], update_count) +
                "insert={}".format(df.shape[0]-update_count))

