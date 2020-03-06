#!/usr/bin/python3

import json
import sys
import random

from fetcher.fetcher import Fetcher
from curator.curator import Curator
from summarizer.summarizer import Summarizer

if __name__ == '__main__':
    print("Initializing...")
    fetcher = Fetcher()
    curator = Curator()
    summarizer = Summarizer()

    # Fetch all articles from rss feeds

    print("\nFetching articles...")
    articles = fetcher.simple_fetch()
    print("Articles found: %d" % len(articles))

    # Curation testing

    print("\nCurating articles...")
    curated_articles = curator.curate(articles)
    with open('curated_articles.out', 'w') as output:
        output.writelines(json.dumps(curated_articles, sort_keys=True, indent=4))
        print("Curation result dumped in curated_articles.out")


    # Functionality testing on a single article

    print("\n")
    print("Testing features on random article...")
    article = random.choice(articles)

    print("---    Article Metadata    ---")
    print(json.dumps(article, indent=4))
    print("\n")

    print("---    Article Contents    ---")
    article_content = fetcher.retrieve_article_contents(article["url"])
    print(article_content)
    print("\n")

    print("---    Article Summary     ---")
    article_summarized_raw = summarizer.summarize(article["title"], article_content)
    print(article_summarized_raw["summary"])
    print("\n")

    print("------------------------------")
