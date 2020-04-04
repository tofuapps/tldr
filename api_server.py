#!/usr/bin/python3
from flask import Flask, jsonify, request, make_response
from werkzeug.exceptions import HTTPException

from fetcher.fetcher import Fetcher
from curator.curator import Curator
from summarizer.summarizer import Summarizer

import json
import sys
import os.path

import traceback
import time

# initialise all the stuff
fetcher = Fetcher()
curator = Curator()
summarizer = Summarizer()

app = Flask(__name__)

# flask routes
@app.route('/')
def index():
    return "Hello, Home!"

@app.errorhandler(404)
def not_found(error):
    print('[ERROR] Offending request: ', request)
    return make_response(jsonify({'success': False, 'error': 'Not found'}), 404)

@app.errorhandler(Exception)
def handle_error(e):
    tb = traceback.format_exc()
    print('[ERROR] Exception: ', str(e))
    print(tb)
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return jsonify(error=str(e)), code

# api routes
@app.route('/api/v1.0/newsfeed/get', methods=['GET'])
def get_newsfeed():
    articles = fetcher.simple_fetch(cached=useCachedFeed)
    result = curator.curate(articles, use_cluster=False)
    return jsonify(result)

@app.route('/api/v1.0/newsfeed/get_article_summary', methods=['POST'])
def get_article_summary():
    articles = request.get_json()['articles']

    filled = []
    if articles:
        for article in articles:
            if article['url']:
                res = fetcher.retrieve_article_info(article['url'], cached=True)
                article_contents = res['plain_text'] if res['success'] else None
                filled.append({
                    'title': article['title'],
                    'passage': article_contents
                })
    result = summarizer.summarize(filled, query=None)
    #print("[TIMER][{}] TOTAL ELAPSED END".format(time.time()-t00), file=sys.stderr)
    return jsonify(result)

@app.route('/api/v1.0/newsfeed/get_query_summary', methods=['GET'])
def get_query_summary():
    query = request.args.get('query')

    #t00 = time.time()
    #t0 = time.time()
    #print("[TIMER][{}] Starting...".format(time.time()-t0), file=sys.stderr); t0 = time.time();
    filled = []
    articles = fetcher.simple_fetch(cached=useCachedFeed)
    #print("[TIMER][{}] Finished simple_fetch.".format(time.time()-t0), file=sys.stderr)
    for a in articles: # TODO: can we check through all the articles quickly?
        res = fetcher.retrieve_article_info(a['url'], cached=True)
        article_contents = res['plain_text'] if res['success'] else None
        filled.append({
            'title': a['title'],
            'passage': article_contents
        })
        #print("[TIMER][{}] Fetched article {}.".format(time.time()-t0,idx), file=sys.stderr); t0 = time.time()
    result = summarizer.summarize(filled, query=query)
    #print("[TIMER][{}] TOTAL ELAPSED END".format(time.time()-t00), file=sys.stderr)
    print((result))
    return jsonify(result)

def preload_articles_news_feed():
    """preloads first few articles in feed"""
    articles = fetcher.simple_fetch(cached=useCachedFeed)
    for article in articles[0:min(20,len(articles))]:
        fetcher.retrieve_article_info(article['url'], cached=True)


if __name__ == '__main__':
    try:
        print("setting cached feed use from presence of useCachedFeed file")
        useCachedFeed = os.path.isfile("useCachedFeed")
        print(" -- using cached feed? %s" % str(useCachedFeed))
        print("preloading first few articles in feed")
        preload_articles_news_feed()
        print("running api server")
        app.run(host='0.0.0.0',port=8888,debug=True)
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        raise e
