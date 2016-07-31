import numpy as np
import multiprocessing
from datasketch.minhash import MinHash
from functools import partial

# Constants
MAX_SLICES = 16


class PartialDist:
    def __init__(self, X=None, Y=None, matrix=None):
        self.X = X
        self.Y = Y
        self.matrix = matrix


def _extract_shingles(string, shingle_length=2):
    words = string.split()
    n_words = len(words)

    shingle_lenght = min(n_words, shingle_length)

    shingles = []
    for i in range(n_words - shingle_lenght + 1):
        shingles.append(" ".join(words[i:i + shingle_lenght]))

    return shingles


def jaccard_minhash_distance(data, shingle_length=2):
    """
    Calculate and return the jaccard distance matrix of all data's elements.

    :param data: list of strings
    :param shingle_length: int, optional, default: 2
    :return D:
    """
    n = len(data)
    D = np.zeros((n, n))

    # Progress bar initialization
    total = n-1
    increment = int(0.02 * total)
    if int(0.02 * total) == 0:
        increment = 1

    _progress(0, n)

    # Calculate jaccard distance in a upper triangular matrix
    for i in range(n - 1):
        for j in range(i + 1, n):
            m1 = MinHash()
            m2 = MinHash()
            for d in _extract_shingles(data[i], shingle_length):
                m1.update(d.encode('utf8'))
            for d in _extract_shingles(data[j], shingle_length):
                m2.update(d.encode('utf8'))
            D[i, j] = 1 - m1.jaccard(m2)

        # Report progress
        if i % increment == 0:
            _progress(i, total)

    # Transform matrix into a symmetrical matrix
    D += D.T

    # End progress bar
    _progress(total, total)

    return D


def jaccard_minhash_distance_mp(data, shingle_length=2):
    """
    Multiprocessing version.
    Calculate and return the jaccard distance matrix of all data's elements.

    If the number of data's elements doesn't meet the criteria described in
    the function get_number_sections(n) or if there is only one processor, the single
    core jaccard_minhash_distance is executed.

    :param data: list of strings
    :param shingle_length: int, optional, default: 2
    :return D:
    """

    n = len(data)
    n_processors = multiprocessing.cpu_count()
    n_sections, n_slices = _get_number_sections(n)

    # If there is only one processor or 'n' is not divisible by (2, MAX_SLICES), execute single core version
    if n_processors == 1 or not n_sections:
        return jaccard_minhash_distance(data, shingle_length=shingle_length)

    # Setup Multiprocessing
    pool = multiprocessing.Pool(n_processors)

    func = partial(_jac_minh_worker, data, n_slices, shingle_length)

    dist_list = []

    # Start Progress bar
    _progress(0, n_sections)

    # Execute jobs and store partial_dist
    for i, partial_dist in enumerate(pool.imap_unordered(func, range(n_sections))):
        _progress(i, n_sections)
        dist_list.append(partial_dist)

    pool.close()
    pool.join()

    # End Progress bar
    _progress(n_sections, n_sections)

    # Create and update final distance matrix
    D = np.zeros((n, n))
    section_lenght = int(n / n_slices)

    for partial_dist in dist_list:
        X = partial_dist.X
        Y = partial_dist.Y
        D[X * section_lenght: ((X + 1) * section_lenght), Y * section_lenght: ((Y + 1) * section_lenght)] = partial_dist.matrix

    ind_low = np.tril_indices(n)
    D[ind_low] = 0
    D += D.T

    return D


def _jac_minh_worker(data, n_slices, shingle_length, i):
    """
    Given n = length (data)
    Returns a submatrix of the n x n final distance matrix

    :param data: list of strings
    :param n_slices: int
    :param shingle_length: int
    :param i:
    :return partial_dist: PartialDist
    """

    # Initialization
    n = len(data)
    section_lenght = int(n / n_slices)
    X, Y = _get_coord_section(i+1, n_slices)
    D = np.zeros((section_lenght, section_lenght))

    # Create distance submatrix according to number of worker (i)
    row = 0
    column = 0
    for i in range(X * section_lenght, ((X + 1) * section_lenght)):
        for j in range(Y * section_lenght, ((Y + 1) * section_lenght)):
            m1 = MinHash()
            m2 = MinHash()
            for d in _extract_shingles(data[i], shingle_length):
                m1.update(d.encode('utf8'))
            for d in _extract_shingles(data[j], shingle_length):
                m2.update(d.encode('utf8'))

            D[row, column] = 1 - m1.jaccard(m2)

            column += 1
        row += 1
        column = 0

    return PartialDist(X, Y, D)


def _get_coord_section(k, n_slices):
    """ Returns PartialDist's coordinates according to the number of worker

    :return i: X coordinate
    :return j: Y coordinate

    """
    count = 0
    for i in range(0, n_slices):
        for j in range(i, n_slices):
            count += 1
            if count == k:
                return i, j


def _get_number_sections(n):
    """
    Get number of sections according to number of elements n
    It checks if n is divisible by the numbers in the range (2, MAX_SLICES) and if the
    length of the generated slices is 2 or more.

    Returns the maximum possible number of n_sections.

    Parameters
    ----------
    :param n: number of elements

    Returns
    -------
    :return n_sections: int
    :return n_slices: int
    """
    for i in range(MAX_SLICES, 2, -1):
        n_sections = i * (i + 1) / 2

        if n % i == 0 and n / i > 1:
            return int(n_sections), i

    return None, None


def _progress(count, total):
    workdone = count/total

    print("\rProgress: [{0:50s}] {1:.1f}%".format('#' * int(workdone * 50), workdone * 100), end="", flush=True)
    if count == total:
        print('\n')
