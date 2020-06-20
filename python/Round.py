import json
import datetime as dt
import dateutil.parser
import backends.entities.Players as Players
import backends.database         as db
import backends.trueskillWrapper as ts

## A comment on why the login-offset is nessesary ##
## - losing teams tend to have players leaving and joining more rapidly
## - every time a new player joins he has to setup
## - new players are unfamiliar with postions of enemy team
## - new players have to run from spawn
## --> their impact factor (which is calculated from their active time) must account for that
loginoffset = dt.timedelta(seconds=60)

class Round:

    def __init__(self, winnerTeam, loserTeam, _map, duration, startTime, winnerSide):

            if duration <= dt.timedelta(0):
                raise ValueError("Duration cannot be zero")

            self.winners     = winnerTeam
            self.losers      = loserTeam
            self.winnerSide = winnerSide
            self.map         = _map
            self.duration    = duration
            self.start       = startTime

            ### Sync players from Databse ###
            for p in self.winners + self.losers:
                playerInDB = db.getOrCreatePlayer(p)
                p.rating   = playerInDB.rating

            self.prediction, self.confidence = ts.predictOutcome(self.winners, self.losers)

    def normalized_playtimes(self):
        '''returns a dict-Object with {key=(teamid,player):value=player_time_played/total_time_of_round}'''
        
        np = dict()
        for p in self.winners:
            if self.duration == None:
                d = 1.0
            else:
                d = (p.activeTime-loginoffset)/self.duration
            if d < -1:
                raise AssertionError("Normalized Playtime was less than -1 ??")
            if d < 0:
                d = 0.0
            elif d > 1:
                d = 1.0
            np.update({(0,p):d})

        for p in self.losers:
            if self.duration == None:
                d = 1.0
            else:
                d = (p.activeTime-loginoffset)/self.duration
            if d < 0:
                d = 0.0
            elif d > 1:
                d = 1.0
            np.update({(1,p):d})

        return np

    def pt_difference(self):
        '''Used to check difference in playtimes per team'''

        if self.duration == None:
            return 1
        w1 = w2 = 0
        for p in self.winners:
            if p.is_fake:
                w1 += 1.0
                continue
            d = (p.activeTime-loginoffset)/self.duration
            if d < 0:
                d = 0.0
            elif d > 1:
                d = 1.0
            w1 += d
        for p in self.losers:
            d = (p.activeTime-loginoffset)/self.duration
            if p.is_fake:
                w2 += 1.0
                continue
            if d < 0:
                d = 0.0
            elif d > 1:
                d = 1.0
            w2 += d

        # no div0 plox
        if min(w1,w2) <= 0:
            return 0

        return max(w1,w2)/min(w1,w2)

    def toJson(self):
        winnersList = []
        losersList  = []
        for w in self.winners:
            winnersList += [{ "playerId" : w.id, 
							  "playerName" : w.name, 
						      "isFake" : w.is_fake, 
							  "activeTime" : w.activeTime.total_seconds() }]

        for w in self.losers:
            losersList +=  [{ "playerId" : w.id, 
							  "playerName" : w.name, 
						      "isFake" : w.is_fake, 
							  "activeTime" : w.activeTime.total_seconds() }]

        retDict = { "winners" : winnersList,
                    "losers"  : losersList,
                    "startTime" : self.start.isoformat(),
                    "duration"  : self.duration.total_seconds(),
					"map"		: self.map,
					"winner-side" : self.winnerSide }

        return json.dumps(retDict)

def fromJson(jsonDict):
    winnersList = []
    losersList  = []
    
    timestamp = dateutil.parser.isoparse(jsonDict["startTime"])
    winnerTeam = jsonDict.get("winner-side")
    if not winnerTeam:
        winnerTeam = -1
        loserTeam  = -2
    else:
        loserTeam = (winnerTeam % 2) + 2

    for p in jsonDict["winners"]:
        pObj = Players.PlayerInRound(p["playerId"], p["playerName"], winnerTeam, timestamp)
        pObj.activeTime = dt.timedelta(int(p["activeTime"]))
        winnersList += [pObj]

    for p in jsonDict["losers"]:
        pObj = Players.PlayerInRound(p["playerId"], p["playerName"], loserTeam, timestamp)
        pObj.activeTime = dt.timedelta(int(p["activeTime"]))
        losersList += [pObj]

    duration = dt.timedelta(seconds=int(jsonDict["duration"]))
    return Round(winnersList, losersList, jsonDict["map"], duration, timestamp, winnerTeam)
