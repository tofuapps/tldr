#!/usr/bin/python3

import json
import sys
import random

from fetcher.fetcher import Fetcher, Feed
from curator.curator import Curator
from summarizer.summarizer import Summarizer

if __name__ == '__main__':
    print("Initializing...")
    fetcher = Fetcher()
    curator = Curator()
    summarizer = Summarizer()

    # Fetch all articles from rss feeds

    print("\nFetching articles...")
    articles = fetcher.simple_fetch(cached=True)
    print("Articles found: %d" % len(articles))

    # Curation testing

    print("\nCurating articles...")
    curated_articles = curator.curate(articles, False)
    print("Curation complete.")
    print("-- Clusters found: --")
    for group in curated_articles:
        articles = group["articles"]
        for article in articles:
            print(article["title"])
        print("- - - - - - - - - - -")
    print("---------------------\n")

    print("Single article fetching and summarisation...")
    # Functionality testing on a single articles
    for i in range(3):
        print("Testing features on random article...\n")
        article = random.choice(articles)

        print("---    Article Metadata    ---")
        #print(json.dumps(article, indent=4))
        print("Title: " + article["title"])
        print("URL  : " + article["url"])
        print()

        print("---    Article Contents    ---")
        article_info = fetcher.retrieve_article_info(article["url"], cached=True)
        if not article_info["success"]:
            print("ERROR")
            continue

        article_content = article_info["plain_text"]
        print("<Retrieval successful>") #print(article_content)

        print()
        print("---    Article Summary     ---")
        article_summarized_raw = summarizer.summarize([{"title": article["title"], "passage": article_content}])
        print(article_summarized_raw["summary"])
        print()

        print("------------------------------")
