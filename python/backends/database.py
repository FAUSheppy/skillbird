import sqlite3
import json
import datetime as dt
import backends.entities.Players as Players
import backends.trueskillWrapper as trueskill

# setup
# create TABLE players (id TEXT PRIMARY KEY, name TEXT, lastgame TEXT, wins INTEGER, mu REAL, sigma REAL, game INTEGER);
# create TABLE rounds (timestamp TEXT PRIMARY KEY, winners BLOB, losers BLOB, winnerSide INTEGER, map TEXT, duration INTEGER, prediction REAL, confidence REAL)
# create TABLE playerHistoricalData (id TEXT, timestamp TEXT, mu REAL, sima REAL)

DATABASE = "players.sqlite"
DATABASE_ROUNDS = "rounds.sqlite"

def check():
    conn = sqlite3.connect(DATABASE)
    conn.close()
    conn = sqlite3.connect(DATABASE_ROUNDS)
    cursor = conn.cursor()
    backlog = dt.datetime.now() - dt.timedelta(days=7)
    query = "SELECT avg(prediction) FROM rounds WHERE timestamp > ? AND confidence > 0.6 \
                    ORDER BY timestamp DESC;"
    cursor.execute(query, (backlog.timestamp(),))
    avgPred = cursor.fetchone()[0]
    query = "SELECT count(*) FROM rounds WHERE timestamp > ? AND confidence > 0.6 \
                    ORDER BY timestamp DESC;"
    cursor.execute(query, (backlog.timestamp(),))
    count = cursor.fetchone()[0]
    conn.close()

    if count < 10:
        raise AssertionError("Game count last 7 days low ({})".format(count))
    elif avgPred > 0.5:
        raise AssertionError("Average Prediction very bad ({})".format(avgPred))
    else:
        return (count, avgPred)

def logHistoricalData(player, timestamp):
    if not timestamp:
        return
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO playerHistoricalData VALUES (?,?,?,?)", (
                            player.id,
                            timestamp.timestamp(),
                            player.rating.mu,
                            player.rating.sigma))
    conn.commit()
    conn.close()



def saveRound(r):
    conn = sqlite3.connect(DATABASE_ROUNDS)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO rounds VALUES (?,?,?,?,?,?,?,?)", (r.start.timestamp(),
                                    json.dumps([ p.toJson() for p in r.winners ]),
                                    json.dumps([ p.toJson() for p in r.losers ]),
                                    r.winnerSide, r.map, r.duration.total_seconds(), 
                                    r.prediction, r.confidence))

    conn.commit()
    conn.close()


def getPlayer(playerId):
    conn = sqlite3.connect("players.sqlite")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM players WHERE id = ?", (playerId,))
        rows = cursor.fetchall()
        if len(rows) < 1:
            return None
        else:
            playerId, playerName, lastGame, wins, mu, sigma, games = rows[0]

            return Players.PlayerInDatabase(playerId, playerName, 
                                                trueskill.newRating(mu=mu, sigma=sigma), wins, games)
    finally:
        conn.close()

def getPlayerRank(player):
    '''Get a players current rank, seperate function because this query is relatively expensive'''

    conn = sqlite3.connect("players.sqlite")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) from players where (mu-2*sigma) > (?-2*?);", 
                        (player.rating.mu, player.rating.sigma))
    rank = cursor.fetchone()[0]
    conn.close()
    return rank

def getOrCreatePlayer(player, timestamp=None):
    playerInDb = getPlayer(player.id)
    if not playerInDb:
        return savePlayerToDatabase(player, timestamp=timestamp)
    else:
        return playerInDb


def getMultiplePlayers(playerIdList):
    return [ getPlayer(p) for p in playerIdList ]

def savePlayerToDatabase(player, incrementWins=0, timestamp=None):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if not player.rating:
        player.rating = trueskill.newRating()
    playerFromDatabase = getPlayer(player.id)
    if playerFromDatabase:
        cursor.execute('''UPDATE players SET id   = ?,
                                           name  = ?,
                                           lastgame = ?,
                                           wins  = ?,
                                           mu    = ?,
                                           sigma = ?,
                                           games = ? 
                                           WHERE id = ?''', 
                        (player.id, player.name, timestamp.timestamp(),
                            playerFromDatabase.wins + incrementWins, 
                            player.rating.mu, player.rating.sigma, playerFromDatabase.games + 1,
                            player.id))
    else:
        cursor.execute("INSERT INTO players VALUES (?,?,?,?,?,?,?)", 
                        (player.id, player.name, timestamp.timestamp(), 0, 
                            player.rating.mu, player.rating.sigma, 0))
    conn.commit()
    conn.close()
    playerDone = getPlayer(player.id)

    logHistoricalData(playerDone, timestamp)
    return playerDone

def saveMultiplePlayersToDatabase(playerList, incrementWins=0, timestamp=None):
    for p in playerList:
        savePlayerToDatabase(p, incrementWins, timestamp=timestamp)

def getBuddyGraphs(players):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    graphs = dict()

    for p in players:
        rows = []# cursor.execute("SELECT buddy from buddies where playerId = ?;", (p.id,))
        buddies = [ r[0] for r in rows ]
        for b in buddies:
            if b in players:
                pass

    conn.close()

