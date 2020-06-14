#!/usr/bin/python3
import sys
import argparse
import httpAPI

#import backends.genericFFA
import backends.eventStream

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Insurgency rating python backend server')

    ### parser backend configuration ###
    parser.add_argument('--parser-backend', required=True, choices=['ffa', 'eventStream'],
                            help="Use the free-for-all parser")
   
    ### readin configuration ###
    parser.add_argument('--http-api-port', type=int, default=5000, help="HTTP API Port")

    args = parser.parse_args()

    ### set parser ###
    if args.parser_backend == "ffa":
        #parser = backends.genericFFA
        raise NotImplementedError()
    elif args.parser_backend == "eventStream":
        parser = backends.eventStream
    else:
        print("Unsupported parser: {}".format(args.parser_backend), file=sys.stderr)
        sys.exit(1)

    ### set input mode ###
    httpAPI.run(args.http_api_port, parser)
