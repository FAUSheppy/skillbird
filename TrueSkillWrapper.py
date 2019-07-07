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

#####################################################
################ HANDLE RATING INPUT ################
#####################################################

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


def rate_teams_simple(winner_team, loser_team, weights=None):
        global clean_rounds
        groups = [winner_team] + [loser_team]

        if len(groups[1]) == 0 or len(groups[0]) ==0 :
            print("WARNING: Groups were {} - {} INCOMPLETE, SKIP".format(len(groups[0]),len(groups[1])))
            return False

        rated = env.rate(groups,weights=weights)
        StorrageBackend.sync_to_database(rated[0],True)
        StorrageBackend.sync_to_database(rated[1],False)
        clean_rounds += 1
        return True

def rate_ffa(players):
        '''Takes a list of players in reverse finishing order (meaning best first)
            perform a truskill evaluation and write it to database'''

        # one player doesnt make sense #
        if len(players) <= 1:
            return False

        # create list of dicts for trueskill-library #
        playerRatingTupelDicts = []
        for p in players:
            playerRatingTupelDicts += [{p:p.rating}]

        # generate ranks
        ranks = [ i for i in range(0, len(playerRatingTupelDicts))]

        # rate and safe to database #
        rated = env.rate(playerRatingTupelDicts)

        # create sync dict #
        # first player is handled seperately #
        allPlayer = dict()
        for playerRatingDict in rated[1:]:
            allPlayer.update(playerRatingDict)

        # only first player gets win #
        StorrageBackend.sync_to_database(rated[0], True)
        StorrageBackend.sync_to_database(allPlayer, False)

        for p in allPlayer.keys():
            print(p)

#####################################################
################### LOCK/GETTER ####################
#####################################################

def lock():
    updateLock.acquire()

def unlock():
    updateLock.release()

def newRating(mu=None):
    if mu:
        return Rating(mu=mu, sigma=env.sigma)
    return env.create_rating()

def getEnviroment():
    return env


def balance(players, buddies=None):
        raise NotImplementedError()

def get_player_rating(sid, name="NOTFOUND"):
        raise NotImplementedError()

#####################################################
############### DEBUGGING FUNCTIONS #################
#####################################################

def playerDebug(sid,rated,groups):
        
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
