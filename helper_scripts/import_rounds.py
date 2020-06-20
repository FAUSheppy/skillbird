#!/usr/bin/python3

import sys
import requests
import json
import datetime as dt

if not len(sys.argv)>1:
    sys.exit(1)

count = 31000
i = 0
skip = 0
if len(sys.argv)>2:
    skip = int(sys.argv[2])

start = dt.datetime.now()
url = "http://127.0.0.1:5000/submitt-round"

with open(sys.argv[1], "r") as f:
    for l in f:
        if skip > 0:
            skip -= 1;
            i+=1
            continue
        requests.post(url, json=json.loads(l))
        cur = dt.datetime.now()
        i+=1

        percent = int(i/count*100);
        elapsed = str(cur-start)
        estRem  = str((cur-start)/i*count)
        if "." in estRem:
            estRem = estRem.split(".")[0]
        if "." in elapsed:
            elapsed = elapsed.split(".")[0]
        print("Round: {} ({}%) - elapsed: {}, estimated remaining: {}\r".format(i, percent, elapsed, estRem), end="")
