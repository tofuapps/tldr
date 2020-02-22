#!/usr/bin/python3
import feedparser

class Fetcher:
    """ Supplies the news articles """
    def __init__(self):
        pass

    def fetch(self, url):
        NewsFeed = feedparser.parse(url)
        print(len(NewsFeed.entries))
        entry = NewsFeed.entries[1] # list of entry objects

        #print(entry.keys())
        #print(entry.title)
        #print(entry.summary)
        #print(entry)
        return NewsFeed.entries

    def fetch(self):
        NewsFeed = feedparser.parse('https://www.channelnewsasia.com/rssfeeds/8395986') # ugly temp function for testing
        print(len(NewsFeed.entries))
        entry = NewsFeed.entries[1] # list of entry objects

        #print(entry.keys())
        #print(entry.title)
        #print(entry.summary)
        #print(entry)
        return NewsFeed.entries

if __name__ == '__main__':
    feeds = [ 'https://www.channelnewsasia.com/rssfeeds/8395986' ]
    fetcher = Fetcher()
    for f in feeds:
        print(fetcher.fetch(f))
