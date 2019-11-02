import Player
import TrueSkillWrapper as TS
from fuzzywuzzy import fuzz
from datetime import datetime, timedelta

known_players = dict()

# care for cpu load #
player_ranks = dict()
playerRankList = []
last_rank_update = datetime.now()- timedelta(minutes=5)

#############################################################
###################### Save/Load File #######################
#############################################################

def load_save():
        with open("score.log") as f:
                for l in f:
                        p = Player.PlayerFormDatabase(l)
                        known_players[p.steamid] = p

def save_to_file(fname="score.log"):
        with open(fname,"w") as f:
                for p in known_players.values():
                        f.write(p.toCSV()+'\n')

#############################################################
###################### SyncPlayerDict #######################
#############################################################

def sync_from_database(players):
    for p in players:
        if p in known_players:
            p.rating   = known_players[p].rating
            if type(players) == dict:
                players[p] = p.rating
            if not p.name or p.name == "PLACEHOLDER":
                p.name = known_players[p].name
        else:
            lastUpdate = datetime.now()
            known_players.update(\
                            { Player.DummyPlayer(p.steamid, p.name) : \
                              Player.PlayerForDatabase(None, None, None, player=p, lastUpdate=lastUpdate)\
                            })

def sync_to_database(players, win):
    for p in players:
        known_players[p].rating = players[p]
        if win:
            known_players[p].wins += 1
        known_players[p].games += 1
        known_players[p].lastUpdate = datetime.now()

    updatePlayerRanks(force=True)

#############################################################
##################### Handle Rank Cache #####################
#############################################################

def updatePlayerRanks(force=False, minGames=10, maxInactivityDays=60):
    '''Precalculate player ranks to be used for low performance impact'''

    global last_rank_update
    global player_ranks
    global playerRankList

    if force or datetime.now() - last_rank_update > timedelta(seconds=240):
        last_rank_update = datetime.now()

        # sort players by rank #
        sortKey = key = lambda x: TS.getEnviroment().expose(x.rating)
        sortedPlayers = sorted(known_players.values(), key=sortKey, reverse=True)

        # filter out inactive and low-game players #
        maxInactivityDelta = timedelta(days=maxInactivityDays)
        filterKey          = lambda p: (last_rank_update - p.lastUpdate) < maxInactivityDelta \
                                                                            and p.games >= minGames
        filteredPlayers    = list(filter(filterKey, sortedPlayers))

        # assing ranks to player objects #
        rankCounter = 1
        for p in filteredPlayers:
            if p in player_ranks:
                player_ranks[p] = rankCounter
            else:
                player_ranks.update({p:rankCounter})
            rankCounter += 1

        # list of players in the right order for a leaderboard #
        playerRankList = list(filteredPlayers)


#############################################################
################## Write/Load External DB ###################
#############################################################

def save_event(event):
        return

def save_psql():
        f=open("pass.secret",'r')
        pw=f.readline().strip();
        f.close()
        PSQL.save("insurgency", "insurgencyUser", "localhost", pw, known_players)

#############################################################
###################### Python API ###########################
#############################################################

def getPlayer(pid, name="NOTFOUND"):
        return known_player[pid]

def searchPlayerByName(name):
        '''Find a player by his name'''
        global player_ranks

        ret = ""
        tup_list = []
        TS.lock()
        try:
            for p in known_players.values():
                sim = fuzz.token_set_ratio(name.lower(),p.name.lower())
                tup_list += [(sim,p)]
            tmp = sorted(tup_list, key=lambda x: x[0], reverse=True)
            players = list([x[1] for x in filter(lambda x: x[0] > 80, tmp)])
            
            # update ranks #
            updatePlayerRanks(force=True)
    
            # build rank tupel #
            playerRankTupel = []
            for p in players:
                try:
                    playerRankTupel += [(p.steamid, p.name, p.rating, player_ranks[p])]
                except KeyError:
                    noRankExplanation = "inactive"
                    if p.games < 10:
                        noRankExplanation = "not enough games"
                    playerRankTupel += [(p.steamid, p.name, p.rating, noRankExplanation)]
        finally:
            TS.unlock()
        return playerRankTupel

def getPlayerRank(playerID):
    '''Get a players rank'''

    global player_ranks
    try:
        return str(player_ranks[playerID])
    except KeyError:
        return "N/A"

def getBalancedTeams(players, buddies=None, teamCount=2):
    '''Balance a number of players into teams'''
    
    if teamCount != 2:
        raise NotImplementedError("Only supporting balancing into two teams currently")
    if not players:
        return ValueError("Input contains no players")
    
    if type(players[0]) == str:
        players = [ Player.DummyPlayer(playerID) for playerID in players]
    
    sync_from_database(players)
    
    arr = sorted(players, key=lambda x: x.rating.mu, reverse=True)
    ret=""
    i = 0
    while i < len(arr):
        ret += "{}|{},".format(players[i].name,(i%2)+2)
        i += 1
    return ret

def qualityForTeams(teamArray):
    '''Get quality for number of teams with players'''

    if not teamArray or len(teamArray) < 2 or not teamArray[0]:
        raise ValueError("Team Array must be more than one team with more than one player each")
        
    if type(teamArray[0][0]) == str:
        teamArray = [ [ Player.DummyPlayer(playerID) for playerID in team ] for team in teamArray ]
    
    for team in teamArray:
        print(team[0].steamid)
        sync_from_database(team)

    teamAsRatings = [ [ player.rating for player in team ] for team in teamArray ]
    teamAsNames   = [ [ player.name for player in team ] for team in teamArray ]
    
    # TODO: implement for !=2 teams #
    if len(teamArray) != 2:
        raise NotImplementedError("Quality is only supported for exactly two teams")
    
    return qualityForRatings(teamAsRatings[0], teamAsRatings[1], teamAsNames[0], teamAsNames[1])
    
def qualityForRatings(team1, team2, names1 = [""], names2 = [""]):
    '''Get Quality for two arrays containing TrueSkill.Rating objects'''

    mu1 = sum(r.mu for r in team1)
    mu2 = sum(r.mu for r in team2)
    mu_tot = mu1 + mu2
    sig1 = sum(r.sigma for r in team1)
    sig2 = sum(r.sigma for r in team2)
    sigtot = sig1 + sig2

    print(team1, team2)

    diff = abs(mu1 - mu2)
    percent = 50 + diff/mu_tot*100

    if percent > 100:
        percent = 100

    if mu1 > mu2:
        string = "{} win at {:.2f}% - {:.2f} to {:.2f}".format(names1, percent, mu1, mu2 )
    else:
        string = "{} win at {:.2f}% - {:.2f} to {:.2f}".format(names2, percent, mu2, mu1 )
    
    return string

def getRankListLength(revalidateRanks=False):
    '''Get the total number of entries in the ranking'''

    global playerRankList
    updatePlayerRanks(revalidateRanks)
    return len(playerRankList)

def getRankRange(start, end, revalidateRanks=False):
    '''Returns a list of player, optionally flushing the ranks-cache first'''

    global playerRankList
    
    print(start,end)
    updatePlayerRanks(revalidateRanks)
    
    if start > len(playerRankList) or start >= end:
        return []
    return playerRankList[start:end]

def rankHasChanged(time):
    '''Indicates to a http-querier if the availiable data has changed'''

    if last_rank_update > time:
        return "True"
    else:
        return "False"

def debugInformation():
    '''Dump a string of debugging information (this may take some times)'''

    return [ "{} {} {}".format(p.steamid, p.name, p.rating) for p in known_players.values() ]
