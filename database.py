import logging
import pymongo
import pandas as pd
import expiringdict
import utils

client = pymongo.MongoClient()
logger = logging.Logger(__name__)
utils.setup_logger(logger, 'db.log')
RESULT_CACHE_EXPIRATION = 20             # seconds


def upsert_dis(df):
    """
    Update MongoDB database `disaster` and collection `disasters` with the given `DataFrame`.
    """
    db = client.get_database("disaster")
    collection = db.get_collection("disasters")
    update_count = 0
    for record in df.to_dict('records'):
        result = collection.replace_one(
            filter=record,                              # locate the document if exists
            replacement=record,                         # latest document
            upsert=True)                                # update if exists, insert if not
        if result.matched_count > 0:
            update_count += 1
    logger.info("rows={}, update={}, ".format(df.shape[0], update_count) +
                "insert={}".format(df.shape[0]-update_count))

def upsert_wea(df):
    """
    Update MongoDB database `disaster` and collection `weather` with the given `DataFrame`.
    """
    db = client.get_database("disaster")
    collection = db.get_collection("weather")
    update_count = 0
    for record in df.to_dict('records'):
        result = collection.replace_one(
            filter={k:v for k,v in record.items() if k in ['long','lat','date']},       # locate the document if exists
            replacement=record,                         # latest document
            upsert=True)                                # update if exists, insert if not
        if result.matched_count > 0:
            update_count += 1
    logger.info("rows={}, update={}, ".format(df.shape[0], update_count) +
                "insert={}".format(df.shape[0]-update_count))


def fetch_all_dis():
    db = client.get_database("disaster")
    collection = db.get_collection("disasters")
    return list(collection.find())


def fetch_all_wea():
    db = client.get_database("disaster")
    collection = db.get_collection("weather")
    return list(collection.find())


_fetch_all_dis_as_df_cache = expiringdict.ExpiringDict(max_len=1,
                                                       max_age_seconds=RESULT_CACHE_EXPIRATION)

_fetch_all_wea_as_df_cache = expiringdict.ExpiringDict(max_len=1,
                                                       max_age_seconds=RESULT_CACHE_EXPIRATION)


def fetch_all_dis_as_df(allow_cached=False):
    """Converts list of dicts returned by `fetch_all_dis` to DataFrame with ID removed
    Actual job is done in `_worker`. When `allow_cached`, attempt to retrieve timed cached from
    `_fetch_all_dis_as_df_cache`; ignore cache and call `_work` if cache expires or `allow_cached`
    is False.
    """
    def _work():
        data = fetch_all_dis()
        if len(data) == 0:
            return None
        df = pd.DataFrame.from_records(data)
        df.drop('_id', axis=1, inplace=True)
        return df

    if allow_cached:
        try:
            return _fetch_all_dis_as_df_cache['cache']
        except KeyError:
            pass
    ret = _work()
    _fetch_all_dis_as_df_cache['cache'] = ret
    return ret


def fetch_all_wea_as_df(allow_cached=False):
    """Converts list of dicts returned by `fetch_all_dis` to DataFrame with ID removed
    Actual job is done in `_worker`. When `allow_cached`, attempt to retrieve timed cached from
    `_fetch_all_dis_as_df_cache`; ignore cache and call `_work` if cache expires or `allow_cached`
    is False.
    """
    def _work():
        data = fetch_all_wea()
        if len(data) == 0:
            return None
        df = pd.DataFrame.from_records(data)
        df.drop('_id', axis=1, inplace=True)
        return df

    if allow_cached:
        try:
            return _fetch_all_wea_as_df_cache['cache']
        except KeyError:
            pass
    ret = _work()
    _fetch_all_wea_as_df_cache['cache'] = ret
    return ret


if __name__ == '__main__':
    print(fetch_all_dis_as_df())
    print(fetch_all_wea_as_df())
