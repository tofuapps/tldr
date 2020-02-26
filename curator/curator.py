#!/usr/bin/python3
import utils.utils

from fetcher.fetcher import Fetcher
from sklearn.feature_extraction.text import TfidfVectorizer

import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

from sklearn.metrics import silhouette_score

class Curator:

    

    def __init__(self):
        pass


    def curate(self, articles): 
        #return self.cluster(articles)
        return self.classify(articles)


    def classify(self, articles):
        corpus = [ x.summary for x in articles ]

        # number of topics to extract
        n_topics = round(len(articles) ** 0.5 * 0.5) # sqrt(n)/2 is hopefully a good estimate

        from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
        vec = TfidfVectorizer(max_features=5000, stop_words="english", max_df=0.95, min_df=2)
        features = vec.fit_transform(corpus)

        from sklearn.decomposition import NMF
        cls = NMF(n_components=n_topics)#, random_state=random_state)
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
        topic_labels = cls.transform(features).argsort(axis=1)[:,-1]

        # sort articles into buckets
        buckets = []
        for i, topic_vec in enumerate(cls.components_):
            buckets.append({
                'keywords': [feature_names[fid] for fid in topic_vec.argsort()[-1:-n_top_words-1:-1].tolist()],
                'articles': []
            })
        for index, a in enumerate(articles):
            buckets[topic_labels[index]]['articles'].append(a)

        return buckets


    def cluster(self, articles):
        corpus = [ x.summary for x in articles ]
        #print("Corpus: ", corpus)

        # calculate the tfidf document vectors
        tfidf_vectorizer = TfidfVectorizer()
        #tf_idf_vectorizer = TfidfVectorizer(analyzer="word", use_idf=True, smooth_idf=True, ngram_range=(2, 3))
        tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)
        print(tfidf_matrix.toarray())

        # apply kmeans clustering for classfication
        n_clusters = round(len(corpus) ** 0.5 * 0.5)
        print("Generating {} clusters".format(n_clusters))
        clustering_model = KMeans(  # create k-means model with custom config
            n_clusters=n_clusters,
            max_iter=300,
            precompute_distances="auto",
            n_jobs=-1
        )

        document_labels = clustering_model.fit_predict(tfidf_matrix) # array of cluster label by document

        # evaluate the clustering quality -1 is bad, 0 is overlap, 1 is good
        print(silhouette_score(tfidf_matrix, labels=document_labels))
        utils.visualize_tfidf_matrix(tfidf_matrix)



if __name__ == '__main__':
    curator = Curator()
    print(curator.curate())
