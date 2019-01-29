import psycopg2
def save(dname,user,host,password,data):
    conn = psycopg2.connect("dbname={} user={} host={} password={}".format(dname,user,host,password))
    cur = conn.cursor()
    tup = ()
    if type(data) == dict:
        for player in data:
            d = dict()
            d.update("steamid",p.steamid)
            d.update("name",p.name)
            d.update("wins",p.wins)
            d.update("games",p.games)
            d.update("mu",p.rating.mu)
            d.update("sigma",p.rating.sigma)
            tup += (d,)
        cur.executemany("""INSERT INTO ratings(steamid,name,wins,games,mu,sigma) \
                        VALUES (%(steamid)s,%(name)s,%(wins)s,%(games)s,%(mu)s,%(sigma)s)""",d)
    elif isinstance(data,Event):
        cur.exceutemany("""INSERT INTO events(etype,timestamp,line) \
                        VALUES (%(etype)s,%(timestamp)s,%(line)s)""",data)

def query_buddies(steamid):
        return []
