'''
This must be run in Python 3.5+ due to asyncio.

This class will perform async HTTP requests, putting the output in
a queue for a writing to storage.

First API Call is to get the Business ID:
We only need to store the Business ID, however we will write the entire reply,
since it is costly to query Yelp, and better to waste memory (<10MB) than time.

Needed Inputs:  [data: output from inspection_parser.py, request: match]

Second API call is to get the business details: 
 * Rating, Category, Reviews, Price
 * Yelp formatted name
 * Coordinates (lat/long)
 * The First Photo (image_url)

 Needed Inputs: [data: parsed output from Part 1, request: details]

 Due to the nature and limited supply of YELP API tokens, this is very manual
 and I will not bother to make it streamlined.
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
import multiprocessing
from multiprocessing import Process
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

'''
Read the row from inspection_parser.py and format the params for the API call.
Return something like:
{"name" : "YOGURTLAND", "address1" : "304 SANTA MONICA BLVD", "city" : "SANTA MONICA", "state" : "CA", "country" : "US"}
'''
def create_params_matches(row):
    params = {}
    params["name"] = row[5]
    params["address1"] = row[2]
    params["city"] = row[3]
    params["state"] = "CA"
    params["country"] = "US"
    return params

'''
Read the output from yelp_requestor.py match run, and call the API.
We only need to supply url/{id}. Not sure if params are needed.
'''
def create_params_biz(row):
    return {"uid": row[0], "id" : row[1]}

'''
Apply throttling so we do not get QPS errors from Yelp.
Follows the Token Bucket algorithm.

Does not limit the number of connections, a semaphore could be used for that,
or a callback that places the token back into the bucket.
'''
class TokenBucket:
    RATE = 5
    MAX_TOKENS = 5

    def __init__(self):
        self.tokens = 0
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

# Oops I Know you can see my client codes. But I will reset these before anyone notices this repo is public. =)
# Headers for my sams.arthur acct
#headers={"Authorization": "Bearer A61NH4bO5yCnxzogPUD6j5kucxY8Z-tFqN865_yoX04ExGpdQFRwCDhuWsgxqxBoQIOTBYBKH9ESB0KfvLSwJfTfXaNPo1gSKZ9f8Quop7xwDZdMU42kbeIhlJBCW3Yx"}
# headers 3:
# cSTI74uyp1mQAwzO0LFKaQ
# SU4DsuGcc5eJSRGkPZPhw87kECpMASX2IBKIZAp5emxhQ7KCgjAS6XhRZD4DIAXCu0spXvnvROjxqXE2FePRX197SrMzwxgDIp6BCz8jEUH-5t52ZeUvv4AB7dh1IW3Yx
#headers={"Authorization": "Bearer SU4DsuGcc5eJSRGkPZPhw87kECpMASX2IBKIZAp5emxhQ7KCjAS6XhRZD4DIAXCu0spXvnvROjxqXE2FePRX197SrMzwxgDIp6BCz8jEUH-5t52ZeUvv4AB7dh1IW3Yx"}
# Client ID 2 lXj7hoG8VKcPXWFECjzs1A
# API KEY 2
# lyt0xVYdmqfFHAfEzZ4Bp2Sq2sBBg9j1iMVL581imdH3OO6NWwyG9gaCn1ALDutJ8UlpyX_hlfxA68w47s07TXdt2cmeAuo_QiPVeTDcCv5mYyWcDlbkmuEMWRJIW3Yx
#headers={"Authorization": "Bearer lyt0xVYdmqfFHAfEzZ4Bp2Sq2sBBg9j1iMVL581imdH3OO6NWwyG9gaCn1ALDutJ8UlpyX_hlfxA68w47s07TXdt2cmeAuo_QiPVeTDcCv5mYyWcDlbkmuEMWRJIW3Yx"}
# key 4
headers={"Authorization": "Bearer HokL43SCJFNWkgiqoDEglWSgGCPj_vGrBHlYJRzvQe8l5q-HgCI78RLWqrO0UmbLDddmRyUI3qIvM81bR8iK2Nhy9X7-8nYsJoSw_q2r7jLkNlzhkTH5X2xl6WtNW3Yx"}
# Key 5   client ID ZJA9ZXqU0v5rLja9-cN5IQ
#headers={"Authorization": "Bearer XMUVIMYGd_ML1TmUNsiwq4KtDw0ShCxU2vSciaisd3pihJ205nmJbaNzr77dXv4qROzaPG3kAUbHeizYq5ciWYdb6edgUJG23oMMMjpziG-F4ZHououbiYXS7d9gW3Yx"}
async def run(url, data, param_creator, queue):
    #url = "https://test.com/"
    tasks = []
    #semi = asyncio.Semaphore(2)
    bucket = TokenBucket()
    #in TCP connector: use_ssl=False
    async with ClientSession(connector = aiohttp.TCPConnector(), headers=headers) as session:
        with open(data, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                # Ugh bad hack.
                if param_creator == create_params_biz:
                    task = asyncio.ensure_future(fetch(url + row[1], row[0], {}, session, bucket, queue))
                else:
                    # UID is the Record ID of the Row (15).
                    task = asyncio.ensure_future(fetch(url, row[15], param_creator(row), session, bucket, queue))
                tasks.append(task)
        responses = asyncio.gather(*tasks,return_exceptions=True)
        await responses

def main():
    STOP_TOKEN = "!!!STOP!!!"
    # The thread safe writing Queue.
    queue = multiprocessing.Queue()

    parser = argparse.ArgumentParser()
    parser.add_argument("data_src", help="which data to run over", type=str)
    parser.add_argument("request", help="which request to get (match or details) ", type=str)
    args = parser.parse_args()

    data_src = args.data_src
    # Grab the filename. Not robust, but works for my naming scheme.
    data_prefix = (data_src.split("/")[-1]).split(".")[0]
    output_prefix = ""
    url = ""
    param_fn = ""
    if args.request == "match":
        output_prefix = "yelp_calls/yelp_requested_"
        param_fn = create_params_matches
        url = "https://api.yelp.com/v3/businesses/matches"
    elif args.request == "details":
        output_prefix = "yelp_calls/details_"
        param_fn = create_params_biz
        url = "https://api.yelp.com/v3/businesses/"

    writer_process = Process(target=writer, args=(output_prefix + data_prefix + ".txt", queue, STOP_TOKEN))
    writer_process.start()

    loop = asyncio.get_event_loop()

    future = asyncio.ensure_future(run(url, data_src, param_fn, queue))
    loop.run_until_complete(future)

    # Posion Pill the Queue.
    queue.put(STOP_TOKEN)
    writer_process.join()

if __name__ == '__main__':
   main()

#python3 yelp_requestor.py split/segmentsaqrst match