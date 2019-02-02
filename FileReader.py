import TrueSkillWrapper as TS
import time
import threading
import insurgencyParsing as iparse

def readfile(filename, start_at_end=True, exit_on_eof=False, parsingBackend=iparse, cpus=1):

    f = open(filename)
    if start_at_end:
        f.seek(0,2)
    
    try:
        if cpus > 1:
            raise NotImplementedError("Multiprocessing not implemeted yet")
        else:
            if callable(parsingBackend):
                parsingBackend(f, exit_on_eof, start_at_end)
            else:
                parsingBackend.parse(f, exit_on_eof, start_at_end)
    except TypeError:
        raise RuntimeError("parsingBackend musst be callable or have .parse() callable")
    
    f.close()

def readfiles(filenames, start_at_end=True, nofollow=False, parsingBackend=iparse ):
        for f in filenames:
            threading.Thread(target=readfile,args=\
                            (f, start_at_end, nofollow, parsingBackend)).start()
