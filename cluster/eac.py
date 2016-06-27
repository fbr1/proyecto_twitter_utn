import multiprocessing
from functools import partial

from sklearn.cluster import KMeans
import numpy as np
import copy

class EAC:
    """
    EAC class.

    Parameters
    ----------
    iterations : int, optional, default: 30
        Number of iterations

    clustering : class, optional, default: Kmeans
        What clustering method to use. Must be a clustering object with a callable fix method

    min_k : int, optional, default: 5
        Minimum number of K clusters

    min_k : int, optional, default: 10
        Max number of K clusters

    """

    def __init__(self, iterations=8, clustering=None, min_k=5, max_k=10):

        self.iterations = iterations

        self.clustering = clustering

        self.min_k = min_k

        self.max_k = max_k

        self.co_asoc_matrix = None

    def _check_init_args(self):

        if self.clustering:
            if not callable(self.clustering.fit):
                raise ValueError("clustering Class needs to have a method fit callable")
        else:
            km = KMeans(init='k-means++', n_init=1, max_iter=100)
            self.clustering = km

    def fit(self, X):
        """
        Fit EAC of selected clustering to the provided data.

        Parameters
        ----------
        X : array-like matrix, shape=(n_samples, n_features)

        Returns
        -------
        self
        """

        self._check_init_args()

        # Setup Multiprocessing
        pool = multiprocessing.Pool(multiprocessing.cpu_count()-1)
        func = partial(self.EAC_worker, X)

        results = pool.imap_unordered(func, range(self.iterations))

        # Generate EAC distance matrix
        m, n = X.shape
        self.distance_ = np.zeros((m, m))

        for partial_dist in results:
            self.distance_ += partial_dist

        pool.close()
        pool.join()

        self.distance_ /= self.iterations

        return self

    def EAC_worker(self, X, i):

        # Choose random k value between min_k and max_k
        k = np.random.randint(self.min_k, self.max_k)

        # Run clustering
        clustering = copy.deepcopy(self.clustering)

        # If it's a K cluster algorithm
        if hasattr(self.clustering, 'n_clusters'):
            clustering.n_clusters = k

        clustering.fit(X)

        # Update co-association matrix
        m, n = X.shape
        partial_dist = np.ones((m, m))

        # For each cluster
        for j in range(k):
            cluster = np.where(clustering.labels_ == j)[0]
            for row in cluster:
                for column in cluster:
                    partial_dist[row, column] = 0

        return partial_dist