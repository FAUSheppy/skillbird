#!/usr/bin/python3

import sqlite3
import datetime
import json
import requests

url = "http://127.0.0.1:5000/submitt-round"
db = "rounds.sqlite"

if __name__ == "__main__":
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # status display #
    start = datetime.datetime.now()
    cursor.execute("select count(*) from rounds")
    count = cursor.fetchone()[0]
    i = 1

    cursor.execute("select * from rounds order by timestamp ASC")
    for row in cursor:

        # load from db
        timestamp, winners, losers, winnerSide, mapName, duration, prediction, confidence = row
        startTime = datetime.datetime.fromtimestamp(int(float(timestamp)))
        winnersParsed = json.loads(winners)
        losersParsed  = json.loads(losers)

        # fix id/playerId db field name for now #
        for pElement in winnersParsed:
            pElement["playerId"] = pElement.pop("id")
            pElement["playerName"] = pElement.pop("name")
            pElement["activeTime"] = pElement.pop("active_time")
        for pElement in losersParsed:
            pElement["playerId"] = pElement.pop("id")
            pElement["playerName"] = pElement.pop("name")
            pElement["activeTime"] = pElement.pop("active_time")

        data = { "map" : mapName,
                 "winner-side" : winnerSide,
                 "winners" : winnersParsed,
                 "losers" : losersParsed,
                 "duration" : duration,
                 "startTime" : startTime.isoformat()}
        
        # submit
        requests.post(url, json=data)

        # status update #
        cur = datetime.datetime.now()
        percent = int(i/count*100);
        elapsed = str(cur-start).split(".")[0]
        estTot  = str((cur-start)/i*count).split(".")[0]
        i += 1
        print("Round: {} ({}%) - elapsed: {}, estimated total: {}\r".format(
                i, percent, elapsed, estTot), end="")
