import TrueSkillWrapper as TS
import utils
import time
import threading

def readfile(filename, start_at_end=True, exit_on_eof=False, parsingBackend=None):
    last_round_end  = None
    f = open(filename)
    count = 0
    
    if start_at_end:
        f.seek(0,2)
    
    # outer loop, continue reading rounds #
    while True:
        # reset #
        round_lines = []
        last_line_was_winner = False

        ## try to read in a full round ##
        seek_start = True
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


            # and line and stop if it was round end #            
            round_lines += [line]
            if last_line_was_winner and not parsing.is_round_end(line):
                f.seek(f.tell()-1,0)
                break
            elif parsing.is_round_end(line):
                last_round_end = line
                break
            elif parsing.is_winner_event(line):
                last_line_was_winner = True

        # parse and evaluate round #
        r=parsing.parse_round(round_lines)
        if not r:
            continue
        try:
            TS.evaluate_round(r)
        except Warning as e:
            utils.print_warning(e)
    f.close()

def readfiles(filenames,start_at_end=True,nofollow=False):
        for f in filenames:
            threading.Thread(target=readfile,args=(f,start_at_end,nofollow,)).start()

