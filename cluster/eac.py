from sklearn.cluster import MiniBatchKMeans
import numpy as np

class EAC:
    """
    EAC class.

    Parameters
    ----------
    iterations : int, optional, default: 30
        Number of iterations

    clustering : class, optional, default: MiniBatchKmeans
        What clustering method to use. Must be a clustering object with a callable fix method

    min_k : int, optional, default: 5
        Minimum number of K clusters

    min_k : int, optional, default: 10
        Max number of K clusters

    """

    def __init__(self, iterations=8, clustering=None, min_k=5, max_k=10):

        self.iterations = iterations

        self.clustering=clustering

        self.min_k = min_k

        self.max_k = max_k

    def _check_init_args(self):

        if self.clustering:
            if not callable(self.clustering.fix):
                km = MiniBatchKMeans(init='k-means++', n_init=1,
                                     init_size=1000, batch_size=1000)
                self.clustering = km
        else:
            raise ValueError("clustering Class needs to have a method fit callable")

    def fit(self, X):
        """Fit EAC of selected clustering to the provided data.

        Parameters
        ----------
        X : array-like or sparse matrix, shape=(n_samples, n_features)

        Returns
        -------
        self
        """

        self._check_init_args()

        m, n = X.shape

        co_asoc_matrix = np.zeros((m, m))

        for i in range(self.iterations):
            # Choose random k value between min_k and max_k

            k = np.random.randint(self.min_k, self.max_k)

            # Run clustering

            # If it's a K algorithm
            if hasattr(self.clustering, 'n_clusters'):
                self.clustering.n_clusters = k

            self.clustering.fit(X)

            # Update co-association matrix
            # For each cluster
            for j in range(k):
                cluster = np.where(self.clustering.labels_ == j)[0]
                for row in cluster:
                    for column in cluster:
                        if row < column:
                            co_asoc_matrix[row][column] += 1 / self.iterations
                        elif row == column:
                            co_asoc_matrix[row][column] = 1

