import socket
import TrueSkillWrapper as TS
import Player
import StorrageBackend as SB
from threading import Thread
import PSQL

TCP_IP      = '127.0.0.1'
TCP_PORT    = 7051
BUFFER_SIZE = 1024

def listen():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(5)
    while True:
        conn, addr = s.accept()
        Thread(target=t_listen_wrapper,args=(conn,)).start()

def t_listen_wrapper(conn):
        try:
            t_listen(conn)
        except RuntimeError as e:
            conn.send(b'503 (Database not in sync)')
        finally:
            conn.close()


def t_listen(conn):
        no_log_in_console = False

        data = conn.recv(BUFFER_SIZE)
        data = str(data,'utf-8')
        data,ident = get_event_ident(data)
        tmp = ''


        if data.startswith("quality,"):
            t1, t2 = parse_teams(data.lstrip("quality,"))
            tmp  = TS.quality(t1.values(),t2.values(),t1.keys(), t2.keys())
        elif data.startswith("balance,"):
            s    = data.lstrip("balance,")
            tmp  = TS.balance(parse_players(s), get_buddies(s))
        elif data.startswith("balancelol,"):
            s    = data.lstrip("balancelol,")
            tmp  = TS.balance(parse_players(s,lol=True), get_buddies(s))
        elif data.startswith("player,"):
            # legacy format support
            p = Player.DummyPlayer(data.lstrip("player,").rstrip("\n"))
            tmp = TS.get_player_rating(p)
        elif data.startswith("playerinfo,"):
            tag, sid, name = data.split(",")
            tmp = "RATING_SINGLE," + TS.get_player_rating_rich(sid, name)
        elif data.startswith("find,"):
            tmp = find_player(data.rstrip("\n").lstrip("find,"))
        elif data.startswith("buddies,"):
            tmp = str(get_buddies())
        elif data.startswith("dump"):
            no_log_in_console = True
            topN = 0
            if "," in data:
                topN = int(data.split(",")[1])
            tmp = SB.dump_rating(topN)
        elif data.startswith("stats"):
            tmp = "Clean: {}\nDirty: {}\n".format(TS.clean_rounds,TS.dirty_rounds)
        elif data.startswith("getteam,"):
            tmp = get_team(data.split("getteam,")[1]);
        elif data.startswith("rebuildteam,"):
            tmp = get_rebuild_team(data.split("rebuildteam,")[1]);
        else:
            print("wtf input: "+data)
        if tmp == '':
            return
        ret = str(ident+str(tmp)).encode('utf-8')
        if not no_log_in_console and ret:
            print(ret)

        conn.send(ret)
        conn.close()

def get_event_ident(data):
    if data.startswith("player_connected"):
        return (data.strip("player_connected"),"player_connected")
    else:
        return (data,"")

def get_team(string):

    # variables #
    ret = "BALANCE_SINGLE,{},{}"
    sid = string.split(",")[0]
    rest = string.split(",")[1:]
    team1 = []
    team2 = []

    # parse #
    for pair in rest:
        p = DummyPlayer(pair.split("|")[0]);
        if pair.split("|")[2] == "2":
            team1 += [p]
        else:
            team2 += [p]
    
    # Prevent totally imbalanced teams #
    if len(team1) == 0:
        return ret.format(sid,"2")
    elif len(team2) == 0:
        return ret.format(sid,"3")
    elif len(team1) > len(team2) + 2:
        return ret.format(sid,"2")
    elif len(team1) +2 < len(team2):
        return ret.format(sid,"3")

    # balance #
    if TS.quality(team1 + [p],team2) > TS.quality(team1,team2 + [p]):
        return ret.format(sid,"2")
    else:
        return ret.format(sid,"3")

def get_rebuild_team(string):
    # parse #
    players = []
    teams = ([],[])
    for pair in string.split(","):
        p = DummyPlayer(pair.split("|")[0]);
        players += [p]
    players = list(map(players,lambda p: SB.known_players[p]))
    players = sorted(players,key=lambda x: TS.get_env().expose(x.rating),reverse=True)
    count = 0
    
    # initial #
    while count<len(player):
        teams[count%2] += [players[count]]
        if len(players) % 2 == 1 and count == len(players)-1:
            if TS.quality(teams[0] + [p],teams[1]) > TS.quality(teams[0],teams[1] + [p]):
                teams[0] += [players[count]]
            else:
                teams[1] += [players[count]]

    # iterate #
    count = 0
    while count < min(len(teams[0]),len(teams[1])):
        old_q = TS.quality(teams[0],teams[1])
        p0 = teams[0][count]
        p1 = teams[1][count]
        # basicly if not better, reset #
        if old_q > TS.quality(teams[0].remove(p0)+[p1],teams[1].remove(p1)+[p0]):
            teams[0].remove(p1)
            teams[0] += [p0]
            teams[1].remove(p0)
            teams[1] += [p1]
    ret = "BALANCE_REBUILD,"
    for p in teams[0]:
        ret += str(p.steamid)+"|2,"
    for p in teams[1]:
        ret += str(p.steamid)+"|3,"

    return ret.rstrip(",");

def get_buddies(players):
    # [[p1,p2,p3 ],...]
    already_found = []
    ret = []
    for sid in players:
        p = Player.DummyPlayer(sid)
        if p in already_found:
            continue
        tmp = PSQL.query_buddies(p)
        already_found += tmp
        ret += [tmp]
    return ret

def parse_teams(data):
    # TEAM_1,Team_2
    # TEAM_X = STEAMID|STEAMID,...
    # return ({p1:p1.rating,p2:p2.rating,...},..)
    ret = (dict(),dict())
    team1, team2 = data.split(",")
    team1 = team1.split("|")
    team2 = team2.split("|")
    for sid in team1:
        sid = sid.strip()
        tmp = Player.DummyPlayer(sid, sid)
        if tmp in SB.known_players:
            ret[0].update({SB.known_players[tmp]:Storrage.known_players[tmp].rating})
        else:
            ret[0].update({tmp:TS.new_rating()})
    for sid in team2:
        sid = sid.strip()
        tmp = Player.DummyPlayer(sid, sid)
        if tmp in SB.known_players:
            ret[1].update({SB.known_players[tmp]:Storrage.known_players[tmp].rating})
        else:
            ret[1].update({tmp:TS.new_rating()})
    return ret

def parse_players(data, lol=False):
    # p1|p2|p3|...
    ret = []
    players = data.strip("\n").split("|")
    if len(players) == 1 and players[0] == '':
        return None
    players = players_new
    for sid in players:
        if lol:
            tmp = Player.DummyPlayer(str(sid[0]),sid[1])
        else:
            tmp = Player.DummyPlayer(str(sid), str(sid))
        if tmp in SB.known_players:
            ret += [SB.known_players[tmp]]
        else:
            ret += [tmp]
    return ret

def find_player(string):
    if string.isdigit():
        if string in SB.known_players:
            return TS.get_player_rating(string, string)
    else:
       tmp = SB.fuzzy_find_player(string)
       return TS.get_player_rating(tmp)

