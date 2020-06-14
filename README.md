# What is "Skillbird" ?
Skillbird is a framework around the python-Trueskill library, which can parse files of versus games to calculate a rating, matchmaking suggestions for future games or create predictions for the outcome of a game with certain team compositions.

# Web Interface
The [Open-web-leaderboard](https://github.com/FAUSheppy/open-web-leaderboard) can be used for visualization. If you leave all settings at default, it should work out of the box.

![open-web-leaderboard](https://media.atlantishq.de/leaderboard-github-picture.png)


# Data Transmission
## /event-blob
Your server may collect certain events during a match of two teams and columinatively report them to the server, which will then evalute those event into a single Round. The events must be submitted as a *JSON-list* with *Content-Type application/json* in a field called *"events"*. Event must be dictionary-like *JSON*-objects as described below.

    {
        events : [ { ... }, { ... } ]

    }

### ActivePlayersEvent
This events lists all players currently in the game, it must be fired whenever a new player connects, changes team or disconnects, but may also be fired at any other point. The *NUMERIC_TEAM_IDENTIIER* must be 0 for *no team*, 1 for *observers* or 2/3 respectively for players actually in one of the teams.

    {
        "etype"     : "active_players",
        "timestamp" : ISO_TIMESTAMP,
        "players"   : [
                        {
                            "id"    : UNIQUE_PLAYER_ID,
                            "name"  : COLOQUIAL_NAME,
                            "team"  : NUMERIC_TEAM_IDENTIIER
                        }
                        ...
                      ]
    }

### WinnerInformationEvent
Event annotating who won a round. Any single round *MUST* only have one such Event.

    {
        "etype"         : "winner",
        "timestamp"     : ISO_TIMESTAMP,
        "winnerTeam"    : NUMERIC_TEAM_IDENTIIER
    }

### MapInformationEvent
Optional event to annotate the map that was played on. Each individual round must only have one such event.

    {
        "etype"     : "map",
        "timestamp" : ISO_TIMESTAMP,
        "map"       : MAP_NAME
    }

## /submitt-round
Your may transmitt a json dictionary representing an actuall round, this is intended more for backups and manual inputs rather than production use, it basicly skips *backends.eventStream.parse* and goes directly to *backends.trueskill.evaluateRound*.

    {
        "map"         : MAP_STRING_OR_NULL,
        "winner-side" : NUMERIC_TEAM_ID_OR_NULL,
        "winners"     : [ player, player, ... ],
        "losers"      : [ player, player, ..., ],
        "duration"    : DURATION_OF_ROUND_IN_SECONDS,
        "startTime"   : ISO_TIMESTAMP_OR_NULL
    }

The player struct in the winner/loser-array must look like this:

    {
        "playerId"   : PLAYER_ID_STR,
        "playerName" : PLAYER_NAME,
        "isFake"     : BOOLEAN,
        "activeTime" : ACTIVE_TIME_IN_SECONDS,
    }

You cannot ommit the duration/active\_time fields, if you don't need or want to use them set them to *1*. If the winner side is unkown or your game is symetrical (meaning there is no possible advantage for one side or the other, set it to *-1*.

## Related projects
- [skillbird-sourcemod](https://github.com/FAUSheppy/skillbird-sourcemod) Sourcemod plugin that produces the necessary output for Source-based servers.
- [open-web-leaderboard](https://github.com/FAUSheppy/open-web-leaderboard)
