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

def getPlayerRank(player):
    '''Get a players current rank, seperate function because this query is relatively expensive'''

    conn = sqlite3.connect("players.sqlite")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) from players where (mu-2*sigma) > (?-2*?);", 
                        (player.rating.mu, player.rating.sigma))
    rank = cursor.fetchone()[0]
    conn.close()
    return rank

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
