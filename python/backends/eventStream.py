import abc
import dateutil.parser
import datetime as dt

import Round
import backends.entities.Players as Players

NO_TEAM   = 0                                                                                       
OBSERVERS = 1
SECURITY  = 2
INSURGENT = 3

def _getKey(dic, key):
    '''Helper function''' 
    tmp = list(dic)
    return tmp[tmp.index(key)]


def parse(events):
    '''Parse a string blob representing a full round'''

    eventsParsed = []
    for eventJsonObject in events:
        eventsParsed += [parseEventString(eventJsonObject)]

    es = EventSeries(eventsParsed)
    return Round.Round(es.winnerTeam, es.loserTeam, es.map, es.duration, es.startTime, es.winnerTeamId)

def parseEventString(event):
    '''Take a dictionary representing an event and return an actual event object'''

    TEAMCHANGE      = ["teamchange"]
    ACTIVE_PLAYERS  = ["ct","dc","round_start_active","round_end_active","tc","active_players"]
    DISCONNECT      = ["disconnect"]
    WINNER_INFO     = ["winner"]
    MAP_INFO        = ["mapname", "map"]
    IGNORE          = ["map_start_active","start","plugin unloaded"]
  
    print(event)

    etype = event["etype"]
    if False:
        pass
#   elif etype in TEAMCHANGE:
#        return TeamchangeEvent(event)
    elif etype in ACTIVE_PLAYERS:
        return ActivePlayersEvent(event)
#    elif etype in DISCONNECT:
#        return DisconnectEvent(event)
    elif etype in WINNER_INFO:
        return WinnerInformationEvent(event)
    elif etype in MAP_INFO:
        return MapInformationEvent(event)
    elif etype in IGNORE:
        pass

class Event(abc.ABC):
    '''Abstract class all events inherit from'''
    pass

#class DisconnectEvent(Event):
#    '''Event describing a disconnect by an individual player'''
#
#    def __init__(self, event):
#        self.timestamp = dt.datetime.fromtimestamp(event["timestamp"])
#        self.player    = event["playerId"]
#
#class TeamchangeEvent(Event):
#    '''Event describing a teamchange by an individual player'''
#
#    def __init__(self, event):
#        self.timestamp = dt.datetime.fromtimestamp(event["timestamp"])
#        self.player    = event["playerId"]
#        self.old_team  = event["previousTeam"]

class ActivePlayersEvent(Event):
    '''Event describing as absolute values the currently active player'''
    
    def __init__(self, event):
        self.timestamp = dt.datetime.fromtimestamp(event["timestamp"])
        self.players   = [ Players.PlayerInRound(p["id"], p["name"], p["team"], self.timestamp) 
                                for p in event["players"] ]

class WinnerInformationEvent(Event):
    '''Event describing which team has won the game'''

    def __init__(self, event):
        self.timestamp = dt.datetime.fromtimestamp(event["timestamp"])
        self.winner    = event["winnerTeam"]

class MapInformationEvent(Event):
    '''Event describing the current map'''

    def __init__(self, event):
        self.timestamp = dt.datetime.fromtimestamp(event["timestamp"])
        self.map = event["map"]

