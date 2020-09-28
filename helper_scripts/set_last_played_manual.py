#!/usr/bin/python3

import sqlite3
import datetime
import json
import requests

url = "http://127.0.0.1:5000/submitt-round"
db = "rounds.sqlite"
db_players = "players.sqlite"

if __name__ == "__main__":
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    connPlayers = sqlite3.connect(db_players)
    cursorPlayers = connPlayers.cursor()

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

        updateQuery = "UPDATE players SET lastgame = ? where id = ?"
        for p in winnersParsed:
            cursorPlayers.execute(updateQuery, (timestamp, p["id"]))
        for p in losersParsed:
            cursorPlayers.execute(updateQuery, (timestamp, p["id"]))

        connPlayers.commit()
        # status update #
        cur = datetime.datetime.now()
        percent = int(i/count*100);
        elapsed = str(cur-start).split(".")[0]
        estTot  = str((cur-start)/i*count).split(".")[0]
        i += 1
        print("Round: {} ({}%) - elapsed: {}, estimated total: {}\r".format(
                i, percent, elapsed, estTot), end="")
