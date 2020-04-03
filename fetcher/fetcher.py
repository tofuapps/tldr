#!/usr/bin/python3
import os
import json
import requests
import feedparser
import newspaper
from datetime import datetime
import utils.utils as utils

import traceback

class Feed:
    """ Class for newsfeeds """

    def __init__(self, name, url):
        self.name = name
        self.url = url



class Fetcher:
    """ Supplies the news articles """

    feeds = [
        Feed('CNA', 'https://www.channelnewsasia.com/rssfeeds/8395986'),
        Feed('BBC', 'http://feeds.bbci.co.uk/news/rss.xml'),
        Feed('StraitsTimes', 'https://www.straitstimes.com/news/world/rss.xml')
    ]

    def __init__(self, use_storage_for_cache=True):
        self.use_storage_for_cache = use_storage_for_cache
        self.__cached_simple_fetch = {}
        self.__cached_articles_info = {}
        if use_storage_for_cache:
            self.readCacheFromStorage()

    def fetch(self, srcs=None, debug=False):
        """"Fetches list of news from a list of rss feeds (list of Feed objects) and returns the raw result."""
        if srcs is None:
            srcs = Fetcher.feeds

        if isinstance(srcs, Feed):
            srcs = [srcs]

        res = []
        for src in srcs:
            try:
                feed = feedparser.parse(src.url)
            except:
                continue

            if debug:
                entry = feed.entries[1]
                print(entry.keys())
                print(entry.title)
                print(entry)

            res += feed.entries

        res.sort(key=lambda x: x.published_parsed, reverse=True)
        return res


    def simple_fetch(self, srcs=None, cached=False):
        """
        Fetches list of news from rss feeds (list of Feed objects), and returns it in a simplified form with basic types.

        The results of the rss feed to avoid multiple requests by using the parameter cached=True. The default is False.

        An array of news in the form of dictionaries with keys:
           - url (string)
           - title (plain text string)
           - published_on (time struct)
           - short_summary (plain text string)
        are returned.
        """
        CACHE_KEY = ("URL<%s>" % str(None if not srcs else srcs.url))

        if cached and CACHE_KEY in self.__cached_simple_fetch:
            final_data = self.__cached_simple_fetch[CACHE_KEY]
        else:
            data = self.fetch(srcs)
            final_data = list(map(lambda entry: \
                                  {
                                      "url": entry.links[0].href,
                                      "title": entry.title,
                                      "published_on": entry.published_parsed,
                                      "short_summary": (None if not "summary" in entry else utils.clean_html(entry.summary))
                                  },
                                  data))
            if cached and final_data:
                self.__cached_simple_fetch[CACHE_KEY] = final_data
                if self.use_storage_for_cache:
                    self.saveCacheToStorage()

        return final_data


    def get_url_domain(self, url):
        """Returns url domain if available, otherwise None."""
        try:
            comp = url.split('/')
            if comp[1] == '' and (comp[0] == 'http' or comp[0] == 'https'):
                return url.split('/')[2]
        except IndexError:
            pass


    def retrieve_article_info(self, url, cached=True):
        """
        Retrieves the article raw info from a url in a dictionary.

        This method also returns the cached contents of the url if possible, and can be overriden via the parameter cached=False.

        The dictionary consists of the following keys:
            - text (string)       - if available, otherwise None.
            - plain_text (string) - if available, otherwise key not included
            - status_code (int)   - if available, otherwise key not included
            - success (boolean)
        """
        CACHE_KEY = ("URL<%s>" % str(url))

        if cached and CACHE_KEY in self.__cached_articles_info:
            result = self.__cached_articles_info[CACHE_KEY]
        else:
            try:
                response = requests.get(url)
            except requests.exceptions.RequestException as e:
                return {"text": str(e), "success": False}

            result = {}
            result["text"] = response.text
            result["status_code"] = response.status_code

            if 200 <= response.status_code < 300:
                result["success"] = True
                try:
                    #if 'channelnewsasia' in self.get_url_domain(url):
                    #    result["plain_text"] = ''   # TODO: fix this to load dynamic content
                    #else:
                    result["plain_text"] = newspaper.fulltext(response.text)
                except Exception as e:
                    result["success"] = False

                if cached:
                    self.__cached_articles_info[CACHE_KEY] = result
                    if self.use_storage_for_cache:
                        self.saveCacheToStorage()
            else:
                result["success"] = False

        return result

    def retrieve_article_contents(self, url):
        """DEPRECATED: Retrieves the text contents of a url pointing to an article. """
        data = self.retrieve_article_info(url)
        if not data["success"]:
            return "Error " + str(data["status_code"])
        return data["plain_text"]

    def saveCacheToStorage(self):
        with open('fetcher__cached_simple_fetch.json', 'w') as out:
            out.write(json.dumps(self.__cached_simple_fetch))
        with open('fetcher__cached_articles_info.json', 'w') as out:
            out.write(json.dumps(self.__cached_articles_info))

    def readCacheFromStorage(self):
        if os.path.isfile('fetcher__cached_simple_fetch.json'):
            with open('fetcher__cached_simple_fetch.json', 'r') as file:
                self.__cached_simple_fetch = json.loads(file.read())
        if os.path.isfile('fetcher__cached_articles_info.json'):
            with open('fetcher__cached_articles_info.json', 'r') as file:
                self.__cached_articles_info = json.loads(file.read())


if __name__ == '__main__':
    fetcher = Fetcher()
    #with open('ui/rip.txt', 'r') as f:
    #    content = '\n'.join(f.readlines())
    #    print(content)
    #    print(newspaper.fulltext(content))
