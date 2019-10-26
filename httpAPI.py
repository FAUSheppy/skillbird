#!/usr/bin/python3
import StorrageBackend as SB
import flask


app = flask.Flask("skillbird")

################## HTML HELPER ########################
def invalidParameters(*args):
    return "500 - Invalid {}".format(args)

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
        return invalidParameters(start, end)

    players = SB.getRankRange(start, end)
    return "\n".join([p.serialize() for p in players])

@app.route('/findplayer')
def findPlayer():
    string = flask.request.args.get("string")
    players = SB.findPlayer(string)
    return "|".join([pt[0].serialize() + "," + str(pt[1]) for pt in players])

@app.route('/haschanged')
def hasChanged():
    string = flask.request.args.get("time")
    # TODO get time with timezone
    return SB.hasChanged(localizedTime)
