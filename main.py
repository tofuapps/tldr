#!/usr/bin/python3
from fetcher.fetcher import Fetcher
from curator.curator import Curator
from summarizer.summarizer import Summarizer

import json
import sys
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AI Backend for News Reader.')
    #parser.add_argument('integers', metavar='N', type=int, nargs='+',
    #                    help='an integer for the accumulator')
    #parser.add_argument('--sum', dest='accumulate', action='store_const',
    #                    const=sum, default=max,
    #                    help='sum the integers (default: find the max)')
    #args = parser.parse_args()
    #print(args.accumulate(args.integers))

    #parser.add_argument('--verbosity', dest)
    parser.add_argument('-b', '--body', action='store_true',
                        help="Body of article")
    parser.add_argument('-t', '--title', action='store_true',
                        help="Title of article")
    parser.add_argument('--summarise', action='store_true',
                        help='Outputs summary of given article')
    parser.add_argument('--curate', action='store_true',
                        help='Outputs list of curated articles')
    args = parser.parse_args()

    print(args)

    #fetcher = Fetcher()
    #curator = Curator()
    ##summarizer = Summarizer()

    #articles = fetcher.fetch()
    #result = curator.curate(articles)

    #with open('curated_articles.out', 'w') as output:
    #    output.writelines(json.dumps(result, sort_keys=True, indent=4))

    #print(json.dumps(result, sort_keys=True))
    #sys.stdout.flush()
