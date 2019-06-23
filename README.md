## What is "Skillbird" ?
Skillbird is a framework around the python-Trueskill library, which can parse files of versus games to calculate a rating, matchmaking suggestions for future games or create predictions for the outcome of a game with certain team compositions.

## Web Interface
The [Open-web-leaderboard](https://github.com/FAUSheppy/open-web-leaderboard) can be used for visualization. If you leave all settings at default, it should work out of the box.

![open-web-leaderboard](https://media.atlantishq.de/leaderboard-github-picture.png)


## Adaption for your own Data
### Data Requirements
To work correctly you data must have the following fields:
- unique player id or name
- player(s) in winning and losing team

You may also have the following informations:
- data/time of the game (you cannot use the cached-rebuild feature without this)
- time players spent playing compared to the full length of the game
- teamchanges of players
- different maps

### Data Input
If you use the official source-plugin and it's output, you don't have to do anything. Alternatively can write your own parser (see the skillbird-examples project), or you can conform to the Source-format which supports the following log-lines. None of the input values may contain any of the separators used (**pipe** and **comma**) or the line identifier (**0x42**).

    # reset state
    0x42,plugin_unloaded
    
    # declare the current map
    0x42,mapname,MAP_NAME
    
    # start a round
    0x42,round_start_active,PLAYER_ID|PLAYER_NAME|TEAMI_D,PLAYER_ID....
    
    # record team changes (ct) or disconnects (dc) and the team composition after it
    # the backend will handle those accordingly
    0x42,ct,PLAYER_ID|PLAYER_NAME|TEAMI_D,PLAYER_ID....
    0x42,dc,PLAYER_ID|PLAYER_NAME|TEAMI_D,PLAYER_ID....

    # declare the team-composition at the end of the round
    # the backend will use this information for sanity checks
    0x42,round_end_active,PLAYER_ID|PLAYER_NAME|TEAMI_D,PLAYER_ID....
    
    # name the winning team  and end the round
    0x42,winner,WINNING_TEAM_ID

## Usage
    usage: startInsurgency.py [-h] [--parse-only] [--start-at-end] [--no-follow]
                              [--one-thread] [--cache-file CACHEFILE]
                              FILE [FILE ...]
    
    positional arguments:
      FILE                  one or more logfiles to parse
    
    optional arguments:
      -h, --help            show this help message and exit
      --parse-only, -po     only parse, do not listen for queries
      --start-at-end, -se   start at the end of each file (overwrites no-follow)
      --no-follow, -nf      wait for changes on the files (does not imply start-
                            at-end)
      --one-thread          run everything in main thread (implies no-follow)
      --cache-file CACHEFILE
                            A cache file which makes restarting the system fast

## Query Options
Skillbird has a TCP-Query interface which supports the following queries. The separator for player-IDs is always a**comma** and the separator for for teams is always a **pipe** as before, those special characters may not be contained in any of the actual input values. A HTTP-api is work in progress (at the start of this project the interface was only intended for sourcemodplugins).

### Quality
Get the balance quality of the current team composition.

    Input:  quality,LIST_OF_PLAYERS_TEAM_1|LIST_OF_PLAYERS_TEAM_2
    Output: float between 0 and 100

### Balance
Return a balance suggestion for a list of players.
    
    Input:  quality,LIST_OF_PLAYER_IDs
    Output: string LIST_OF_PLAYERS_TEAM_1|LIST_OF_PLAYERS_TEAM_2

### Player
Return rating information about a player-ID

    Input:  quality,PLAYER_ID
    Output: string: rating information
   

### Find
Fuzzy search for the name or ID of a player

    Input: find,string
    Output: string: rating information

### Force rank reload
For the reload of player ranks, which are usually updated every 5 minutes immediately.

    Input: forceRankReload
    Output: string: "OK" (if successful)

### Dump
Reload the player ranks cache and dump the entire contents.

    Input: dump
    Output: string: all players, their ratings and their ranks

### Stats
Return some statistics about the system

    Input: stats
    Output: string: general information

## Related projects
- [skillbird-sourcemod](https://github.com/FAUSheppy/skillbird-sourcemod) Sourcemod plugin that produces the necessary output for Source-based servers.
- [open-web-leaderboard](https://github.com/FAUSheppy/open-web-leaderboard)
