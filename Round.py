from datetime import timedelta, datetime
import threading
from Player import PlayerInRound
import TrueSkillWrapper as TS

## A comment on why the login-offset is nessesary ##
## - losing teams tend to have players leaving and joining more rapidly
## - every time a new player joins he has to setup
## - new players are unfamiliar with postions of enemy team
## - new players have to run from spawn
## --> their impact factor must account for that
loginoffset = timedelta(seconds=60)

class Round:
    writeLock = threading.RLock()
    def __init__(self, winner_team, loser_team, _map, duration,\
                    starttime, winner_side=None, cache=None):
            self.winners     = winner_team
            self.losers      = loser_team
            self.winner_side = winner_side
            self.map         = _map
            self.duration    = duration
            self.start       = starttime
            #self.add_fake_players()
            if cache:
                Round.writeLock.acquire()
                with open(cache, "a") as f:
                    f.write(self.serialize())
                    f.write("\n")
                    f.flush()
                Round.writeLock.release()


    def normalized_playtimes(self):
        '''returns a dict-Object with {key=(teamid,player):value=player_time_played/total_time_of_round}'''
        np = dict()

        for p in self.winners:
            if self.duration == None:
                d = 1.0
            else:
                d = (p.active_time-loginoffset)/self.duration
            if d < -1:
                print("lol")
            if d < 0:
                d = 0.0
            elif d > 1:
                d = 1.0
            np.update({(0,p):d})
        for p in self.losers:
            if self.duration == None:
                d = 1.0
            else:
                d = (p.active_time-loginoffset)/self.duration
            if d < 0:
                d = 0.0
            elif d > 1:
                d = 1.0
            np.update({(1,p):d})

        return np

    def add_fake_players(self):
        ''' adds map/side specific player to account for asynchronous gameplay '''
        if not self.map:
            #print("Warning: No map info, cannot add fake players.")
            return
        ins = self.map+str(2)
        sec = self.map+str(3)

        p_ins = PlayerInRound(ins,2,None)
        p_sec = PlayerInRound(sec,3,None)

        if p_ins in Storrage.known_players:
            p_ins = Storrage.known_players[p_ins]
        if p_sec in Storrage.known_players:
            p_sec = Storrage.known_players[p_sec]

        if self.winner_side == 2:
            self.winners += [p_ins]
            self.losers += [p_sec]
        else:
            self.winners += [p_sec]
            self.losers += [p_ins]

    def pt_difference(self):
        '''Used to check difference in playtimes per team'''
        if self.duration == None:
            return 1
        w1 = w2 = 0
        for p in self.winners:
            if p.is_fake:
                w1 += 1.0
                continue
            d = (p.active_time-loginoffset)/self.duration
            if d < 0:
                d = 0.0
            elif d > 1:
                d = 1.0
            w1 += d
        for p in self.losers:
            d = (p.active_time-loginoffset)/self.duration
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

    def serialize(self):
        # full = winners|losers|winner_side|map|duration|start
        # winners/losers = p1,p2,p3 ...
        winners = ""
        losers = ""
        for p in self.winners:
            winners += "," + p.serialize()
        for p in self.losers:
            losers += "," + p.serialize()
        
        teams = "{}|{}".format(winners, losers)
        startTimeStr = self.start.strftime("%y %b %d %H:%M:%S")

        ret = "{}|{}|{}|{}|{}".format(teams, self.winner_side, \
                                        self.map, self.duration.seconds, startTimeStr)
        return ret

    def deserialize(string):
        string = string.strip("\n")
        winnersStr, losersStr, winner_side, _map, duration, startTimeStr = string.split("|")
        winners = dict()
        losers  = dict()
        for pStr in winnersStr.split(","):
            if pStr == "":
                continue
            winners.update({PlayerInRound.deserialize(pStr):TS.newRating()})
        for pStr in losersStr.split(","):
            if pStr == "":
                continue
            losers.update({PlayerInRound.deserialize(pStr):TS.newRating()})
        startTime = datetime.strptime(startTimeStr, "%y %b %d %H:%M:%S")
        duration = timedelta(seconds=int(duration))
        return Round(winners, losers, _map, duration, startTime, winner_side)
