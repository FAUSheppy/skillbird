import datetime

class Player:
        def __init__(self, steamid, name, rating=None):
            if rating:
                self.rating = rating
            else:
                self.rating = TS.new_rating()
            self.steamid = steamid
            self.cur_name = name
        def __hash__(self):
            return hash(self.steamid)
        def __eq__(self, other):
            if not other:
                return False
            if isinstance(other,str):
                return self.steamid == other
            elif isinstance(other,Player):
                return self.steamid == other.steamid
            else:
                raise TypeError("Unsupported Equals with types {} and {}".format(type(other),type(self)))
        def __str__(self):
            return "Player: {}, ID: {}".format(self.name, self.steamid)

class DummyPlayer(Player):
        def __init__(self, steamid, name="PLACEHOLDER", rating=None):
            self.rating = TS.new_rating()
            if rating:
                self.rating = rating
            self.name     = name
            self.cur_name = name
            super().__init__(steamid, name)

class PlayerInRound(Player):
        def __init__(self, steamid, name, team, timestamp):
            self.name = name
            self.cur_name = name
            self.steamid = steamid
            self.rating = TS.new_rating()
            self.active_time     = datetime.timedelta(0)
            if type(team) != int or team > 3 or team < 0:
                raise Exception("Invalid TeamID '{}', must be 0-3 (inkl.)".format(team))
            self.team            = int(team)
            self.active          = True   # unset when player has disconnected or changed team
            if not timestamp:
                self.is_fake = True
            else:
                self.is_fake = False
            self.timestamp = timestamp
        def __str__(self):
            return "TMP-Player: {}, ID: {}, active: {}".format(self.cur_name,self.steamid,self.active_time)

class PlayerForDatabase(Player):
        def __init__(self,steamid,name,rating,player=None):
            if player:
                self.steamid = player.steamid
                self.name    = player.name
                self.rating  = player.rating
            else:
                self.steamid = steamid
                self.name    = name
                self.rating  = rating
            self.games = 0
            self.wins  = 0
        def winratio(self):
            if self.games == 0:
                return "---"
            return str(int(self.wins*100/self.games))
        def get_name(self):
            return self.name.encode('utf-8')[:25].decode('utf-8','ignore').rstrip(" ")

class PlayerFromDatabase(PlayerForDatabase):
        def __init__(line):
            super().__init__(None,None,None)
