import Player
from datetime import datetime, timedelta

class Event:
    def __init__(self,timestamp,_map=None):
        self.map = _map
        self.timestamp = timestamp
    def serialize(self):
        raise NotImplementedError()

class DisconnectEvent(Event):
    def __init__(self,player,timestamp,line):
        self.timestamp = timestamp
        self.player = player
        self.string = line
    def serialize(self):
        return {"etype":"DCE","timestamp":self.timestamp.strftime(),"string":self.string}

class TeamchangeEvent(Event):
    def __init__(self,player,old_team,timestamp,line):
        self.timestamp = timestamp
        self.player = player
        self.old_team = int(old_team)
        self.string = line
    def serialize(self):
        return {"etype":"TCE","timestamp":self.timestamp.strftime(),"string":self.string}

class ActivePlayersEvent(Event):
    def __init__(self,player_str,timestamp):
        self.timestamp = timestamp
        self.players = []
        self.string = player_str
        try:
            for s in player_str.split(","):
                if not s or len(s.split("|"))==1:
                    continue
                steamid = s.split("|")[1]
                name    = s.split("|")[2]
                team    = int(s.split("|")[3])
                self.players += [Player.PlayerInRound(steamid,name,team,self.timestamp)]
        except IndexError:
            print("ERROR: CANNOT PARSE LOGLINE: {}".format(player_str))
            print("WARNING: EVENT WILL BE USED IN INCOMPLETE STATE")

    def serialize(self):
            return {"etype":"APE","timestamp":self.timestamp.strftime(),"string":self.string}

class WinnerInformationEvent(Event):
    def __init__(self,winner_side,timestamp,line):
        self.timestamp = timestamp
        self.winner = winner_side
        self.string = line
    def serialize(self):
        return {"etype":"WIE","timestamp":self.timestamp.strftime(),"string":self.string}

class MapInformationEvent(Event):
    def __init__(self,_map,timestamp,line):
        self.timestamp = timestamp
        self.map = _map
        self.string = line
    def serialize(self):
        return {"etype":"MIE","timestamp":self.timestamp.strftime(),"string":self.string}

class MapInformationEvent(Event):
    def __init__(self,_map,timestamp,line):
        self.timestamp = timestamp
        self.map = _map
        self.string = line
    def serialize(self):
        return {"etype":"MIE","timestamp":self.timestamp.strftime(),"string":self.string}





