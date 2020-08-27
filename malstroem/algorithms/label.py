# coding=utf-8
# -------------------------------------------------------------------------------------------------
# Copyright (c) 2016
# Developed by Septima.dk and Thomas Balstrøm (University of Copenhagen) for the Danish Agency for
# Data Supply and Efficiency. This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free Software Foundation,
# either version 2 of the License, or (at you option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PORPOSE. See the GNU Gene-
# ral Public License for more details.
# You should have received a copy of the GNU General Public License along with this program. If not,
# see http://www.gnu.org/licenses/.
# -------------------------------------------------------------------------------------------------
from __future__ import (absolute_import, division, print_function) #, unicode_literals)  # See issue #3
from builtins import *
import numpy as np


def connected_components(data):
    """Label connected components in data.

    Parameters
    ----------
    data : array_like
        An array-like object to be labeled. Any non-zero values in input are counted as features and zero values are
        considered the background.

    Returns
    -------
    label : ndarray or int
        An integer ndarray where each unique feature in input has a unique label in the returned array.
    nlabels : int
        How many objects were found. Features are numbered in the range [1;nlabels]. The background is labelled 0.
    """
    import scipy.ndimage
    connectivity = [[1, 1, 1],
                    [1, 1, 1],
                    [1, 1, 1]]
    labelled, nlabels = scipy.ndimage.label(data, structure=connectivity)
    return labelled, nlabels


def label_stats(data, labelled, nlabels=None):
    """Calculate data stats for each label.

    Parameters
    ----------
    data
    labelled
    nlabels

    Returns
    -------

    """
    if not nlabels:
        nlabels = np.max(labelled)

    # dtype field names across py2 and py3 are a mess: https://github.com/numpy/numpy/issues/2407
    dtype = [('min', np.float64), ('max', np.float64), ('sum', np.float64), ('count', np.int64)]
    stats = np.zeros((nlabels + 1,), dtype=dtype)
    stats[:]['min'] = float('inf')
    stats[:]['max'] = float('-inf')
    for r in range(0, data.shape[0]):
        for c in range(0, data.shape[1]):
            val = data[r, c]
            lbl = labelled[r, c]
            record = stats[lbl]
            record['count'] += 1
            record['sum'] += val
            if val < record['min']:
                record['min'] = val
            if val > record['max']:
                record['max'] = val
    return stats


def keep_labels(labelled, keep_label, background=0):
    """

    Parameters
    ----------
    labelled
    keep_label : list-like
        List-like object of same length as number of labels. label n is kept if keep_label[n] == True
    background : int
        Label of background

    Returns
    -------
    new_components : ndarray
        A boolean array of same dimensions as labelled where True indicates a kept label
    """
    # Make sure background label is NOT kept
    keep_label[background] = False

    keep_array = np.array(keep_label).astype(bool)
    return keep_array[labelled]


def label_min_index(data, labelled, nlabels=None):
    """Calculate min data value and index for each label.

    Parameters
    ----------
    data
    labelled
    nlabels

    Returns
    -------

    """
    # TODO: Use labeled_comprehension from scipy instead?
    if not nlabels:
        nlabels = np.max(labelled)

    dtype = [('value', float), ('row', int), ('col', int)]
    lmin = np.zeros((nlabels + 1,), dtype=dtype)
    lmin[:]['value'] = float('inf')
    lmin[:]['row'] = -1
    lmin[:]['col'] = -1
    for r in range(0, data.shape[0]):
        for c in range(0, data.shape[1]):
            val = data[r, c]
            lbl = labelled[r, c]
            record = lmin[lbl]
            if val < record['value']:
                record['value'] = val
                record['row'] = r
                record['col'] = c
    return lmin


def label_max_index(data, labelled, nlabels=None):
    """Calculate max data value and index for each label.

    Parameters
    ----------
    data
    labelled
    nlabels

    Returns
    -------

    """
    # TODO: Use labeled_comprehension from scipy instead?
    if not nlabels:
        nlabels = np.max(labelled)

    dtype = [('value', float), ('row', int), ('col', int)]
    lmax = np.zeros((nlabels + 1,), dtype=dtype)
    lmax[:]['value'] = float('-inf')
    lmax[:]['row'] = -1
    lmax[:]['col'] = -1
    for r in range(0, data.shape[0]):
        for c in range(0, data.shape[1]):
            val = data[r, c]
            lbl = labelled[r, c]
            record = lmax[lbl]
            if val > record['value']:
                record['value'] = val
                record['row'] = r
                record['col'] = c
    return lmax


def label_count(labelled):
    """Count number of cells of each label.

    Parameters
    ----------
    labelled

    Returns
    -------
        List-like object of same length as number of labels where result[lbl] holds the number of cells for label = lbl
    """
    return np.bincount(labelled.ravel())



def label_data(data, labelled, nlabels=None, background=0):
    """Gathers all cell values for each label.

    Parameters
    ----------
    data : ndarray
        Data array of same dimensions as labelled
    labelled: ndarray
        An integer ndarray where each value indicates a unique feature.
    nlabels: int
        Number of labels (np.max(labelled))
    background: int
        Label of background. Data is NOT returned for the background label

    Returns
    -------
        data_per_label: list of lists
            A list (length = nlabels) of lists which holds the data values. The data for label n are found at data_per_label[n]
    """
    if not nlabels:
        nlabels = np.max(labelled)
    
    # Init list of lists
    l = [[] for x in range(nlabels + 1)]
    
    # Collect data per label
    ravelled_labelled = labelled.ravel()
    ravelled_data = data.ravel()
    for ix in range(len(ravelled_labelled)):
        label_id = ravelled_labelled[ix]
        data_value = ravelled_data[ix]
        if label_id == background:
            continue
        l[label_id].append(data_value)
    return l