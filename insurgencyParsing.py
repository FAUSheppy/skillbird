from InsurgencyEventSeries import EventSeries
import InsurgencyEvent as Event

def is_round_end(line):
    return "0x42,round_end_active" in line
def is_plugin_output(line):
    return "0x42" in line
def is_winner_event(line):
    return "0x42,winner" in line
def get_key(dic,key):
     tmp = list(dic)
     return tmp[tmp.index(key)]

def parseRoundFromLines(r):

    # get an event series #
    es = Event.EventSeries()
    for l in r:
        if is_plugin_output(l):
            e = Event.parse_line_to_event(l)
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
    Storrage.sync_from_database(winners)
    Storrage.sync_from_database(losers)
    
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
        return TeamchangeEvent(player,old_team,timestamp,line)
    
    elif etype in ACTIVE_PLAYERS:
        return ActivePlayersEvent(line,timestamp)
    
    elif etype in DISCONNECT:
        player   = Player.DummyPlayer(line.split(",")[1])
        return DisconnectEvent(player,timestamp,line)
    
    elif etype in WINNER_INFO:
        winner_side = line.split(",")[1]
        return WinnerInformationEvent(winner_side,timestamp,line)
    
    elif etype in MAP_INFO:
        return MapInformationEvent(line.split(",")[1],timestamp,line)

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
    Storrage.save_event(event);
    return event
