import TrueSkillWrapper as TS
import time
import threading
import insurgencyParsing as iparse

DATE_LENGTH = 15

def readfile(filename, start_at_end, exit_on_eof, parsingBackend, startAtTime, cacheFile, cpus=1):

    f = open(filename)
    if start_at_end:
        f.seek(0,2)

    if startAtTime:
        while True:
            line = f.readline()
            try:
                dt = parsingBackend.parseDate(line)
                if not dt:
                    break
                if dt > startAtTime:
                    break
            except IndexError:
                pass
            except ValueError:
                pass
    
    try:
        if cpus > 1:
            raise NotImplementedError("Multiprocessing not implemeted yet")
        else:
            if callable(parsingBackend):
                parsingBackend(f, exit_on_eof, start_at_end, cacheFile)
            else:
                parsingBackend.parse(f, exit_on_eof, start_at_end, cacheFile)
    except TypeError:
        raise RuntimeError("parsingBackend musst be callable or have .parse() callable")
    
    f.close()

def readfiles(filenames, start_at_end, nofollow, oneThread, cacheFile, parsingBackend=iparse):
        if cacheFile:
            startAtTime = parsingBackend.loadCache(cacheFile)
            print(startAtTime)
        else:
            startAtTime = None
        for f in filenames:
            if oneThread:
                readfile(f, start_at_end, nofollow, parsingBackend, startAtTime, cacheFile)
            else:
                threading.Thread(target=readfile,args=\
                            ( f, start_at_end, nofollow, \
                              parsingBackend, startAtTime, cacheFile, )).start()
