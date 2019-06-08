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
    pname = flask.request.args.get("name")
    return pname

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
    print(start, end)
    return "|".join([p.serialize() for p in players])

@app.route('/findplayer')
def findPlayer():
    string = flask.request.args.get("string")
    players = SB.fuzzy_find_player(string)
    return "|".join([p.serialize() for p in players])
