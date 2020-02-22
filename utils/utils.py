#!/usr/bin/python3
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

def visualize_tfidf_matrix(self, tfidf_matrix):
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

if __name__ == '__main__':
    print('[WARNING]: This module is not meant to be run as a standalone program.')
    # run tests?
