#!/usr/bin/python3
import utils.utils as utils
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from sklearn.cluster import KMeans
from sklearn.decomposition import NMF

from sklearn.metrics import silhouette_score

class Curator:

    def __init__(self):
        pass


    def curate(self, articles, use_cluster):
        if use_cluster:
            return self.kmeans_cluster(articles)
        else:
            return self.classify_NMF(articles)


    def classify_NMF(self, articles):
        corpus = [ x.get("summary", x.get("short_summary", "")) for x in articles ]
        corpus = [ '' if x is None else x for x in corpus ]

        # number of topics to extract
        n_topics = round(len(articles) ** 0.5 * 0.5) # sqrt(n)/2 is hopefully a good estimate
        #n_topics = 20

        vec = TfidfVectorizer(max_features=5000, stop_words="english", max_df=0.95, min_df=2)
        features = vec.fit_transform(corpus)

        random_state = 42
        cls = NMF(n_components=n_topics, random_state=random_state)
        cls.fit(features)

        # list of unique words found by the vectorizer
        feature_names = vec.get_feature_names()

        # number of most influencing words to display per topic
        n_top_words = 15

        #for i, topic_vec in enumerate(cls.components_):
        #    print(i, end=' ')
        #    # topic_vec.argsort() produces a new array
        #    # in which word_index with the least score is the
        #    # first array element and word_index with highest
        #    # score is the last array element. Then using a
        #    # fancy indexing [-1: -n_top_words-1:-1], we are
        #    # slicing the array from its end in such a way that
        #    # top `n_top_words` word_index with highest scores
        #    # are returned in descending order
        #    for fid in topic_vec.argsort()[-1:-n_top_words-1:-1]:
        #        print(feature_names[fid], end=' ')
        #    print()

        # first transform the text into features using vec
        # then pass it to transform of cls
        # the result will be a matrix of shape [2, 10]
        # then we sort the topic id based on the score using argsort
        # and take the last one (with the highest score) for each row using `[:,-1]` indexing
        #topic_labels = cls.transform(features).argsort(axis=1)[:,-1]
        topic_scores = cls.transform(features)
        #for row in topic_scores:
        #    print(row.max()))
        FIT_VAL = 0.3   # certainty we require before classifying into any topic
        topic_labels = np.apply_along_axis(lambda row: row.argmax() if row[row.argmax()] >= FIT_VAL else -1, 1, topic_scores)   # for each row
        #print(topic_labels)

        # categorise articles into buckets
        buckets = []
        for i, topic_vec in enumerate(cls.components_):
            buckets.append({
                'keywords': [feature_names[fid] for fid in topic_vec.argsort()[-1:-n_top_words-1:-1].tolist()],
                'articles': [],
                'hotness': 0
            })
        for index, a in enumerate(articles):
            current_topic = topic_labels[index]
            if current_topic == -1:
                continue
            a['score'] = topic_scores[index][current_topic]
            buckets[current_topic]['articles'].append(a)

        # remove empty buckets, sort articles within buckets by score and compute bucket score
        for b in buckets:
            l = len(b['articles'])
            if l == 0:
                buckets.remove(b);
            else:
                b['articles'].sort(key=lambda a: a['score'], reverse=True)
                from sklearn.metrics.pairwise import euclidean_distances
                variance = np.sum(euclidean_distances(features, features), axis=1)
                for idx, a in enumerate(b['articles']):
                    a['variance'] = variance[idx]
                b['hotness'] = sum([a['score'] for a in b['articles']])  # TODO: consider length? similarity (ie reposts)?
        buckets.sort(key=lambda b: b['hotness'], reverse=True)

        return buckets


    def kmeans_cluster(self, articles):
        corpus = [ x.summary for x in articles ]
        #print("Corpus: ", corpus)

        # calculate the tfidf document vectors
        #tfidf_vectorizer = TfidfVectorizer()
        tfidf_vectorizer = TfidfVectorizer(max_features=5000, stop_words="english", max_df=0.95, min_df=2)
        #tf_idf_vectorizer = TfidfVectorizer(analyzer="word", use_idf=True, smooth_idf=True, ngram_range=(2, 3))
        tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)
        #print(tfidf_matrix.toarray())

        # apply kmeans clustering for classfication
        n_clusters = round(len(corpus) ** 0.5 * 0.5)
        #n_clusters = 50
        #print("Generating {} clusters".format(n_clusters))
        clustering_model = KMeans(  # create k-means model with custom config
            n_clusters=n_clusters,
            max_iter=300,
            precompute_distances="auto",
            n_jobs=-1
        )

        document_labels = clustering_model.fit_predict(tfidf_matrix) # array of cluster label by document

        # evaluate the clustering quality -1 is bad, 0 is overlap, 1 is good
        print(silhouette_score(tfidf_matrix, labels=document_labels))
        #utils.visualize_tfidf_matrix(tfidf_matrix)
        return document_labels



if __name__ == '__main__':
    from fetcher.fetcher import Fetcher
    fetcher = Fetcher()
    curator = Curator()
    articles = fetcher.simple_fetch();
    print(articles)
    #print(curator.cluster(articles))
    print(curator.curate(articles,False))
