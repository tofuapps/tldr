#!/usr/bin/python3
import json
import requests
import feedparser
import utils.utils as utils
import newspaper

class Fetcher:
    feeds = [
        'https://www.channelnewsasia.com/rssfeeds/8395986',
        'http://feeds.bbci.co.uk/news/rss.xml',
        'https://www.straitstimes.com/news/world/rss.xml'
        #'https://news.google.com/rss/'
    ]

    """ Supplies the news articles """
    def __init__(self):
        pass

    def fetch(self, urls=None, debug=False):
        """"Fetches list of news from a list of rss feeds and returns the raw result."""
        if urls is None:
            urls = Fetcher.feeds

        if isinstance(urls, str):
            urls = [urls]

        res = []
        for url in urls:
            feed = feedparser.parse(url)

            if debug:
                entry = feed.entries[1]
                print(entry.keys())
                print(entry.title)
                print(entry)

            res += feed.entries

        res.sort(key=lambda x: x.published_parsed, reverse=True)
        return res



    def simple_fetch(self, url=None):
        """
        Fetches list of news from an rss feed, and returns it in a simplified form with basic types.

        An array of news in the form of dictionaries with keys:
           - link (string)
           - title (plain text string)
           - published_on (time struct)
           - short_summary (plain text string)
        are returned.
        """
        data = self.fetch(url)

        final_data = list(map(lambda entry: \
                              {
                                  "url": entry.links[0].href,
                                  "title": entry.title,
                                  "published_on": entry.published_parsed,
                                  "short_summary": (None if not "summary" in entry else utils.clean_html(entry.summary))
                              },
                              data))

        return final_data


    def retrieve_article_contents(self, url):
        """Retrieves the text contents of a url pointing to an article. Does not include the title of the article."""

        response = requests.get(url)

        if 200 <= response.status_code < 300:
            return newspaper.fulltext(response.text)
            #return utils.clean_html(response.content, tag="article")

        #There's a problem.
        #TODO: throw an error instead.
        return "Error " + str(response.status_code)

if __name__ == '__main__':
    fetcher = Fetcher()
