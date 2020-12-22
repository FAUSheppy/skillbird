#!/usr/bin/python3

import backends.database as db
import backends.trueskillWrapper as ts
import backends.entities.Players as players
import backends.eventStream
import Round
import json
import flask
import os
import sys
import datetime as dt

app     = flask.Flask("skillbird")

def run(port, parser):
    app.run(port=port)

## SERVER QUERIES ###
@app.route('/health')
def health():
    try:
        count, avgPred = db.check()
        return ("Rounds: {}, PredQuality: (lower than 0.5 is good): {}".format(count, avgPred), 200)
    except AssertionError as e:
        return ("{}".format(e), 500)

@app.route('/get-player-rating-msg')
def getPlayer():
    playerId = flask.request.args.get("id")
    p = db.getPlayer(playerId)
    if not p:
        return ("Player not found", 404)
    return "{}'s Rating: {} (Rank {})".format(p.name, int(p.rating.mu - 2*p.rating.sigma), db.getPlayerRank(p))

@app.route('/get-outcome-prediction', methods=["POST"])
def getOutcomePrediction():
    '''Make a prediction based tww submitted teams of players'''

    teamA = filter(lambda x: x["team"] % 2 == 0, flask.request.json["players"])
    teamB = filter(lambda x: x["team"] % 2 == 1, flask.request.json["players"])


    playersA = [ db.getOrCreatePlayer(players.playerInRoundFromJson(pJson)) for pJson in teamA ]
    playersB = [ db.getOrCreatePlayer(players.playerInRoundFromJson(pJson)) for pJson in teamB ]

    prediction, confidence = ts.predictOutcome(playersA, playersB)
    quality = 1-abs(0.5-confidence)
    balanceSuggestion, qualityOfSuggestion = ts.balance(playersA+playersB)

    retData = dict()
    retData.update( { "action"     : "balance"  } )
    retData.update( { "quality"    : quality    } )
    retData.update( { "prediction" : prediction } )
    retData.update( { "prediction-confidence" : confidence } )

    balanceSuggestionJson = { 
                              "teamA" : [ json.loads(p.toJson()) for p in balanceSuggestion[0] ],
                              "teamB" : [ json.loads(p.toJson()) for p in balanceSuggestion[1] ]
                            }

    retData.update( { "teamA-orig" : [ json.loads(p.toJson()) for p in playersA ] })
    retData.update( { "teamB-orig" : [ json.loads(p.toJson()) for p in playersB ] })

    retData.update( { "qualityOfSuggestion" : qualityOfSuggestion } )
    retData.update( { "balanceSuggestion" : balanceSuggestionJson } )

    return flask.json.jsonify(retData)


################# DataSubmission #######################
@app.route('/submitt-round', methods=["POST"])
def jsonRound():
    '''Submitt a full Round in the form a json directory as described in the documentation'''
    evaluateRound(Round.fromJson(flask.request.json))
    
    return ("", 204)

@app.route('/single-event', methods=["POST"])
def singleEvent():
    '''Location for submitting single events with a session id, such an event stream must be terminated
        with an "round_end" event'''

    # get and check request parameters #
    jsonDict = flask.request.json
    session = flask.request.args.get("session")
    if not session:
        return ("Bad session ID", 500)

    # define local names #
    ROUND_END_IDENT     = "round_end"
    PATH_BASE           = "data/"
    SESSION_FILE_FORMAT = "{}-session-events.txt"
    sesionFile = SESSION_FILE_FORMAT.format(session)
    fullPath   = os.path.join(PATH_BASE, sesionFile)

    # if there is a local session check it's age first and delete it if it is too old #
    if os.path.isfile(fullPath):
        fileLastModified = dt.datetime.fromtimestamp(os.path.getmtime(fullPath))
        maxAge = dt.timedelta(minutes=30)
        if dt.datetime.now() - fileLastModified > maxAge:
            print("Removed orphaned session file: {}".format(fullPath), file=sys.stderr)
            os.remove(fullPath)

    # update live stats #
    if jsonDict["etype"] == "active_players":
        db.logLiveState(jsonDict, session)

    if jsonDict["etype"] == ROUND_END_IDENT:
        events = []
        with open(fullPath, "r") as f:
            for l in f:
                events += [json.loads(l)]
        os.remove(fullPath)
        matchRound = backends.eventStream.parse(events)
        evaluateRound(matchRound)
        print(matchRound.toJson())
    else:
        with open(fullPath, "a") as f:
            f.write(json.dumps(jsonDict))
            f.write("\n")

    return ("", 204)

        

@app.route('/event-blob', methods=["POST"])
def eventBlob():
    '''Location for submitting full rounds in the form of an event array'''

    matchRound = backends.eventStream.parse(flask.request.json["events"])
    evaluateRound(matchRound)
    return ("", 204)

def evaluateRound(matchRound):
    '''Run a match round throught the backand (includeing persisting it'''

    db.saveRound(matchRound)

    # winners/losers are both dictionaries in the form of { PlayerInDatabase : newRating } #
    winnersRated, losersRated = ts.evaluateRound(matchRound)

    for playerInDatabase in winnersRated.keys():
        playerInDatabase.rating = winnersRated[playerInDatabase]
    for playerInDatabase in losersRated.keys():
        playerInDatabase.rating = losersRated[playerInDatabase]

    db.saveMultiplePlayersToDatabase(winnersRated.keys(), incrementWins=1, 
                                        timestamp=matchRound.start)
    db.saveMultiplePlayersToDatabase(losersRated.keys(), timestamp=matchRound.start)
