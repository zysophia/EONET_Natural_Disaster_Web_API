"""
Earth Observatory Natural Event Tracker.
"""
import time
import sched
import pandas as pd
import json
import logging
import requests
import numpy as np
from io import StringIO

import utils
from database import upsert_dis


DIS_SOURCE = "https://eonet.sci.gsfc.nasa.gov/api/v2.1/events"
MAX_DOWNLOAD_ATTEMPT = 5
DOWNLOAD_PERIOD = 30        # second
logger = logging.Logger(__name__)
utils.setup_logger(logger, 'data.log')

def download_disaster(url=DIS_SOURCE, retries=MAX_DOWNLOAD_ATTEMPT, limit = 10, days = 2, status = "open", timeout = 1.0):
    """Returns disaster information text from `DIS_SOURCE` that includes disaster information
    Returns None if network failed
    """
    js = None
    for _ in range(retries):
        try:
            req = requests.get(f"{url}?limit={limit}&days={days}&status={status}", timeout=timeout)
            req.raise_for_status()
            text = req.text
            js = json.loads(text)
        except requests.exceptions.HTTPError as e:
            logger.warning("Retry on HTTP Error: {}".format(e))
    if js is None:
        logger.error('download_dis too many FAILED attempts')
    return js


def filter_dis(js):
    """Converts `json` to `DataFrame`
    """
    data = []
    filter_tits = ["Wildfires", "Severe_Storms", "Sea_and_Lake_Ice"]
    for x in js["events"]:
        tit = x["categories"][0]["title"].replace(" ","_")
        if tit not in filter_tits:
            continue
        id = x["categories"][0]["id"]
        subtit, subid, url = x['title'], x['id'], x['sources'][0]['url']
        g = x["geometries"]
        for gg in g:
            dt, geo = pd.to_datetime(gg["date"]), gg['coordinates']
            singled = [id, tit, subtit, subid, dt, geo[0], geo[1], url]
            data.append(singled)
    data = np.array(data)
    df = pd.DataFrame(data, columns = ["id", "title", "subid", "subtitle", "datetime", "geo1", "geo2", "url"])
    return df


def update_once():
    t = download_disaster(limit = 100, days = 5)
    df = filter_dis(t)
    upsert_dis(df)

def update_history():
    try:
        t = download_disaster(limit = 1000000, days = 1000, status = "closed", timeout = 15.0)
        df = filter_dis(t)
        upsert_dis(df)
    except Exception as e:
            logger.warning("history disaster worker ignores exception and continues: {}".format(e))



def main_loop(timeout=DOWNLOAD_PERIOD):
    scheduler = sched.scheduler(time.time, time.sleep)

    def _worker():
        try:
            update_once()
        except Exception as e:
            logger.warning("main loop worker ignores exception and continues: {}".format(e))
        scheduler.enter(timeout, 1, _worker)    # schedule the next event

    scheduler.enter(0, 1, _worker)              # start the first event
    scheduler.run(blocking=True)



if __name__ == '__main__':
    update_history()
    main_loop()