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

        def normalize(t):
            return [self.wordnet_lemmatizer.lemmatize(word.lower()) for word in self.tokenizer.tokenize(t)]
        self.tfidf_vectorizer = TfidfVectorizer(max_df=0.7, stop_words="english")

    def summarize(self, articles, query=None):
        """
        Returns a summary of the passage based upon the articles given.

        Articles must be formatted in the form {'title': <>, 'passage': <>}

        A dict with the keys 'title' and 'summary' will be returned.
        """
        if query is None:
            return self.summarize_all(articles)
        #else:
            #querySummarizer = QuerySummarizer()
            #return querySummarizer.run(articles, query)


    def single_summarize(self, title, passage, title_factor=3, num_sentences=None):
        """
        Returns a summary of the passage based upon the title.

        The importance of the title contents in the summary can be adjusted with the title_factor parameter, which defaults to 3.

        The number of sentences in the returned summary can be adjusted with the num_sentences parameter, which defaults to None (auto-determine).

        A dict with the keys 'title', 'summary_sentences' and 'summary' will be returned.

        This is a wrapper for summarize_all method for a single article.
        """
        return self.summarize_all([(title, passage)], title_factor, num_sentences)


    def __levenshtein(self,seq1, seq2):
        """
        Calculates Levenshtein distance of two sequences.

        Retrieved from https://stackabuse.com/levenshtein-distance-and-text-similarity-in-python/
        """
        size_x = len(seq1) + 1
        size_y = len(seq2) + 1
        matrix = np.zeros ((size_x, size_y))
        for x in range(size_x):
            matrix [x, 0] = x
        for y in range(size_y):
            matrix [0, y] = y

        for x in range(1, size_x):
            for y in range(1, size_y):
                if seq1[x-1] == seq2[y-1]:
                    matrix [x,y] = min(
                        matrix[x-1, y] + 1,
                        matrix[x-1, y-1],
                        matrix[x, y-1] + 1
                    )
                else:
                    matrix [x,y] = min(
                        matrix[x-1,y] + 1,
                        matrix[x-1,y-1] + 1,
                        matrix[x,y-1] + 1
                    )
        return (matrix[size_x - 1, size_y - 1])

    def __sentence_lev_dist_2d(self,*sentences):
        """
        Calculate sentence distances based on Levenshtein distance of lemmatized words.

        This allows matching of similar to exact sentences.

        Returns a 2d numpy array of distances of each sentence to all others.

        Note: if return_value[2,3]==1, it refers to sentences with indices 2 & 3 having a 1 word difference.
        """
        sentence_list = list(map(lambda x:
                                 list(filter(lambda y: y not in self.stopwords, [self.wordnet_lemmatizer.lemmatize(word.lower()) for word in self.tokenizer.tokenize(x)])),
                                 sentences
        ))

        #TODO: Check if considering stopwords would affect accuracy.

        size = len(sentence_list)

        result = np.zeros((size, size))
        for i in range(size):
            for j in range(i, size):
                sent_a = sentence_list[i]
                sent_b = sentence_list[j]
                lev_dist = int(self.__levenshtein(sent_a, sent_b))
                result[i, j] = lev_dist
                result[j, i] = lev_dist

        return result

    def __sentence_cos_sim_2d(self, *sentences):
        """
        Calculate sentence cosine similarities from tfdif vectorisation.

        Returns a 2d numpy array of similarities of each sentence to all others.

        Note: if return_value[2,3]==1, it refers to sentences with indices 2 & 3 having a cos sim of 1, i.e. exactly the same.
        """
        tfidf = self.tfidf_vectorizer.fit_transform(sentences)
        pairwise_similarity = tfidf * tfidf.T
        arr = pairwise_similarity.toarray()
        return arr




    def summarize_all(self, articles, title_factor=3, num_sentences=None):
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

        #find weighted frequency
        max_freq = max(word_freq.values())
        for word in word_freq:
            word_freq[word] /= max_freq

        #calculate sentence distance for redundancy removal later
        sentence_lev_dist = self.__sentence_lev_dist_2d(*sentences)
        sentence_cos_sim = self.__sentence_cos_sim_2d(*sentences)

        #calculate sentence info - saved in form (sentence, score, accepted)
        sentence_info_list = []
        for idx, sentence in enumerate(sentences):
            score = 0
            for word in self.tokenizer.tokenize(sentence.lower()):
                word = self.wordnet_lemmatizer.lemmatize(word)
                score += word_freq.get(word, 0)

            #get comparison of this sentence among all others
            levdis = sentence_lev_dist[idx,:]
            cossim = sentence_cos_sim[idx,:]

            #search for close matches in sentences
            idx_levdis, = np.where((levdis < 8))
            idx_cossim, = np.where((cossim > 0.6))

            #merge all matches
            idx_consider = np.unique(np.concatenate((idx_levdis, idx_cossim)))

            #if self.debug:
                #print(idx_consider)

            #the sentence would only be similar to itself if it's unique. If it's not unique, it should only accept the sentence if it's the first to appear.
            accepted = idx_consider.shape[0] <= 1 or idx_consider[0] == idx

            #add to list
            sentence_info_list.append((sentence, score, accepted))

        #sort by sentence scores
        sentence_info_list.sort(key=lambda x: x[1], reverse=True)
        if self.debug:
            print("<accepted>[score] <sentence>")
            for data in sentence_info_list[0:min(len(sentence_info_list), 20)]:
                print("%1s[%.6f]: %s" % ("+" if data[2] else "-", data[1], data[0]))

        #remove redundant sentences
        sentence_info_list = list(filter(lambda x: x[2], sentence_info_list))

        #use first n sentences, and arrange based on original sentence order
        sentence_info_list = sentence_info_list[0:min(num_sentences, len(sentence_info_list))]
        sentence_info_list.sort(key=lambda x: sentences.index(x[0]))

        #combine the summaries together, with [...] to indicate parts that are removed.
        last_index = -1
        current_article_idx = 0
        next_article_start_idx = idx_article_start[0]
        final_summary_str = ""
        for sen, _, _ in sentence_info_list:
            i = sentences.index(sen)
            if len(articles) == 1:
                if last_index != -1 and i - 1 > last_index:
                    final_summary_str += " [...] "
            else:
                appended = False
                while i >= next_article_start_idx:
                    if not appended and final_summary_str:
                        final_summary_str += "\n[------]\n"
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
        articles = []

        while True:
            print("\n")
            try:
                filenames = input("Filename (sep w/ ';') [^C to cancel]: ")
                print(filenames.split(';'))
                for filename in filenames.split(';'):
                    filename = filename.strip()
                    text = read_input_file(filename)
                    spstr = text.split("\n")
                    articles.append((spstr[0], "\n".join(spstr[1:])))
                break
            except IOError:
                print("IO Error. Try again.")
                articles = []


        print("note: assuming first line of each file to be the title.")
        ans = summarizer.summarize_all(articles)
        print("\nTITLE:")
        print(ans['title'])
        print("\nSUMMARY:")
        print(ans['summary'])

    except KeyboardInterrupt:
        pass
