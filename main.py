#!/usr/bin/python3
from fetcher.fetcher import Fetcher
from curator.curator import Curator
from summarizer.summarizer import Summarizer

import json
import sys

if __name__ == '__main__':
    fetcher = Fetcher()
    curator = Curator()
    #summarizer = Summarizer()

    articles = fetcher.fetch()
    result = curator.curate(articles)

    with open('curated_articles.out', 'w') as output:
        output.writelines(json.dumps(result, sort_keys=True, indent=4))

    print(json.dumps(result, sort_keys=True))
    sys.stdout.flush()
