#!/usr/bin/python3
import StorrageBackend as SB
import flask


app = flask.Flask("skillbird")

################## HTML HELPER ########################
def _invalidParameters():
    return "500 - Invalid"

########################################################

@app.route('/getplayer')
def getPlayer():
    raise NotImplementedError()

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
        return invalidParameters()

    players = SB.getRankRange(start, end)
    return "\n".join([p.serialize() for p in players])

@app.route('/findplayer')
def findPlayer():
    string = flask.request.args.get("string")
    players = SB.findPlayer(string)
    return "|".join([pt[0].serialize() + "," + str(pt[1]) for pt in players])
