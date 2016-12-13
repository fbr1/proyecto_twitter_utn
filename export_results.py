from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import make_pipeline
from time import time
from cluster.eac import EAC
from cluster.kmedoids import KMedoids
from sklearn.cluster import KMeans
import metrics.jaccard_minhash as metrics
import util
import filter
import warnings
import json
warnings.filterwarnings("ignore", category=DeprecationWarning)

def isAdable(table):
    for i in range(2):
        count = 0
        for j in range(2):
            count += table[i][j]
        if count > 1:
            return False

    return True

def kmeans(eac, removeTerms, ngram):
    terms = ['lazaro', 'lázaro', 'baez', 'báez', 'carlitos']

    print('Filtering tweets')
    tweets = util.read_from_file("dataset.csv")
    if removeTerms:
        tweets = filter.filter_tweets(tweets, terms_to_remove=terms)
    else:
        tweets = filter.filter_tweets(tweets)

    # Reduce tweets list length
    tweets = tweets[0:6300]

    carlitos = 0
    lazaro = 0

    data = []
    for tw in tweets:
        if tw.tw_type == 'Carlitos':
            carlitos += 1
        else:
            lazaro += 1
        data.append(tw.text)

    print(carlitos, lazaro)

    print("Transform Data...")
    # Transform data
    if ngram:
        hasher = HashingVectorizer(non_negative=True, ngram_range=(1, 3), analyzer='word',
                                   norm='l2', binary=False)
    else:
        hasher = HashingVectorizer(non_negative=True,
                                   norm='l2', binary=False)
    vectorizer = make_pipeline(hasher)
    X = vectorizer.fit_transform(data)

    count = 0
    precision_list = []

    while count < 100:

        # Start timer
        t0 = time()

        if eac:

            clustering = EAC(30, min_k=2, max_k=10)
            EAC_D = clustering.fit(X).distance_

            # Kmedoids over EAC_D
            kmed = KMedoids(2, init='random', distance_metric="precomputed")
            labels = kmed.fit(EAC_D).labels_

        else:

            km = KMeans(n_clusters=2, init='k-means++', n_init=1, max_iter=100)
            labels = km.fit(X).labels_

        # Assign labels to tweets
        for i in range(len(tweets)):
            tweets[i].label = labels[i]

        print("Precision: ")
        # Print precision
        precision = util.precision(tweets)

        print("done in %0.3fs" % (time() - t0))

        if isAdable(precision):
            precision_list.append(precision)
            count += 1

    return precision_list


def minhash(eac, shingle, removeTerms):
    terms = ['lazaro', 'lázaro', 'baez', 'báez', 'carlitos']

    print('Filtering tweets')
    tweets = util.read_from_file("dataset.csv")
    if removeTerms:
        tweets = filter.filter_tweets(tweets, terms_to_remove=terms)
    else:
        tweets = filter.filter_tweets(tweets)

    # Reduce tweets list length
    tweets = tweets[0:6300]

    carlitos = 0
    lazaro = 0

    data = []
    for tw in tweets:
        if tw.tw_type == 'Carlitos':
            carlitos += 1
        else:
            lazaro += 1
        data.append(tw.text)

    print(carlitos, lazaro)

    # Extract text from tweets
    X = [tw.text for tw in tweets]

    # Start timer
    t0 = time()

    print("Calculating distance matrix...")
    D = metrics.jaccard_minhash_distance_mp(X, shingle_length=shingle)

    count = 0
    precision_list = []

    while count < 100:

        if eac:

            print("EAC clustering...")
            # EAC clustering
            kmedoid = KMedoids(init='random', distance_metric='precomputed')
            clustering = EAC(30, min_k=2, max_k=10, clustering=kmedoid)
            EAC_D = clustering.fit(D).distance_

            # Kmedoids over EAC_D
            kmed = KMedoids(2, init='random', distance_metric="precomputed")
            labels = kmed.fit(EAC_D).labels_

        else:
            kmedoid = KMedoids(2, init='random', distance_metric='precomputed')

            print("Kmedoids clustering...")
            labels = kmedoid.fit(D).labels_

        # Assign labels to tweets
        for i in range(len(tweets)):
            tweets[i].label = labels[i]

        # Print precision
        print("Precision: ")
        precision = util.precision(tweets)

        if isAdable(precision):
            print(count)
            precision_list.append(precision)
            count += 1

        print("done in %0.3fs" % (time() - t0))

    return precision_list

if __name__ == "__main__":

    # EAC Kmeans
    precision_list = kmeans(eac=True, removeTerms=True, ngram=False)
    with open('N6300_100_eac_kmeans.json', 'w') as myfile:
        json.dump(precision_list, myfile)

    # Con Term
    precision_list = kmeans(eac=True, removeTerms=False, ngram=False)
    with open('N6300_100_eac_kmeans_sinterm.json', 'w') as myfile:
        json.dump(precision_list, myfile)

    # # MinHash
    # # Shingle 1
    # precision_list = minhash(eac=False, shingle=1,removeTerms=True)
    # with open('N6300_100_minhash_1shingle_sinterm.json', 'w') as myfile:
    #     json.dump(precision_list, myfile)
    #
    # # Shingle 2
    # precision_list = minhash(eac=False, shingle=2,removeTerms=True)
    # with open('N6300_100_minhash_2shingle_sinterm.json', 'w') as myfile:
    #     json.dump(precision_list, myfile)
    #
    # # EAC MinHash
    # # Shingle 1
    # precision_list = minhash(eac=True, shingle=1,removeTerms=True)
    # with open('N6300_100_eac_minhash_1shingle_sinterm.json', 'w') as myfile:
    #     json.dump(precision_list, myfile)
    #
    # # Shingle 2
    # precision_list = minhash(eac=True, shingle=2,removeTerms=True)
    # with open('N6300_100_eac_minhash_2shingle_sinterm.json', 'w') as myfile:
    #     json.dump(precision_list, myfile)
