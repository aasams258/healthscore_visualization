'''
This must be run in Python 3.5+ due to asyncio.

This class will perform async HTTP requests, putting the output in
a queue for a writing thread to persist to storage.

We will write the pertinent information only. [TBD may dump it all]
First request is to get:
 * Business ID
 * Yelp formatted name
 * Coordinates (lat/long)
These will be output to a file.

Second to get the business details:
Rating, Category, Reviews, Price, The First Photo (image_url)
'''
#https://pawelmhm.github.io/asyncio/python/aiohttp/2016/04/22/asyncio-aiohttp.html
#https://aiohttp.readthedocs.io/en/stable/client_quickstart.html

# # modified fetch function with semaphore
# https://hackernoon.com/asyncio-for-the-working-python-developer-5c468e6e2e8e
# https://medium.com/@yeraydiazdiaz/asyncio-coroutine-patterns-errors-and-cancellation-3bb422e961ff


# need to rate limit:
# https://quentin.pradet.me/blog/how-do-you-rate-limit-calls-with-aiohttp.html

import random
import asyncio
from aiohttp import ClientSession
import aiohttp
from multiprocessing import Process, Queue
import csv
import time
import argparse

def writer(dest_filename, queue, stop_token):
    with open(dest_filename, 'w') as dest_file:
        while True: 
            line = queue.get()
            if line == stop_token:
                return
            dest_file.write("{}:::{}:::{}\n".format(line[0], line[1], line[2]))

def create_params(row):
    params = {}
    params["name"] = row[5]
    params["address1"] = row[2]
    params["city"] = row[3]
    params["state"] = "CA"
    params["country"] = "US"
    #params = {"name" : "YOGURTLAND", "address1" : "304 SANTA MONICA BLVD", "city" : "SANTA MONICA", "state" : "CA", "country" : "US"}
    return params

'''
Apply throttling so we do not get QPS errors from Yelp.
Follows the Token Bucket algorithm.

This is better than using a Semaphore because we can use the clock to rate limit.
'''
class TokenBucket:
    RATE = 5
    MAX_TOKENS = 5

    def __init__(self):
        self.tokens = self.MAX_TOKENS
        self.last_refresh = time.monotonic()

    async def get_token(self):
        while self.tokens < 1:
            self.replenish_tokens()
            await asyncio.sleep(1)
        self.tokens -= 1
        return self.tokens

    def replenish_tokens(self):
        now = time.monotonic()
        time_since_refresh = now - self.last_refresh
        new_tokens = int(time_since_refresh * self.RATE)
        # Refresh RATE tokens every ~ one second.
        if new_tokens > 1:
            self.tokens = min(self.tokens + new_tokens, self.MAX_TOKENS)
            self.last_refresh = now

async def fetch(url, uid, params, session, bucket, queue):
    t = await bucket.get_token()
    async with session.get(url, params=params) as response:
        res_text = await response.text()
        queue.put([uid, response.status, res_text])

async def run(data, queue):
    url = "https://api.yelp.com/v3/businesses/matches"
    #url = "https://test.com/"
    tasks = []
    #semi = asyncio.Semaphore(2)
    bucket = TokenBucket()
    # Client ID 2 lXj7hoG8VKcPXWFECjzs1A
    # API KEY 2
    # lyt0xVYdmqfFHAfEzZ4Bp2Sq2sBBg9j1iMVL581imdH3OO6NWwyG9gaCn1ALDutJ8UlpyX_hlfxA68w47s07TXdt2cmeAuo_QiPVeTDcCv5mYyWcDlbkmuEMWRJIW3Yx
    #headers={"Authorization": "Bearer lyt0xVYdmqfFHAfEzZ4Bp2Sq2sBBg9j1iMVL581imdH3OO6NWwyG9gaCn1ALDutJ8UlpyX_hlfxA68w47s07TXdt2cmeAuo_QiPVeTDcCv5mYyWcDlbkmuEMWRJIW3Yx"}
    # Headers for my sams.arthur acct
    #headers={"Authorization": "Bearer A61NH4bO5yCnxzogPUD6j5kucxY8Z-tFqN865_yoX04ExGpdQFRwCDhuWsgxqxBoQIOTBYBKH9ESB0KfvLSwJfTfXaNPo1gSKZ9f8Quop7xwDZdMU42kbeIhlJBCW3Yx"}
    # headers 3:
    # cSTI74uyp1mQAwzO0LFKaQ
    # SU4DsuGcc5eJSRGkPZPhw87kECpMASX2IBKIZAp5emxhQ7KCgjAS6XhRZD4DIAXCu0spXvnvROjxqXE2FePRX197SrMzwxgDIp6BCz8jEUH-5t52ZeUvv4AB7dh1IW3Yx
    #headers={"Authorization": "Bearer SU4DsuGcc5eJSRGkPZPhw87kECpMASX2IBKIZAp5emxhQ7KCjAS6XhRZD4DIAXCu0spXvnvROjxqXE2FePRX197SrMzwxgDIp6BCz8jEUH-5t52ZeUvv4AB7dh1IW3Yx"}
    # headers 4:
    #   
    async with ClientSession(connector = aiohttp.TCPConnector(verify_ssl=False), headers=headers) as session:
        with open(data, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                task = asyncio.ensure_future(fetch(url, row[1], create_params(row), session, bucket, queue))
                tasks.append(task)
        responses = asyncio.gather(*tasks)
        await responses

queue = Queue()
STOP_TOKEN="!!!STOP!!!"

parser = argparse.ArgumentParser()
parser.add_argument("prefix", help="which segment to run", type=str)
args = parser.parse_args()

prefix = args.prefix
writer_process = Process(target=writer, args=("yelp/yelp_requested_"+ prefix +".txt", queue, STOP_TOKEN))
writer_process.start()
data = "/Users/Arthur/Documents/Coding/health_scores/split/segments" + prefix
loop = asyncio.get_event_loop()
future = asyncio.ensure_future(run(data, queue))
loop.run_until_complete(future)

# Posion Pill the Queue.
queue.put(STOP_TOKEN)
writer_process.join()
