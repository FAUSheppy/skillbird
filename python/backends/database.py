import sqlite3
import backends.entities.Players as Players
import backends.trueskillWrapper as trueskill

# setup
# create TABLE players (id TEXT PRIMARY KEY, name TEXT, lastgame TEXT, wins INTEGER, mu REAL, sigma REAL, game INTEGER);

DATABASE = "players.sqlite"

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

def getOrCreatePlayer(player):
    playerInDb = getPlayer(player.id)
    if not playerInDb:
        return savePlayerToDatabase(player)
    else:
        return playerInDb


def getMultiplePlayers(playerIdList):
    return [ getPlayer(p) for p in playerIdList ]

def savePlayerToDatabase(player, incrementWins=0):
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
                        (player.id, player.name, None, playerFromDatabase.wins + incrementWins, 
                            player.rating.mu, player.rating.sigma, playerFromDatabase.games + 1, player.id))
    else:
        cursor.execute("INSERT INTO players VALUES (?,?,?,?,?,?,?)", 
                        (player.id, player.name, None, 0, 
                            player.rating.mu, player.rating.sigma, 0))
    conn.commit()
    conn.close()
    return getPlayer(player.id)

def saveMultiplePlayersToDatabase(playerList, incrementWins=0):
    for p in playerList:
        savePlayerToDatabase(p, incrementWins)

## open leaderboard functions ##
def findPlayerByName(playerName):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    playerNamePrepared = "%{}%".format(playerName.replace("%", "%%"))
    cursor.execute("SELECT * FROM players WHERE name == ?", (playerName,))
    rows = cursor.fetchall()
    playerRow = None
    if len(rows) < 1:
        cursor.execute("SELECT * FROM players WHERE name LIKE ?", (playerNamePrepared,))
        rows = cursor.fetchall()
        if len(rows) < 1:
            return None
        playerRow = rows[0]
    else:
        playerRow = rows[0]
    
    playerId, playerName, lastGame, wins, mu, sigma, games = playerRow
    conn.close() 
    return Players.PlayerInDatabase(playerId, playerName, 
                                            trueskill.newRating(mu=mu, sigma=sigma), wins, games)

def getTotalEntries(playerName):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    playerNamePrepared = "%{}%".format(playerName.replace("%", "%%"))
    cursor.execute("select count(*) from players")
    count =  cursor.fetchone()
    conn.close()
    return count

def getRankRange(start, end):
    pass
