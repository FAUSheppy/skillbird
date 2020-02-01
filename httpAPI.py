#!/usr/bin/python3
import StorrageBackend as SB
import flask


app = flask.Flask("skillbird")

################## HTML HELPER ########################
def invalidParameters(*args):
    return "500 - Invalid {}".format(args)

########################################################

@app.route('/dumpdebug')
def dumpDebug():
    return "<br>".join(SB.debugInformation())

@app.route('/getplayer')
def getPlayer():
    playerName = flask.request.args.get("name")
    return str(SB.searchPlayerByName(playerName))

@app.route('/getmaxentries')
def getMaxEntries():
    return str(SB.getRankListLength())

@app.route('/rankrange')
def getRankRange():
    try:
        start = int(flask.request.args.get("start"))
        end   = int(flask.request.args.get("end"))
        if end - start <= 0 or end - start > 100:
            raise ValueError()
    except ValueError:
        return invalidParameters(start, end)

    players = SB.getRankRange(start, end)
    return "\n".join([p.serialize() for p in players])

@app.route('/haschanged')
def hasChanged():
    string = flask.request.args.get("time")
    # TODO get time with timezone
    return SB.rankHasChanged(localizedTime)

@app.route('/getbalancedteams')
def getBalancedTeams():
    players = flask.request.args.get("players").split(",")
    useNames = flask.request.args.get("names")
    return SB.getBalancedTeams(players, useNames=bool(useNames))

@app.route('/quality')
def quality():
    '''Get a game quality estimate for two or more given teams'''
    string = flask.request.args.get("playerswithteams")
    useNames = flask.request.args.get("names")
    teams = string.split("|")
    if len(teams) < 2:
        flask.abort("Invalid input string: {}".format(string))
    teams = [ x.split(",") for x in teams ]
    return SB.qualityForTeams(teams, useNames=bool(useNames))
