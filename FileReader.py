import TrueSkillWrapper as TS
import time
import threading
import insurgencyParsing as iparse

def readfile(filename, start_at_end, exit_on_eof, parsingBackend, cpus=1):

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

def readfiles(filenames, start_at_end=False, nofollow=False,parsingBackend=iparse, oneThread=False):
        for f in filenames:
            if oneThread:
                readfile(f, start_at_end, nofollow, parsingBackend)
            else:
                threading.Thread(target=readfile,args=\
                            (f, start_at_end, nofollow, parsingBackend,)).start()
