#!/usr/bin/python3
from trueskill import TrueSkill, Rating

env = TrueSkill(draw_probability=0, mu=1500, sigma=833, tau=40, backend='mpmath')
env.make_as_global()

#####################################################
################ HANDLE RATING INPUT ################
#####################################################

def evaluateRound(r):

    # do no rate rounds that were too imbalanced #
    if r.pt_difference() >= 2.1 or r.pt_difference() == 0:
        raise ValueError("Teams too imbalanced: {} (zero=inifinity)".format(r.pt_difference()))

    weights = r.normalized_playtimes()
    
    # trueskill need groups = [ { key : rating, ... } , { key : rating, ... } ]
    #                              ---------------         ---------------
    #                              Team 1 (winners)        Team 2 (losers)
    groups=[dict(), dict()]
    for playerInDatabase in r.winners:
        groups[0].update( { playerInDatabase : playerInDatabase.rating } )
    for playerInDatabase in r.losers:
        groups[1].update( { playerInDatabase : playerInDatabase.rating } )
    
    if len(groups[1]) == 0 or len(groups[0]) ==0 :
        raise ValueError("One of the rated Teams was empty")
    
    rated = env.rate(groups, weights=weights)
    return rated

#def rate_ffa(players):
#        '''Takes a list of players in reverse finishing order (meaning best first)
#            perform a truskill evaluation and write it to database'''
#
#        # one player doesnt make sense #
#        if len(players) <= 1:
#            return False
#
#        # create list of dicts for trueskill-library #
#        playerRatingTupelDicts = []
#        for p in players:
#            playerRatingTupelDicts += [{p:p.rating}]
#
#        # generate ranks
#        ranks = [ i for i in range(0, len(playerRatingTupelDicts))]
#
#        # rate and safe to database #
#        rated = env.rate(playerRatingTupelDicts)
#
#        # create sync dict #
#        # first player is handled seperately #
#        allPlayer = dict()
#        for playerRatingDict in rated[1:]:
#            allPlayer.update(playerRatingDict)
#
#        # only first player gets win #
#        StorrageBackend.sync_to_database(rated[0], True)
#        StorrageBackend.sync_to_database(allPlayer, False)
#
#        for p in allPlayer.keys():
#            print(p)

#####################################################
################### LOCK/GETTER ####################
#####################################################

def newRating(mu=None, sigma=None):
    if mu and sigma:
        return Rating(mu=mu, sigma=sigma)
    elif mu:
        return Rating(mu=mu, sigma=env.sigma)
    else:
        return env.create_rating()

def getEnviroment():
    return env

def balance(players, buddies=None):
        raise NotImplementedError()

def get_player_rating(sid, name="NOTFOUND"):
        raise NotImplementedError()
