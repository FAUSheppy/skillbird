#!/usr/bin/python3
import sys
import argparse
import datetime as dt
import json
import requests
import random

possiblePlayers = {
"KD0FF8NC" : None, 
"SA5BPTYB" : None, 
"KBXGPV20" : None, 
"1TNLXYO9" : None, 
"S4M3Z7AT" : None, 
"FO4V590D" : None, 
"A116P0TY" : None, 
"8OPBPAZ1" : None, 
"QLIEC5F9" : None, 
"TYSXZB6S" : None, 
"M6Y54UI2" : None, 
"AEB7EHLC" : None, 
"OY8ZQEYJ" : None, 
"LJ5BRST2" : None, 
"CBR279YR" : None, 
"GSI4J4D3" : None, 
"YHTACQB8" : None, 
"LD2I5Z52" : None, 
"GB4ZC8Z7" : None, 
"RVT3KQZC" : None, 
"8L8UWEJE" : None, 
"VUBITUD2" : None, 
"SCG4LCK9" : None, 
"VVYP0AOE" : None, 
"8QFDCKB4" : None, 
"P4WFV6P4" : None, 
"6NDWTM7O" : None, 
"7JU4HSEQ" : None, 
"AE3V6PFV" : None, 
"0OPM7MAZ" : None, 
"160Y4R9T" : None, 
"TZ8TLYO5" : None, 
"5RHPGONF" : None, 
"AEVXADMM" : None, 
"VG70J1PR" : None, 
"TWWQXOTR" : None, 
"PW3X67XA" : None, 
"DLGGHKWZ" : None, 
"4QZVPKTG" : None, 
"I75UFRUC" : None, 
"6CY0QDF1" : None, 
"SNHDK5V3" : None, 
"91URSK04" : None, 
"P1S9GSVY" : None, 
"FZOY6QCW" : None, 
"S0EVQ1S9" : None, 
"EL3MU8YE" : None, 
"5M3S90WK" : None, 
"TUUYU1J5" : None, 
"UFT70NL1" : None }

def simulatedTime(timeSimMultiplier):
    return dt.datetime.isoformat(dt.datetime.now() + dt.timedelta(minutes=1) * timeSimMultiplier )


def genActivePlayersEvent(timeSimMultiplier):

    ## pick some random players and generate json #
    players = []
    tmp = list(possiblePlayers.keys())
    random.shuffle(tmp)
    for x in range(0,10):
        playerDict = dict()
        curPlayer  = tmp[x]
        playerDict.update({ "id"   : possiblePlayers[curPlayer] })
        playerDict.update({ "name" : curPlayer })
        playerDict.update({ "team" : (x % 2) + 2 })
        players += [playerDict]

    return { "etype" : "active_players", "timestamp" : simulatedTime(timeSimMultiplier), "players" : players }

def submitt(jsonLikeObject):
    #print(json.dumps(jsonLikeObject, indent=2))
    requests.post("http://localhost:{}/event-blob".format(args.target_port), json=jsonLikeObject)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Insurgency rating python backend server')
    parser.add_argument('--target-port', type=int, default=5000, help="HTTP API Port")
    args = parser.parse_args()

    # generate uniq playerIds    
    idCount = 0
    for p in possiblePlayers.keys():
        possiblePlayers[p] = idCount
        idCount += 1

    for r in range(1,1000):
        print(r)
        winner = random.randint(2,3)
        events = []
        events += [{ "etype" : "map",    "timestamp" : simulatedTime(r), "map" : "kappa" }]
        events += [{ "etype" : "winner", "timestamp" : simulatedTime(r+1), "winnerTeam" : winner }]
        for activityEvent in range(1,10):
            events += [genActivePlayersEvent((r*activityEvent)+2)]
        submitt({"events" : events})
