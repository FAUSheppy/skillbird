#!/usr/bin/python3
import sys
import NetworkParser
import FileReader
import argparse
import StorrageBackend
import NetworkListener
import httpAPI

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
parser.add_argument('--cache-file', dest='cacheFile',\
                help="A cache file which makes restarting the system fast")

if __name__ == "__main__":
        args = parser.parse_args()
        if args.cacheFile:
            open(args.cacheFile, "a").close()
        FileReader.readfiles( args.files ,\
                              start_at_end=args.start_at_end,\
                              nofollow=args.nofollow, \
                              oneThread=args.oneThread, \
                              cacheFile=args.cacheFile)
        if not args.parse_only:
            print("Starting network-listener")
            httpAPI.app.run()
            NetworkListener.listen()
        else:
            sys.exit(0)
