"""
Earth Observatory Natural Event Tracker.
"""
import time
import sched
import pandas as pd
from datetime import datetime
import json
import logging
import requests
import numpy as np
from io import StringIO

import utils
from database import upsert_dis, upsert_wea


DIS_SOURCE = "https://eonet.sci.gsfc.nasa.gov/api/v2.1/events"
W_SOURCE = "https://api.darksky.net/forecast/b4c50d35d2b602d506c708a505757c25/"
MAX_DOWNLOAD_ATTEMPT = 3
DOWNLOAD_PERIOD = 120        # second
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
    return js, status


def filter_dis(js, status):
    """Converts `json` to `DataFrame`
    """
    data = []
    filter_tits = ["Wildfires", "Severe_Storms", "Sea_and_Lake_Ice"]
    for x in js["events"]:
        tit = x["categories"][0]["title"].replace(" ","_")
        if tit not in filter_tits:
            continue
        try:
            id = x["categories"][0]["id"]
            subtit, subid, url = x['title'], x['id'], x['sources'][0]['url'] if x["sources"] else None
            g = x["geometries"]
            for gg in g:
                dt, geo = pd.to_datetime(gg["date"]), gg['coordinates']
                singled = [id, tit, subtit, subid, dt, geo[0], geo[1], status, url]
                data.append(singled)
        except:
            continue
    data = np.array(data)
    df = pd.DataFrame(data, columns = ["id", "title", "subid", "subtitle", "datetime", "geo1", "geo2", "status", "url"])
    return df


def download_weather(url=W_SOURCE, retries=MAX_DOWNLOAD_ATTEMPT, lat=34, lon=-118, timeout=1.0):
    """Returns weather forecast information dataframe from `W_SOURCE` that includes weather information
    Returns None if network failed
    """
    df = None
    for _ in range(retries):
        try:
            req = requests.get(f"{url}{lat},{lon}", timeout=timeout)
            req.raise_for_status()
            text = req.text
            js = json.loads(text)
            data = js['daily']['data']

            df = pd.DataFrame()
            for forecast in data:
                dt = datetime.fromtimestamp(forecast['time'])
                if dt < datetime.now():
                    continue
                fore_dict = {k:v for k,v in forecast.items() if ('Time' not in k and 'icon' not in k and 'summary' not in k and 'precip' not in k and 'time' not in k)}
                fore_dict['long'], fore_dict['lat'],  fore_dict['date']= lon, lat, dt.date()
                df = df.append(fore_dict, ignore_index=True)
        except requests.exceptions.HTTPError as e:
            logger.warning("Retry on HTTP Error: {}".format(e))
    if js is None:
        logger.error('download_wea too many FAILED attempts')
    return df


def update_once_d():
    t, s = download_disaster(limit = 1000, days = 100)
    df = filter_dis(t, s)
    upsert_dis(df)


def update_once_w():
    df1 = download_weather(lat=34, lon=-118)
    upsert_wea(df1)
    df2 = download_weather(lat=34, lon=-118)
    upsert_wea(df2)


def update_history():
    try:
        t, s = download_disaster(limit = 1000, days = 1000, status = "closed", timeout = 60.0)
        print("History disaster data requested..........")
        df = filter_dis(t, s)
        print("History disaster data filtered..........")
        upsert_dis(df)
        print("History disaster data updated..........")
    except Exception as e:
        logger.warning("history disaster worker ignores exception and continues: {}".format(e))



def main_loop(timeout=DOWNLOAD_PERIOD):
    scheduler = sched.scheduler(time.time, time.sleep)

    def _worker():
        try:
            update_once_d()
            update_once_w()
        except Exception as e:
            logger.warning("main loop worker ignores exception and continues: {}".format(e))
        scheduler.enter(timeout, 1, _worker)    # schedule the next event

    scheduler.enter(0, 1, _worker)              # start the first event
    scheduler.run(blocking=True)



if __name__ == '__main__':
    #update_history()
    main_loop()