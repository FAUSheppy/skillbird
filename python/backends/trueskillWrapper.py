#!/usr/bin/python3
import trueskill
import scipy.stats
import math

env = trueskill.TrueSkill(draw_probability=0, mu=1500, sigma=833, tau=40, backend='mpmath')
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
##################### GETTER ########################
#####################################################

def newRating(mu=None, sigma=None):
    if mu and sigma:
        return trueskill.Rating(mu=mu, sigma=sigma)
    elif mu:
        return trueskill.Rating(mu=mu, sigma=env.sigma)
    else:
        return env.create_rating()

def getEnviroment():
    return env

def balance(players, buddies=None):
        raise NotImplementedError()

def predictOutcome(teamA, teamB):
    '''Predict outcome of a game between team a and team b
        returns: (0|1, confidence)'''
   
    ratingsA = [ p.rating for p in teamA ]
    ratingsB = [ p.rating for p in teamB ]
    muTeamA  = sum([ r.mu for r in ratingsA])
    muTeamB  = sum([ r.mu for r in ratingsB])
    sigmaTeamA = sum([ r.sigma for r in ratingsA])
    sigmaTeamB = sum([ r.sigma for r in ratingsB])

    # probabilty that a random point from normDistTeamA is greater
    # than a random point from  normDistB is normA - normB and then the
    # "1 - Cumulative Distribution Function" (cdf) aka the "Survival Function" (sf)
    # of the resulting distribution being greater than zero
    prob = scipy.stats.norm(loc=muTeamA-muTeamB, scale=sigmaTeamB+sigmaTeamA).sf(0)
    if prob >= 0.5:
        return (0, prob)
    elif prob < 0.5:
        return (1, 1-prob)
    else:
        raise ValueError("Probability was NAN, team rating must have been malformed.")

def balance(players):
    sortedByRating = sorted(players, key=lambda p: env.expose(p.rating))
    teamA = []
    teamB = []

    graphs = db.getBuddyGraphs(players)

    for i in range(0, len(players)):
        if i % 2 == 0:
            teamA += [sortedByRating[i]]
        else:
            teamB += [sortedByRating[i]]

    prediction, confidence = predictOutcome(teamA, teamB)
    quality = 1-abs(0.5 - confidence)
    return ((teamA, teamB), quality)
