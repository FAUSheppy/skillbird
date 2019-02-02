import insurgencyEvent as Event
from datetime import timedelta

NO_TEAM   = 0                                                                                       
OBSERVERS = 1
SECURITY  = 2
INSURGENT = 3

class EventSeries(list):
    def __init__(self):
        self.winner_side_cache = None
        self.loser_side_cache  = None
        self.map_cache         = None
        self.security_cache    = dict()
        self.insurgent_cache   = dict()

    def _cache_teams(self):
        for e in self:
            if type(e) == Event.ActivePlayersEvent:
                # TODO deal with players that are missing without a teamchange or dc event #
                for p in e.players:
                    if p not in self._team_from_id(p.team):
                        self._team_from_id(p.team).update({p:p.rating})
                    else:
                        tmp_team   = list(self._team_from_id(p.team))
                        tmp_player = tmp_team[tmp_team.index(p)]
                        ## Add active time if player was active last event ##
                        if tmp_player.active:
                            tmp_player.active_time += e.timestamp - tmp_player.timestamp
                        tmp_player.timestamp = e.timestamp
                        tmp_player.active  = True

            ## set player.active to false for disconnect or teamchange, it will be set to true at the next event that player is seen in a team ##
            elif type(e) == Event.DisconnectEvent:
                if e.player in self.security_cache and get_key(self.security_cache,e.player).active:
                    get_key(self.security_cache,e.player).active_time += e.timestamp - get_key(self.security_cache,e.player).timestamp
                    get_key(self.security_cache,e.player).active = False
                elif e.player in self.insurgent_cache and get_key(self.insurgent_cache,e.player).active:
                    get_key(self.insurgent_cache,e.player).active_time += e.timestamp - get_key(self.insurgent_cache,e.player).timestamp
                    get_key(self.insurgent_cache,e.player).active = False
            elif type(e) == Event.TeamchangeEvent:
                if e.player in self._team_from_id(e.old_team):
                    get_key(self._team_from_id(e.old_team),e.player).active_time += e.timestamp-get_key(self._team_from_id(e.old_team),e.player).timestamp
                    get_key(self._team_from_id(e.old_team),e.player).active     = False

    def _find_winner(self):
        time = "NO_TIME_FOUND"
        for e in self:
            time = e.timestamp#.strftime("%d-%m-%Y %H:%M:%S")
            if type(e) == Event.WinnerInformationEvent:
                if self.winner_side_cache != None:
                    raise Warning("%s | Info: More than one Winner in series, skipping Round."%time)
                self.winner_side_cache = int(e.winner)
                self.loser_side_cache  = ( ( ( int(e.winner) - 2 ) + 1 ) % 2) + 2 #löl
        if self.winner_side_cache:
            return self.winner_side_cache
        else:
            raise Warning("%s | Info: No winner found in series, skipping Round."%time)

    def _team_from_id(self,tid):
        if tid == OBSERVERS or tid == NO_TEAM:
            return dict()
        elif tid == SECURITY:
            return self.security_cache;
        elif tid == INSURGENT:
            return self.insurgent_cache;
        else:
            raise ValueError("TeamID must be 0 - NoTeam, 1 - Observers, 2 - Security or 3 - Insurgent, but was {}".format(tid))

    def get_duration(self):
        key = lambda x: x.timestamp
        max_   = max(self,key=key)
        min_   = min(self,key=key)
        ret    = max_.timestamp-min_.timestamp
        if ret > timedelta(seconds=60*30):
                raise Warning("%s | Info: Round Length was %s, too long,  ignoring."%(min_.timestamp,ret))
        if ret < timedelta(seconds=60*3):
                raise Warning("%s | Info: Round Length was %s, too short, ignoring."%(min_.timestamp,ret))
        return ret

    def get_starttime(self):
        key = lambda x: x.timestamp
        return min(self,key=key).timestamp

    def get_winners(self):
        if not self.security_cache or not self.insurgent_cache:
            self._cache_teams()
            self._find_winner()
        return self._team_from_id(self.winner_side_cache)

    def get_losers(self):
        if not self.security_cache or not self.insurgent_cache:
            self._cache_teams()
            self._find_winner()
        return self._team_from_id(self.loser_side_cache)

    def get_map(self):
        if self.map_cache == None:
            for e in self:
                if type(e) == Event.MapInformationEvent:
                    self.map_cache = e.map
        return self.map_cache

def get_key(dic,key):
    tmp = list(dic)
    return tmp[tmp.index(key)]    
