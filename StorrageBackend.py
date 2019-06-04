import Player
import TrueSkillWrapper as TS
from fuzzywuzzy import fuzz
from datetime import datetime, timedelta

known_players = dict()

# care for cpu load #
player_ranks = dict()
last_rank_update = datetime.now()

def _get_known_players():
    return known_players

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
        #print("BKnP: {}".format(p))
        if p in known_players:
            #print("KnP: {}".format(p))
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
    updatePlayerRanks()

#############################################################
##################### Handle Rank Cache #####################
#############################################################

def updatePlayerRanks(force=False):
    global last_rank_update
    global player_ranks

    if force or last_rank_update - datetime.now() > timedelta(seconds=240):
        last_rank_update = datetime.now()
        s = sorted(known_players.values(), key=lambda x: TS.get_env().expose(x.rating),reverse=True)
        now = datetime.now()
        s = filter(lambda p: now - p.lastUpdate < timedelta(days=60), s)
        rank = 1
        for p in s:
            if p in player_ranks:
                player_ranks[p] = rank
            else:
                player_ranks.update({p:rank})
            rank += 1


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

def fuzzy_find_player(name):
        ret = ""
        tup_list = []
        TS.lock()
        try:
            for p in known_players.values():
                sim = fuzz.token_set_ratio(name.lower(),p.name.lower())
                tup_list += [(sim,p)]
        finally:
            TS.unlock()
        tmp = sorted(tup_list, key=lambda x: x[0], reverse=True)
        return list(filter(lambda x: x[0] > 80, tmp))

def get_player_rank(p):
        global player_ranks
        try:
            return str(player_ranks[p])
        except KeyError:
            return "N/A"

                        
def dumpRatings(top=0, forceMeanSort=False, enforceWhitelist=None):
        global known_players
        ret = ""
        updatePlayerRanks(force=True)

        if forceMeanSort:
            sort = sorted(known_players.values(), \
                            key=lambda x: x.rating.mu,reverse=True)
        else:
            sort = sorted(known_players.values(), \
                            key=lambda x: TS.get_env().expose(x.rating),reverse=True)
        if enforceWhitelist:
            sort = list(filter(lambda x: x.name in enforceWhitelist, sort))

        tmp = ["{} {} mean: {} var: {}   WinRatio: {}% ({} Games)".format( \
                        x.get_name().ljust(30), \
                        str(int(TS.get_env().expose(x.rating))).rjust(5), \
                        str(int(x.rating.mu)).rjust(4), \
                        str(int(x.rating.sigma)).rjust(4),x.winratio().rjust(4), \
                        str(x.games).rjust(3)) \
                        for x in sort]
        if top != 0:
            tmp = tmp[:top]
        count = 0
        for s in tmp:
            count += 1
            ret += ("Rank: "+str(count).rjust(4) +" " + s + "\n") 
        return ret
