# insurgency specific
import insurgencyEvent  as Event
import StorrageBackend  as SB
import TrueSkillWrapper as TS
from insurgencyEventSeries import EventSeries

# general
import Player
import Round
from datetime import datetime

def is_round_end(line):
    return "0x42,round_end_active" in line
def is_plugin_output(line):
    return "0x42" in line
def is_winner_event(line):
    return "0x42,winner" in line
def get_key(dic,key):
    tmp = list(dic)
    return tmp[tmp.index(key)]

def parse(f, exit_of_eof=True, start_at_end=False):
    last_round_end = None
    seek_start = True
    round_lines = []
    last_line_was_winner = False
    while True:
        old_line_nr = f.tell()
        line = f.readline()
        
        # if no line or incomplete line, sleep and try again #
        if not line:
            if exit_on_eof:
                return
            time.sleep(5000)
            continue
        elif not line.endswith("\n"):
            f.seek(old_line_nr)
            time.sleep(5000)
            continue

                
        if seek_start and not "round_start_active" in line and line:
            continue
        elif "round_start_active" in line:
            seek_start = False
        elif "plugin unloaded" in line:
            round_lines = []
            seek_start = True
            continue

        evalRound = False
        # and line and stop if it was round end #            
        round_lines += [line]
        if last_line_was_winner and not is_round_end(line):
            f.seek(f.tell()-1,0)
            evalRound = True
        elif is_round_end(line):
            last_round_end = line
            evalRound = True
        elif is_winner_event(line):
            last_line_was_winner = True

        # parse and evaluate round #
        if evalRound:
            nextRound = parseRoundFromLines(round_lines)
            round_lines = []
            if nextRound:
                try:
                    TS.evaluate_round(nextRound)
                except Warning as e:
                    pass


def parseRoundFromLines(r):

    # get an event series #
    es = EventSeries()
    for l in r:
        if is_plugin_output(l):
            e = parse_line_to_event(l)
            if e != None:
                es += [e]

    # get players with teams #
    try:
        winners = es.get_winners()
        losers  = es.get_losers()
    except Warning as e:
        TS.dirty_rounds += 1
        return None

    # deal with teamchanges  #
    losers_pop  = []
    winners_pop = []
    for p in winners:
        if p in losers:
            if get_key(losers,p).active_time < get_key(winners,p).active_time:
                get_key(winners,p).active_time -= get_key(losers,p).active_time
                losers_pop += [p]
            else:
                get_key(losers,p).active_time -= get_key(winners,p).active_time
                winners_pop += [p]

    # we cannot change dict during iteration #
    for p in losers_pop:
        losers.pop(p)
    for p in winners_pop:
        winners.pop(p)

    # get ratings if there are any yet #
    SB.sync_from_database(winners)
    SB.sync_from_database(losers)
    
    try:
        es.get_duration()
    except Warning as e:
        TS.dirty_rounds += 1
        return None
    return Round.Round(winners,losers,es.get_map(),es.get_duration(),es.get_starttime())

def create_event(etype,line,timestamp):
    TEAMCHANGE      = ["teamchange"]
    ACTIVE_PLAYERS  = ["ct","dc","round_start_active","round_end_active","tc"]
    DISCONNECT      = ["disconnect"]
    WINNER_INFO     = ["winner"]
    MAP_INFO        = ["mapname"]
    IGNORE          = ["map_start_active","start","plugin unloaded"]
    
    if etype in TEAMCHANGE:
        player   = Player.DummyPlayer(line.split(",")[1])
        old_team = line.split(",")[2]
        return Event.TeamchangeEvent(player,old_team,timestamp,line)
    
    elif etype in ACTIVE_PLAYERS:
        return Event.ActivePlayersEvent(line,timestamp)
    
    elif etype in DISCONNECT:
        player   = Player.DummyPlayer(line.split(",")[1])
        return Event.DisconnectEvent(player,timestamp,line)
    
    elif etype in WINNER_INFO:
        winner_side = line.split(",")[1]
        return Event.WinnerInformationEvent(winner_side,timestamp,line)
    
    elif etype in MAP_INFO:
        return Event.MapInformationEvent(line.split(",")[1],timestamp,line)

    elif etype in IGNORE:
        pass
    
    else:
        raise Exception("Cannot create event from logline. (etype was: '{}')".format(etype))

def parse_line_to_event(l):
    tmp = l.split("0x42,")[1].strip("\n")
    etype = tmp.split(",")[0].split("|")[0]
    try:
        if ": L " in l.split("0x42")[0]:
            timestamp = datetime.strptime(l.split(": L ")[1].split(": [")[0],"%m/%d/%Y - %H:%M:%S")
        else:
            timestamp = datetime.strptime(l.split(": [ints_logging.smx]")[0],"L %m/%d/%Y - %H:%M:%S")
    except ValueError:
        print(" ---- NO TIME ----  | WARNING: Failed to parse time for event, SKIP")
        return None

    event = create_event(etype,tmp,timestamp)
    SB.save_event(event);
    return event
