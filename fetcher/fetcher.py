#!/usr/bin/python3
from bs4 import BeautifulSoup, Comment
import requests
import feedparser
import json

class Fetcher:
    """ Supplies the news articles """
    def __init__(self):
        pass

    def fetch(self, url, debug=False):
        """"Fetches list of news from an rss feed and returns the raw result."""
        NewsFeed = feedparser.parse(url)

        if debug:
            print(len(NewsFeed.entries))
            entry = NewsFeed.entries[1]

            print(entry.keys())
            print(entry.title)
            print(entry.summary)
            print(entry)

        return NewsFeed.entries

    def simple_fetch(self, url):
        """
        Fetches list of news from an rss feed, and returns it in a simplified form.

        An array of news in the form of dictionaries with keys: link, title, tags, published_on & provided_summary, are returned.
        """
        data = self.fetch(url)

        final_data = []
        for entry in data:
            final_data.append({"url": entry.id,
                               "title": entry.title,
                               "tags": entry.tags,
                               "published_on": entry.published_parsed,
                               "provided_summary": entry.summary})

        return final_data

    def retrieve_article_contents(self, url):
        """Retrieves the text contents of a url pointing to an article. Does not include the title of the article."""

        response = requests.get(url)

        if 200 <= response.status_code < 300:

            #remove html comments
            soup = BeautifulSoup(response.content, 'html.parser')
            comments = soup.findAll(text=lambda text:isinstance(text, Comment))
            _ = [comment.extract() for comment in comments]
            commentless_content = str(soup)

            #get the article tag
            soup = BeautifulSoup(commentless_content, 'html.parser')
            tags = soup.find_all("article")
            article_raw_content = str(tags[0])

            #parse the article tag
            soup = BeautifulSoup(article_raw_content, 'html.parser')
            contents = soup.find_all(text=True)

            #blacklist for tags
            blacklist = [
                '[document]',
                'noscript',
                'header',
                'html',
                'meta',
                'head',
                'input',
                'script',
                'img',
                'source',
                'style',
                'aside',
                'header',
                'footer',
                'h2',
                'h3',
                'h4',
                'h5',
                'h6',
                'h7'
            ]

            #set offset of search to only search after header tag and before footer tag
            index_start_search = 0
            tag_names = list(map(lambda x: x.parent.name, contents))
            while "header" in tag_names:
                i = tag_names.index("header")
                index_start_search = i
                tag_names[i] = ""
            index_end_search = tag_names.index("footer") if "footer" in tag_names else len(tag_names)

            #start extracting contents into content_str
            content_str = ""
            for item in contents[index_start_search: index_end_search]:
                if item.parent.name not in blacklist and str(item) != "Advertisement":
                    content_str += str(item) + " "

            #clean up newlines
            while True:
                _tmp = content_str.replace("\n\n", "\n").replace("\n ", "\n")
                if content_str == _tmp:
                    break
                content_str = _tmp

            #return contents
            return content_str

        #There's a problem.
        #TODO: throw an error instead.
        return "Error " + str(response.status_code)


if __name__ == '__main__':
    feeds = [ 'https://www.channelnewsasia.com/rssfeeds/8395986' ]
    fetcher = Fetcher()
    for f in feeds:
        results = fetcher.simple_fetch(f)
        print("\n\n--- Article  ---")
        print(json.dumps(results[0], indent=4))
        print("\n\n--- Contents ---")
        print(fetcher.retrieve_article_contents(results[0]["url"]))
        print("\n\n----------------")