class EventSeries():
    def __init__(self, events):

        self.events         = events
        self.winnerTeam     = None
        self.winnerTeamId   = -1
        self.loserTeam      = None
        self.loserTeamId    = -1
        self.map            = ""

        lastEvent  = max(events, key=lambda e: e.timestamp)
        firstEvent = min(events, key=lambda e: e.timestamp)

        self.duration = lastEvent.timestamp - firstEvent.timestamp
        self.startTime = firstEvent.timestamp



        self.teamA     = []
        self.teamAId   = 2
        self.teamB     = []
        self.teamBId   = 3

        for e in events:
            if type(e) == ActivePlayersEvent:
                for playerInRound in e.players:

                    ## Case 1: Player isn't in any team yet
                    if playerInRound not in self.teamA and playerInRound not in self.teamB:
                        playerInRound.active = True
                        if playerInRound.team == self.teamAId:
                            self.teamA += [playerInRound]
                        else:
                            self.teamB += [playerInRound]

                    ## Case 2: Player is in the wrong team
                    if playerInRound not in self._teamFromId(playerInRound.team):
                        index = self._teamFromId(playerInRound.team, inverted=True).index(playerInRound)
                        playerInEventSeries = self._teamFromId(playerInRound.team, inverted=True)[index]
                        
                        # update playtime #
                        playerInEventSeries.active = False
                        playerInEventSeries.activeTime += e.timestamp - playerInEventSeries.timestamp

                        # add player to correct team #
                        playerInRound.active = True
                        if playerInRound.team == self.teamAId:
                            self.teamA += [playerInRound]
                        else:
                            self.teamB += [playerInRound]

                    ## Case 3: Player is already in the correct team
                    else:
                        index = self._teamFromId(playerInRound.team).index(playerInRound)
                        playerInEventSeries = self._teamFromId(playerInRound.team)[index]

                        # update playtime #
                        if playerInEventSeries.active:
                            playerInEventSeries.activeTime += e.timestamp - playerInEventSeries.timestamp
                        playerInEventSeries.timestamp = e.timestamp
                        playerInEventSeries.active  = True
                
                # mark all missing players as inactive and update their play times #
                for playerInEventSeries in self.teamA + self.teamB:
                    if playerInEventSeries not in e.players:

                        # update playtime #
                        playerInEventSeries.active = False
                        playerInEventSeries.activeTime += e.timestamp - playerInEventSeries.timestamp

            elif type(e) == WinnerInformationEvent:
                self.winnerTeamId = int(e.winner)
                self.winnerTeam   = self._teamFromId(self.winnerTeamId)
                self.loserTeam    = self._teamFromId(self.winnerTeamId, inverted=True)
            elif type(e) == MapInformationEvent:
                self.map = e.map

        ### normalize teamchanges
        toBeRemovedFromLosers  = [] # cannot change iteable during iteration
        toBeRemovedFromWinners = []

        for playerInEventSeries in self.winnerTeam:
            if playerInEventSeries in self.loserTeam:
                
                # get active time in both teams #
                playerLoserTeamIndex = self.loserTeam.index(playerInEventSeries)
                loserTeamActiveTime  = self.loserTeam[playerLoserTeamIndex].activeTime
                winnerTeamActiveTime = playerInEventSeries.activeTime

                # substract the smaller active time and mark player #
                # to be removed from the team he played less on     #
                if winnerTeamActiveTime > loserTeamActiveTime:
                    toBeRemovedFromLosers += [playerInEventSeries]
                    playerInEventSeries.activeTime - loserTeamActiveTime
                else:
                    toBeRemovedFromWinners += [playerInEventSeries]
                    self.loserTeam[playerLoserTeamIndex].activeTime -= winnerTeamActiveTime
        
        # after iteration actually remove the players #
        for player in toBeRemovedFromWinners:
            self.winnerTeam.remove(player)
        for player in toBeRemovedFromLosers:
            self.loserTeam.remove(player)


    def _teamFromId(self, teamId, inverted=False):
        '''Return the attribute array representing the teamId in this event series 
            or a dummy array for observers and no-team
            Inverted: return the team NOT beloning to the teamId'''

        if inverted:
            teamId = ( teamId + 1 ) % 2 +2 # 2 => 3 and 3 => 2, 0/1 don't matter

        if teamId == OBSERVERS or teamId == NO_TEAM:
            return []
        elif teamId == 2:
            return self.teamA;
        elif teamId == 3:
            return self.teamB;
        else:
            errorMsg = "TeamID must be 0 - NoTeam, 1 - Observers, 2 - Security or 3 - Insurgent, but was {}"
            raise ValueError(errorMsg.format(teamId))
