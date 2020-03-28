import json
import nltk

class QuerySummarizer:
    """Performs multi-document (hopefully) query based summarization"""

    

    def __init__(self):
        self.stopwords = nltk.corpus.stopwords.words('english')


    def run(self, articles, query):
        """
        Articles: List of article objects, which should contain the following fields:
                * title : string
                * body: string

        Algorithm:
            We propose a pipeline to achieve query-focused multi-document abstractive summarisation. The
            basic steps included are as follows:
            1. Retrieve relevant documents for the given query from the entire corpus of documents.
            2. Extract relevant passages from each document.
            3. Extractive summarisation 
            information need.
            3. Perform redundancy removal to keep the length of such a collated document reasonable
            This following sections describes each step in the proposed pipeline in detail.
        """

        relevant_articles = self.extract_articles(articles, query)
        summary_raw = []
        for article in relevant_articles:
            summary_raw.append(self.summarize(article['title'], article['passage'], query))

        summary = '\n\n'.join([ x['title'] + ':\n' + x['summary'] for x in self.redundancy_filter(summary_raw) ])
        return { 'summary': summary }
        

    def extract_articles(self, articles, query):
        return articles
        pass


    def summarize(self, title, passage, query, title_factor=3, num_sentences=5, debug=False):
        """
        Returns a summary of the passage based upon the title.

        The importance of the title contents in the summary can be adjusted with the title_factor parameter, which defaults to 3.

        The number of sentences in the returned summary can be adjusted with the num_sentences parameter, which defaults to 5.

        A dict with the keys 'title' and 'summary' will be returned.
        """
        if not passage:
            return {"title": title, "summary": None}

        paragraphs = passage.split("\n\n")
        sentences  = []
        for paragraph in paragraphs:
            sentences += nltk.sent_tokenize(paragraph)

        #tokenizes words
        tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
        title_words = [word.lower() for word in tokenizer.tokenize(title)]
        words       = [word.lower() for word in tokenizer.tokenize(passage)]

        #calculate frequency of words
        word_freq = {}
        for word in words:
            if word in self.stopwords:
                continue
            if word in word_freq:
                word_freq[word] += 1
            else:
                word_freq[word] = 1

        #amplify importance of words contained in title
        for word in word_freq:
            if word in title_words:
                word_freq[word] *= title_factor

        #preprocess the query: tokenize and calculate freq
        #TODO current process calculates some kind of relevance score, but we need fidelity score
        #Fidelity score: Score rel (sen) = RET ∗ n^2 /q, where
        #   *RET is a constant (default 2), n is number of query terms in sentence, q is total number of query terms
        #Paper's Relevance score: Score f id (sen) = SW^2 /TW, where
        #   *SW is number of significant words in cluster, TW is total number of words in cluster

        #find weighted frequency
        max_freq = max(word_freq.values())
        for word in word_freq:
            word_freq[word] /= max_freq

        #calculate sentence score - saved in form (sentence, score)
        sentence_score_pairs = []
        for sentence in sentences:
            score = 0
            for word in tokenizer.tokenize(sentence.lower()):
                score += word_freq.get(word, 0)

            sentence_score_pairs.append((sentence, score))

        #sort by sentence scores
        sentence_score_pairs.sort(key=lambda x: x[1], reverse=True)
        if debug:
            print("sentence scoring")
            for data in sentence_score_pairs:
                print(str(data[1]) + ": " + data[0])

        #use first 5 sentences, and arrange based on original sentence order
        sentence_score_pairs = sentence_score_pairs[0:min(num_sentences, len(sentence_score_pairs))]
        sentence_score_pairs.sort(key=lambda x: sentences.index(x[0]))

        #combine the summaries together, with [...] to indicate parts that are removed.
        last_index = -1
        final_summary = ""
        for sen, _ in sentence_score_pairs:
            i = sentences.index(sen)
            if last_index != -1 and i - 1 > last_index:
                final_summary += "\n[...]"
            if last_index != -1:
                final_summary += "\n"
            final_summary += sen.strip()
            last_index = i

        return {
            "title": title,
            "summary": final_summary
        }


    def redundancy_filter(self, articles):
        # TODO: implement cosine similarity test
        return articles


if __name__ == '__main__':
    qs = QuerySummarizer()
    articles = []
    with open('test.in', 'r') as f:
        s = f.readlines()
        a = { 'title': s[0], 'body': s[1:] }
        articles.append(a)
    query = 'trump'
    print(qs.run(articles, query))