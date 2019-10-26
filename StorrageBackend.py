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

def getBalanceForPlayers(players, buddies=None):
        if not players:
            return ""
        StorrageBackend.sync_from_database(players)
        for p in players:
            print(p, p.rating)
        arr = sorted(players, key=lambda x: x.rating.mu, reverse=True)
        ret=""
        i = 0
        while i < len(arr):
            ret += "{}|{},".format(players[i].name,(i%2)+2)
            i += 1
        return ret

def getPlayer(pid, name="NOTFOUND"):
		return known_player[pid]

def fuzzy_find_player(name):
        return "Not Implemented"

def findPlayer(name):
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
                    playerRankTupel += [(p, player_ranks[p])]
                except KeyError:
                    playerRankTupel += [(p, "N/A")]
        finally:
            TS.unlock()
        return playerRankTupel


def get_player_rank(p):
        global player_ranks
        try:
            return str(player_ranks[p])
        except KeyError:
            return "N/A"

def quality(team1, team2, names1 = [""], names2 = [""]):
    mu1 = sum(r.mu for r in team1)
    mu2 = sum(r.mu for r in team2)
    mu_tot = mu1 + mu2
    sig1 = sum(r.sigma for r in team1)
    sig2 = sum(r.sigma for r in team2)
    sigtot = sig1 + sig2

    names1 = list(map(lambda x: str(x.name), names1))
    names2 = list(map(lambda x: str(x.name), names2))

    diff = abs(mu1 - mu2)
    percent = 50 + diff/mu_tot*100
    if percent > 100:
        percent = 100

    if mu1 > mu2:
        string = "{} win at {:.2f}% - {:.2f} to {:.2f} Uncertainty: {:.2f}%".format(\
                        ",".join(names1), \
                        percent, mu1, mu2, sigtot/diff*100)
    else:
        string = "{} win at {:.2f}% - {:.2f} to {:.2f} Uncertainty: {:.2f}%".format(\
                        ",".join(names2), \
                        percent, mu2, mu1, sigtot/diff*100)
    
    return string

def getRankListLength(revalidateRanks=False):
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

def hasChanged(time):
    '''Indicates to a http-querier if the availiable data has changed'''
    if last_rank_update > time:
        return "True"
    else:
        return "False"
