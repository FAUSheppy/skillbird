#!/usr/bin/python3
import sys
import NetworkParser
import FileReader
import argparse

parser = argparse.ArgumentParser(description='Insurgency rating python backend server')
parser.add_argument('files', metavar='FILE', type=str, nargs='+',\
                help='one or more logfiles to parse')
parser.add_argument('--parse-only','-po',dest='parse_only', action='store_const',\
                const=True, default=False,help="only parse, do not listen for queries")
parser.add_argument('--start-at-end','-se',dest='start_at_end', action='store_const',\
                const=True, default=False,help="start at the end of each file (implies follow)")
parser.add_argument('--no-follow','-nf',dest='nofollow', action='store_const',\
                const=True, default=False,help="wait for changes on the files (does not imply start-at-end)")

if __name__ == "__main__":
        args = parser.parse_args()
        FileReader.readfiles( args.files ,\
                                args.start_at_end,\
                                args.nofollow,
                               )
        if not args.parse_only:
            Query.listen()
        else:
            sys.exit(0)
