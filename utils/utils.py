#!/usr/bin/python3
from bs4 import BeautifulSoup, Comment
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

def visualize_tfidf_matrix(tfidf_matrix):
    # Visualisation (optional)
    # ----------------------------------------------------------------------------------------------------------------------
    X = tfidf_matrix.todense() # convert list of vectors into 2d matrix

    # first reduction using PCA (Principal Component Analysis)
    reduced_data = PCA(n_components=50).fit_transform(X)

    labels_color_map = {
        0: '#20b2aa', 1: '#ff7373', 2: '#ffe4e1', 3: '#005073', 4: '#4d0404',
        5: '#ccc0ba', 6: '#4700f9', 7: '#f6f900', 8: '#00f91d', 9: '#da8c49'
    }
    fig, ax = plt.subplots()
    for index, instance in enumerate(reduced_data):
        # print instance, index, labels[index]
        pca_comp_1, pca_comp_2 = reduced_data[index]
        color = labels_color_map[labels[index]]
        ax.scatter(pca_comp_1, pca_comp_2, c=color)
        plt.show()

    # second reduction using t-SNE (t-Distributed Stochastic Neighbouring Entities)
    embeddings = TSNE(n_components=2)
    Y = embeddings.fit_transform(X)
    plt.scatter(Y[:, 0], Y[:, 1], cmap=plt.cm.Spectral)
    plt.show()

def clean_html(content, tag=None, auto_tag=False):
    """
    Parses and retrieves primary plain text content from html content.
    Excludes headings, images, JS code, headers & footers, etc.
    Filtering a full article by tag is not fully working yet.
    """
    #remove html comments
    soup = BeautifulSoup(content, 'html.parser')
    comments = soup.findAll(text=lambda text:isinstance(text, Comment))
    _ = [comment.extract() for comment in comments]
    commentless_content = str(soup)

    if tag or auto_tag:
        #get the relevant tag
        soup = BeautifulSoup(commentless_content, 'html.parser')

        if tag:
            tags = soup.find_all(tag)
        if auto_tag:
            if not tags:
                tags = soup.find_all("article")
            if not tags:
                tags = soup.find_all("div", "container")

        article_raw_content = "" if not tags else str(tags[0])
    else:
        article_raw_content = "<span>" + commentless_content + "</span>"

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
    index_end_search = len(contents)
    tag_names = list(map(lambda x: x.parent.name, contents))

    if tag or auto_tag:
        while "header" in tag_names:
            i = tag_names.index("header")
            index_start_search = i
            tag_names[i] = ""
        if "footer" in tag_names:
            index_end_search = tag_names.index("footer")

    #start extracting contents into content_str
    content_str = ""
    for item in contents[index_start_search: index_end_search]:
        if item.parent.name not in blacklist and str(item) != "Advertisement":
            content_str += str(item).strip() + " "

    #clean up newlines
    while True:
        _tmp = content_str.replace("\n\n", "\n").replace("\n ", "\n").replace("  "," ")
        if content_str == _tmp:
            break
        content_str = _tmp

    #return contents
    return content_str.strip()

### TESTS ###
def test_clean_html():
    print("TEST: clean_html")
    print("  plain text rejection : " + str(clean_html("test 123").strip() == "test 123"))
    print("  html text cleaning   : " + str(clean_html("<u><b>test</b></u> <i>123</i>").strip() == "test 123"))


if __name__ == '__main__':
    print("Testing utilities...")
    test_clean_html()



