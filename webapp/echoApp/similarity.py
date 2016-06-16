import numpy
import scipy.sparse
from scipy.stats import entropy
import scipy.linalg
from scipy.linalg.lapack import get_lapack_funcs
from six import iteritems, itervalues, string_types


def isbow(vec):
    """
    Checks if vector passed is in bag of words representation or not.
    Vec is considered to be in bag of words format if it is 2-tuple format.
    """
    if scipy.sparse.issparse(vec):
        vec = vec.todense().tolist()
    try:
        id_, val_ = vec[0] # checking first value to see if it is in bag of words format by unpacking
        id_, val_ = int(id_), float(val_)
    except IndexError:
        return True # this is to handle the empty input case
    except Exception:
        return False
    return True


def kullback_leibler(vec1, vec2, num_features=None):
    """
    A distance metric between two probability distributions.
    Returns a distance value in range <0,1> where values closer to 0 mean less distance (and a higher similarity)
    Uses the scipy.stats.entropy method to identify kullback_leibler convergence value.
    If the distribution draws from a certain number of docs, that value must be passed.
    """
    if scipy.sparse.issparse(vec1):
        vec1 = vec1.toarray()
    if scipy.sparse.issparse(vec2):
        vec2 = vec2.toarray() # converted both the vectors to dense in case they were in sparse matrix 
    if isbow(vec1) and isbow(vec2): # if they are in bag of words format we make it dense
        if num_features != None: # if not None, make as large as the documents drawing from
            dense1 = sparse2full(vec1, num_features)
            dense2 = sparse2full(vec2, num_features)
            return entropy(dense1, dense2)
        else:
            max_len = max(len(vec1), len(vec2))
            dense1 = sparse2full(vec1, max_len)
            dense2 = sparse2full(vec2, max_len)
            return entropy(dense1, dense2)
    else:
        # this conversion is made because if it is not in bow format, it might be a list within a list after conversion
        # the scipy implementation of Kullback fails in such a case so we pick up only the nested list.
        if len(vec1) == 1:
            vec1 = vec1[0]
        if len(vec2) == 1:
            vec2 = vec2[0]
        return scipy.stats.entropy(vec1, vec2)


def hellinger(vec1, vec2):
    """
    Hellinger distance is a distance metric to quantify the similarity between two probability distributions.
    Distance between distributions will be a number between <0,1>, where 0 is minimum distance (maximum similarity) and 1 is maximum distance (minimum similarity).
    """
    if scipy.sparse.issparse(vec1):
        vec1 = vec1.toarray()
    if scipy.sparse.issparse(vec2):
        vec2 = vec2.toarray()
    if isbow(vec1) and isbow(vec2): 
        # if it is a bag of words format, instead of converting to dense we use dictionaries to calculate appropriate distance
        vec1, vec2 = dict(vec1), dict(vec2)
        if len(vec2) < len(vec1): 
            vec1, vec2 = vec2, vec1 # swap references so that we iterate over the shorter vector
        sim = numpy.sqrt(0.5*sum((numpy.sqrt(value) - numpy.sqrt(vec2.get(index, 0.0)))**2 for index, value in iteritems(vec1)))
        return sim
    else:
        sim = numpy.sqrt(0.5 * ((numpy.sqrt(vec1) - numpy.sqrt(vec2))**2).sum())
        return sim


def jaccard(vec1, vec2):
    """
    A distance metric between bags of words representation.
    Returns 1 minus the intersection divided by union, where union is the sum of the size of the two bags.
    If it is not a bag of words representation, the union and intersection is calculated in the traditional manner.
    Returns a value in range <0,1> where values closer to 0 mean less distance and thus higher similarity.
    """

    # converting from sparse for easier manipulation
    if scipy.sparse.issparse(vec1):
        vec1 = vec1.toarray()
    if scipy.sparse.issparse(vec2):
        vec2 = vec2.toarray()
    if isbow(vec1) and isbow(vec2): 
        # if it's in bow format, we use the following definitions:
        # union = sum of the 'weights' of both the bags
        # intersection = lowest weight for a particular id; basically the number of common words or items 
        union = sum(weight for id_, weight in vec1) + sum(weight for id_, weight in vec2)
        vec1, vec2 = dict(vec1), dict(vec2)
        intersection = 0.0
        for feature_id, feature_weight in iteritems(vec1):
            intersection += min(feature_weight, vec2.get(feature_id, 0.0))
        return 1 - float(intersection) / float(union)
    else:
        # if it isn't in bag of words format, we can use sets to calculate intersection and union
        if isinstance(vec1, numpy.ndarray):
            vec1 = vec1.tolist()
        if isinstance(vec2, numpy.ndarray):
            vec2 = vec2.tolist()
        vec1 = set(vec1)
        vec2 = set(vec2)
        intersection = vec1 & vec2
        union = vec1 | vec2
        return 1 - float(len(intersection)) / float(len(union))