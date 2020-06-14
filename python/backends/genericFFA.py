# insurgency specific
import StorrageBackend  as SB
import TrueSkillWrapper as TS

# general
import Player
import time
from   datetime import datetime

def loadCache(cacheFile):
    raise NotImplementedError("This backend does not support caching")

def parse(f, exit_on_eof=True, start_at_end=False, cacheFile=None):
    last_round_end = None
    seek_start = True
    round_lines = []
    last_line_was_winner = False
    lineCount = 0
    startTime = datetime.now()

    while True:
        old_line_nr = f.tell()
        line = f.readline()
        
        # if no line or incomplete line, sleep and try again #
        if not line or not line.strip("\n"):
            if exit_on_eof:
                return
            time.sleep(5000)
            continue
        elif not line.endswith("\n"):
            f.seek(old_line_nr)
            time.sleep(5000)
            continue
    
        players = line.strip("\n").split("|")
        playerObjects = [Player.PlayerForDatabase(pname, pname, TS.newRating()) for pname in players]

        # get ratings if there are any yet #
        SB.sync_from_database(playerObjects)
        TS.rate_ffa(playerObjects)
