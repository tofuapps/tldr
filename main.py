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
    parser.add_argument('-b', '--body', action='store',
                        help="Body of article")
    parser.add_argument('-t', '--title', action='store',
                        help="Title of article")
    parser.add_argument('-l', '--link', action='store',
                        help="Link to the article")
    parser.add_argument('-q', '--query', action='store',
                        help="Query to summarise by")
    parser.add_argument('--summarize', action='store_true',
                        help='Outputs summary of given article')
    parser.add_argument('-c', '--cluster', action='store_true',
                        help='On: group by clusters; Off (default): group by topics')
    parser.add_argument('--curate', action='store_true',
                        help='Outputs list of curated articles')
    args = parser.parse_args()

    try:
        fetcher = Fetcher()
        if args.curate:
            curator = Curator()

            articles = fetcher.simple_fetch()
            result = curator.curate(articles, args.cluster)

            with open('curated_articles.out', 'w') as output:
                output.writelines(json.dumps(result, sort_keys=True, indent=4))

            print(json.dumps(result, sort_keys=True))
            sys.stdout.flush()
        elif args.summarize:
            summarizer = Summarizer()
            filled = []
            if args.title is not None and args.link is not None:
                article_contents = fetcher.retrieve_article_contents(args.link)
                fillled.append({
                    'title': args.title, 
                    'passage': article_contents
                })
            else:
                articles = fetcher.simple_fetch()
                for a in articles[:5]:
                    article_contents = fetcher.retrieve_article_contents(a['url'])
                    filled.append({
                        'title': a['title'],
                        'passage': article_contents
                    })
            result = summarizer.summarize(filled, query=args.query)
            print(json.dumps(result, sort_keys=True))
            sys.stdout.flush()

    except Exception as e:
        print('exception: ' + str(e))
        raise e

