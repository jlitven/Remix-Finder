"""
Module for doing image analysis.

References:
http://stackoverflow.com/questions/3241929/python-find-dominant-most-common-color-in-an-image/3242290

Joshua Litven July 2016.
"""
from PIL import Image
import scipy
import scipy.misc
import scipy.cluster
import requests
from StringIO import StringIO

def cluster_colors(image_url, num_clusters=5):
    """
    Return the most clustered colors of an image.
    Use scipy's k-means clustering algorithm.
    """

    print 'Reading image...'
    response = requests.get(image_url)
    im = Image.open(StringIO(response.content))
    im = im.resize((150, 150))      # optional, to reduce time
    ar = scipy.misc.fromimage(im)
    shape = ar.shape
    ar = ar.reshape(scipy.product(shape[:2]), shape[2])
    ar = ar.astype(float)

    print 'Finding clusters...'
    # k-means clustering
    codes, dist = scipy.cluster.vq.kmeans(ar, num_clusters)
    vecs, dist = scipy.cluster.vq.vq(ar, codes)         # assign codes
    counts, bins = scipy.histogram(vecs, len(codes))    # count occurrences
    sorted_index = sorted(range(len(counts)), key=lambda index: counts[index], reverse=True)

    most_common_colors = []
    for index in sorted_index:
        peak = codes[index]
        peak = peak.astype(int)
        colour = ''.join(format(c, '02x') for c in peak)
        most_common_colors.append('#' + colour)
    return most_common_colors
