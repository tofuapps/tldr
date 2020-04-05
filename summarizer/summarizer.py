import json
import math
import nltk
import numpy as np
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
#from .query_summarizer import QuerySummarizer

class Summarizer:
    """Summarizes news articles [WIP]"""

    def __init__(self, debug=False):
        self.debug = debug

        #Setup
        self.stopwords = nltk.corpus.stopwords.words('english')
        self.tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
        self.wordnet_lemmatizer = WordNetLemmatizer()

        self.tfidf_vectorizer = TfidfVectorizer(max_df=0.7, stop_words="english")

    def summarize(self, articles: list, query: str = None):
        """
        Returns a summary of the passage based upon the articles given.

        Articles must be formatted in the form {'title': <>, 'passage': <>}

        A dict with the keys 'title' and 'summary' will be returned.
        """

        #type checking
        if not isinstance(articles, list):
            raise ValueError("articles parameter accepts only a 'list' of elements, but '%s' was given" % str(type(articles)))

        for article in articles:
            if not isinstance(article, dict):
                raise ValueError("articles should only contain 'dict' elements, but %s found" % str(type(article)))

        #process query if requested
        if query:
            articles = self.extract_articles_for_query(articles, query)

        #summarize!
        return self.__summarize_all(articles, focus_on=query)

    def extract_articles_for_query(self, articles: list, query: str, use_crisp: bool = False):
        """
        Extracts relevant articles out of a list of articles for the given query
        """
        if use_crisp:
            corpus = [ x['passage'] for x in articles ]
            corpus = [ '' if x is None else x for x in corpus ]

            vec = TfidfVectorizer(max_features=5000, stop_words="english", max_df=0.95, min_df=2)
            features = vec.fit_transform(corpus)

            # list of unique words found by the vectorizer
            feature_names = vec.get_feature_names()

            filtered = []
            query_words = [feature_names.index(x) for x in query.split() if x in feature_names]
            for idx, article in enumerate(articles):
                score = 0
                for w in query_words:
                    score += features[idx,w]
                if score > 0:
                    filtered.append(article)
            return filtered
        else:
            corpus = [ x['passage'] for x in articles ]
            corpus = [ '' if x is None else x for x in corpus ]
            corpus.append(' '.join([query]*3))  # need to bump up its df to >= 2

            vec = TfidfVectorizer(max_features=5000, stop_words="english", max_df=0.95, min_df=2)
            features = vec.fit_transform(corpus)

            filtered = []
            FIT_VAL = 0
            sim = cosine_similarity(features[-1,:],features[:-1,:])
            for idx, article in enumerate(articles):
                #print(sim[0,idx])
                if sim[0,idx] > FIT_VAL:
                    filtered.append(article)
            return filtered

    def __sentence_cos_sim_2d(self, *sentences):
        """
        Calculate sentence cosine similarities from tfdif vectorisation.

        Returns a 2d numpy array of similarities of each sentence to all others.

        Note: if return_value[2,3]==1, it refers to sentences with indices 2 & 3 having a cos sim of 1, i.e. exactly the same.
        """
        tfidf = self.tfidf_vectorizer.fit_transform(sentences)
        pairwise_similarity = tfidf * tfidf.T
        arr = pairwise_similarity.toarray()
        np.fill_diagonal(arr, 1.0) #guarentee that cos sim of a sentence w/ itself is 1.0
        return arr


    def __summarize_all(self, articles: list, title_factor: int = 3, focus_factor: int = 5, separator: str = None, focus_on: str = None, num_sentences: str = None, redundancy_threshold: float = 0.6):
        """
        Returns a summary of all articles, assuming them all to be relevant to each other.

        The first argument accepts a list of articles.
        An article must either be formatted as a dict {'title': <>, 'passage': <>} or a tuple (<title>, <passage>).

        The importance of the title contents in the summary can be adjusted with the title_factor parameter, which defaults to 3.

        The number of sentences in the returned summary can be adjusted with the num_sentences parameter, which defaults to None (auto-determine).

        A dict with the keys 'title', 'summary_sentences' and 'summary' will be returned.
        """

        #stop if empty
        if not articles:
            return {'title': None, 'summary_sentences': [], 'summary': None}

        #type checking to avoid weird errors later
        if not isinstance(articles, list):
            raise ValueError("articles parameter accepts only a 'list' of elements, but '%s' was given" % str(type(articles)))

        for article in articles:
            if not isinstance(article, dict) and not isinstance(article, tuple):
                raise ValueError("articles should only contain 'dict' or 'tuple' elements, but %s found" % str(type(article)))

        #merge all article titles for processing
        title = '\n'.join(list(map(
            lambda article: (article.get('title','') or '') if isinstance(article, dict) else (article[0] or ''),
            articles
        )))

        #tokenize sentencess for each paragraph in each article
        idx_article_start = []
        sentences  = []
        for article in articles:
            passage = (article.get('passage','') or '') if isinstance(article, dict) else (article[1] or '')
            for paragraph in passage.rstrip().split("\n\n"):
                sentences += nltk.sent_tokenize(paragraph)
            idx_article_start.append(len(sentences))

        #stop if empty
        if not sentences:
            return {'title': title, 'summary_sentences': [], 'summary': None}

        #check if number of sentences to return is given
        if not num_sentences:
            # dynamically compute sentence count for summary.
            # uses 10% of content of the average length of the articles, or 5, whichever is larger, then
            # add sentences proportionally w.r.t. article count increase until a max cap of 5 additional sentences.
            num_sentences = max(
                5,
                len(sentences)//len(articles)//10
            ) + min(5, len(articles) - 1)

        if self.debug:
            print("Summarizing: %d/%d of passage" % (num_sentences, len(sentences)))

        #tokenizes words for title and passage
        title_words = [word.lower() for word in self.tokenizer.tokenize(title)]
        focus_words = [word.lower() for word in self.tokenizer.tokenize(focus_on if focus_on else '')]
        words       = [word.lower() for word in self.tokenizer.tokenize(passage)]

        #calculate word use frequency
        word_freq = {}
        for word in words:
            if word in self.stopwords:
                continue
            word = self.wordnet_lemmatizer.lemmatize(word)
            if word in word_freq:
                word_freq[word] += 1
            else:
                word_freq[word] = 1

        #amplify importance of words contained in title
        for word in [self.wordnet_lemmatizer.lemmatize(word) for word in title_words]:
            if word in word_freq:
                word_freq[word] *= title_factor

        #amplify importance of words contained in focus
        for word in [self.wordnet_lemmatizer.lemmatize(word) for word in focus_words]:
            if word in word_freq:
                word_freq[word] *= focus_factor

        #find weighted frequency
        max_freq = max(word_freq.values()) if word_freq else 0
        for word in word_freq:
            word_freq[word] /= max_freq

        #calculate sentence distance for redundancy removal later
        if redundancy_threshold < 1:
            sentence_cos_sim = self.__sentence_cos_sim_2d(*sentences)

        #calculate sentence info - saved in form (sentence, score, group_id)
        # we compute the following:
        #  - score   : the sum of weighted_importance of non-stopwords in the sentence
        #  - group_id: identifier of similar sentences in which the sentence belong to

        sentence_info_list = []
        group_ids = [-1]*len(sentences)
        group_id_count = 0

        for idx, sentence in enumerate(sentences):
            score = 0
            for word in self.tokenizer.tokenize(sentence.lower()):
                word = self.wordnet_lemmatizer.lemmatize(word)
                score += word_freq.get(word, 0)

            if redundancy_threshold < 1:
                #get comparison of this sentence among all others
                cossim = sentence_cos_sim[idx,:]

                #search for close matches in sentences
                idx_cossim, = np.where((cossim >= redundancy_threshold))

                #If the first element to match this sentence is itself, we can create a new group for that
                if idx_cossim[0] == idx:
                    group_id_count += 1

                    for sim_idx in idx_cossim:
                        group_ids[sim_idx] = group_id_count

                elif group_ids[idx] == -1:
                    group_id_count += 1
                    group_ids[idx] = group_id_count
            else:
                group_id_count += 1
                group_ids[idx] = group_id_count

            #add to list
            sentence_info_list.append((sentence, score, group_ids[idx]))

        #sort by sentence scores
        sentence_info_list.sort(key=lambda x: x[1], reverse=True)
        if self.debug:
            print("<id>[score] <sentence>")
            for data in sentence_info_list[0:min(len(sentence_info_list), 20)]:
                print("%6d[%.6f]: %s" % (data[2], data[1], data[0]))

        #use top k sentences excluding redundant sentences
        final_sentences = []
        used_sim_sent_groups = {}

        for data in sentence_info_list:
            if len(final_sentences) >= num_sentences:
                break
            if data[2] not in used_sim_sent_groups:
                used_sim_sent_groups[data[2]] = True
                final_sentences.append(data[0])

        if self.debug:
            print("using sentences from group_ids %s" % str(list(used_sim_sent_groups.keys())))

        #arrange based on original sentence order
        final_sentences.sort(key=sentences.index)

        #combine the summaries together, with [...] to indicate parts that are removed.
        last_index = -1
        current_article_idx = 0
        next_article_start_idx = idx_article_start[0]
        final_summary_str = ""
        for sen in final_sentences:
            i = sentences.index(sen)
            if len(articles) == 1:
                if last_index != -1 and i - 1 > last_index:
                    final_summary_str += separator if separator else " [...] "
            else:
                appended = False
                while i >= next_article_start_idx:
                    if not appended and final_summary_str:
                        final_summary_str += separator if separator else "\n[------]\n"
                        appended = True

                    current_article_idx += 1
                    next_article_start_idx = idx_article_start[current_article_idx]


            if final_summary_str:
                final_summary_str += " "

            final_summary_str += sen.strip()
            last_index = i

        #return the final result
        return {
            "title": title.split("\n")[0],
            "summary_sentences": list(map(lambda x: x[0], sentence_info_list)),
            "summary": final_summary_str
        }



if __name__ == '__main__':
    #dummy debug code
    def read_input_file(fn):
        text_file=open(fn,"r")
        return text_file.read()

    try:
        summarizer = Summarizer(debug=True)
        items = []

        while True:
            print("\n")
            try:
                filenames = input("Filename (sep w/ ';') [^C to cancel]: ")
                print(filenames.split(';'))
                for filename in filenames.split(';'):
                    filename = filename.strip()
                    text = read_input_file(filename)
                    spstr = text.split("\n")
                    items.append((spstr[0], "\n".join(spstr[1:])))
                break
            except IOError:
                print("IO Error. Try again.")
                items = []


        print("note: assuming first line of each file to be the title.")
        ans = summarizer.summarize_all(items)
        print("\nTITLE:")
        print(ans['title'])
        print("\nSUMMARY:")
        print(ans['summary'])

    except KeyboardInterrupt:
        pass
