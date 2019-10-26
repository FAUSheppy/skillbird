#!/usr/bin/python3
import sys
import NetworkParser
import FileReader
import argparse
import StorrageBackend
import NetworkListener
import httpAPI
from threading import Thread

import backends.genericFFA  as ffaParser
import insurgencyParsing    as iparser

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
parser.add_argument('--ffa', action='store_const', default=False, const=True, \
                help="Use the free-for-all parser")
parser.add_argument('--http-api-port', default=5000, \
                help="Port to use for http-api port")

if __name__ == "__main__":
        args = parser.parse_args()
        if args.cacheFile:
            open(args.cacheFile, "a").close()

        if args.ffa:
            parser = ffaParser
        else:
            parser = iparser

        FileReader.readfiles( args.files ,\
                              start_at_end=args.start_at_end,\
                              nofollow=args.nofollow, \
                              oneThread=args.oneThread, \
                              cacheFile=args.cacheFile, \
                              parsingBackend=parser)

        if not args.parse_only:
            print("Starting network-listener(s)")
            Thread(target=httpAPI.app.run,kwargs={'port':args.http_api_port}).start()
            NetworkListener.listen()
        else:
            sys.exit(0)
