#!/usr/bin/python3
from trueskill import TrueSkill, Rating
import StorrageBackend
import threading
import Player

env = TrueSkill(draw_probability=0, mu=1500, sigma=833, tau=40, backend='mpmath')
env.make_as_global()
updateLock  = threading.RLock()
dirty_rounds = 0
clean_rounds = 0

def evaluate_round(r):
        global clean_rounds
        global dirty_rounds

        updateLock.acquire()
        try:
            if not r:
                dirty_rounds += 1
                return
            if r.pt_difference() >= 2.1 or r.pt_difference() == 0:
                dirty_rounds += 1
                raise Warning("%s | Info: Teams too imbalanced, not rated (1:%.2f)"%(r.start+r.duration,r.pt_difference()))
            weights = r.normalized_playtimes()
            tmp = rate_teams_simple(r.winners,r.losers,weights)
            if not tmp:
                dirty_rounds += 1
                return
        finally:
            updateLock.release()


def rate_teams_simple(winner_team,loser_team,weights):
        global clean_rounds
        groups = [winner_team]+[loser_team]

        if len(groups[1]) == 0 or len(groups[0]) ==0 :
            print("WARNING: Groups were {} - {} INCOMPLETE, SKIP".format(len(groups[0]),len(groups[1])))
            return False
        rated = env.rate(groups,weights=weights)
        Storrage.sync_to_database(rated[0],True)
        Storrage.sync_to_database(rated[1],False)
        clean_rounds += 1
        return True

def quality(team1,team2, names1 = [""], names2 = [""]):
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

def player_debug(sid,rated,groups):
        
        print("winner")
        for key in groups[0]:
            #if key.steamid == sid:
                print(key.name,key.rating)
        print("loser")
        for key in groups[1]:
            #if key.steamid == sid:
                print(key.name,key.rating)

        p = Player.DummyPlayer(sid)
        if p in rated[0]:
            if p in groups[0]:
                print("Before: {}".format(groups[0][p]))
                print("After:  {}".format(rated[0][p]))
            else:
                print("Before: {}".format(groups[1][p]))
                print("After:  {}".format(rated[0][p]))
        if p in rated[1]:
            if p in groups[0]:
                print("Before: {}".format(groups[0][p]))
                print("After:  {}".format(rated[1][p]))
            else:
                print("Before: {}".format(groups[1][p]))
                print("After:  {}".format(rated[1][p]))
        print("\n")
        

def balance(players, buddies=None):
        if not players:
            return ""
        Storrage.sync_from_database(players)
        for p in players:
            print(p, p.rating)
        arr = sorted(players, key=lambda x: x.rating.mu, reverse=True)
        ret=""
        i = 0
        while i < len(arr):
            ret += "{}|{},".format(players[i].name,(i%2)+2)
            i += 1
        return ret

def get_player_rating(p):
        try:
            p = Storrage.known_players[p]
            tmp = int(env.expose(p.rating))
            return "Rating of '{}' : {} ({}% won)".format(p.name,tmp,p.winratio())
        except KeyError:
            return "No Rating (yet)."

def get_player_rating(sid, name):
        try:
            p = Storrage.known_players[sid]
            tmp = int(env.expose(p.rating))
            return "Rating of '{}' : {} (Rank: {})".format(name, tmp, Storrage.get_player_rank(p))
        except KeyError:
            return "Rating of '{}' : No Rating (yet).".format(name)

def lock():
    updateLock.acquire()

def unlock():
    updateLock.release()

def new_rating(mu=None):
    if mu:
        return Rating(mu=mu, sigma=env.sigma)
    return env.create_rating()

def get_env():
    return env

