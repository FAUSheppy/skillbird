#!/usr/bin/python3
import sys
import NetworkParser
import FileReader
import argparse
import StorrageBackend

parser = argparse.ArgumentParser(description='Insurgency rating python backend server')
parser.add_argument('files', metavar='FILE', type=str, nargs='+',\
                help='one or more logfiles to parse')
parser.add_argument('--parse-only','-po',dest='parse_only', action='store_const',\
                const=True, default=False,help="only parse, do not listen for queries")
parser.add_argument('--start-at-end','-se',dest='start_at_end', action='store_const',\
                const=True, default=False, \
                help="start at the end of each file (overwrites no-follow)")
parser.add_argument('--no-follow','-nf',dest='nofollow', action='store_const',\
                const=True, default=False, \
                help="wait for changes on the files (does not imply start-at-end)")
parser.add_argument('--one-thread', dest='oneThread', action='store_const',\
                const=True, default=False, \
                help="run everything in main thread (implies no-follow)")
if __name__ == "__main__":
        args = parser.parse_args()
        FileReader.readfiles( args.files ,\
                              start_at_end=args.start_at_end,\
                              nofollow=args.nofollow,
                              oneThread=args.oneThread)
        if args.oneThread:
            for l in StorrageBackend.dumpRatings().split("\n"):
                print(l)
        if not args.parse_only:
            Query.listen()
        else:
            sys.exit(0)
