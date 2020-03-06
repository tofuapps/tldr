import json
import nltk

class Summarizer:
    """Summarizes a news article"""

    def __init__(self):
        self.stopwords = nltk.corpus.stopwords.words('english')


    def summarize(self, title, passage, title_factor=3, sentences=5, debug=False):
        """
        Returns a summary of the passage based upon the title.

        The importance of the title contents in the summary can be adjusted with the title_factor parameter, which defaults to 3.

        The number of sentences in the returned summary can be adjusted with the sentences parameter, which defaults to 5.

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
        sentence_score_pairs = sentence_score_pairs[0:min(sentences, len(sentence_score_pairs))]
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



if __name__ == '__main__':
    #dummy debug code
    def read_input_file(filename):
        text_file=open(filename,"r")
        return text_file.read()

    try:
        summarizer = Summarizer()
        while True:
            print("\n")
            try:
                text = read_input_file(input("Read file at path [^C to cancel]: "))
            except IOError:
                print("IO Error. Try again.")
                continue
            spstr = text.split("\n")
            print("assuming first line is title.")
            ans = summarizer.summarize(spstr[0], "\n".join(spstr[1:]))
            print("\nresult:\n")
            print(json.dumps(ans, indent=4))
            print("\n")
    except KeyboardInterrupt:
        pass
