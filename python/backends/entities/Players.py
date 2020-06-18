import datetime as dt
import json

class Player:
    def __init__(self, playerId, name, rating=None):
        self.rating = rating
        self.id = playerId
        self.name = name

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not other:
            return False
        elif isinstance(other, str):
            return self.id == other
        elif isinstance(other, Player):
            return self.id == other.id
        else:
            raise TypeError("Player: Unsupported equals with types {} and {}".format(type(other),type(self)))

    def __str__(self):
        return "Player: {}, ID: {}".format(self.name, self.id)

class PlayerInRound(Player):
        def __init__(self, playerId, name, team, timestamp, is_fake=False):
            self.name   = name
            self.id     = playerId
            self.team   = int(team)
            self.active = True
            self.rating = None
            self.activeTime = dt.timedelta(0)
            self.is_fake = is_fake
            self.timestamp = timestamp

        def __str__(self):
            return "PlayerInRound: N: {} ID: {} Team: {}".format(self.name, self.id, self.team)

def playerInRoundFromJson(jsonDict):
        return PlayerInRound(jsonDict["id"], jsonDict["name"], jsonDict["team"], timestamp=dt.datetime.now())

class PlayerInDatabase(Player):

        def __init__(self, playerId, name, rating, wins, games):
            self.id         = playerId
            self.name       = name
            self.rating     = rating
            self.lastUpdate = dt.datetime.now()
            self.wins       = wins
            self.games      = games

        def winratio(self):
            if self.games == 0:
                return "---"
            return str(int(self.wins*100/self.games))

        def getName(self):
            return self.name.encode('utf-8')[:25].decode('utf-8','ignore').rstrip(" ")

        def toJson(self):
            retDict = { "name" : self.name, 
                            "id" : self.id, 
                            "rating-mu" : self.rating.mu,
                            "rating-sigma" : self.rating.sigma,
                            "games" : self.games,
                            "wins" : self.wins,
                            "last-game" : self.lastUpdate.isoformat()}

            return json.dumps(retDict)
