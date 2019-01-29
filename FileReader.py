import TrueSkillWrapper as TS
import time
import threading

def readfile(filename, start_at_end=True, exit_on_eof=False, parsingBackend=None):

    f = open(filename)
    
    if start_at_end:
        f.seek(0,2)
    
    try:
        if cpus > 1:
            raise NotImplementedError("Multiprocessing not implemeted yet")
        else:
            if callable(parsingBackend):
                parsingBackend(f)
            else:
                parsingBackend.parse(f)
    except TypeError:
        raise RuntimeError("parsingBackend musst be callable or have .parse() callable")
    
    f.close()

def readfiles(filenames, parsingBackend, start_at_end=True, nofollow=False):
        for f in filenames:
            threading.Thread(target=readfile,args=\
                            (f, start_at_end, nofollow, parsingBackend)).start()
