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
from __future__ import (absolute_import, division, print_function) #, unicode_literals)
import cython
import numpy as np

# cimports
cimport numpy as np
from cyarray.carray cimport FloatArray, DoubleArray


cdef packed struct stat_record:
  np.float64_t min, max, sum
  np.int64_t count

cdef packed struct index_record:
    np.float64_t value
    np.int32_t row, col


def label_stats(data, labelled, nlabels=None):
    if data.dtype == np.float32 and labelled.dtype == np.int32:
        return label_stats_float32_int32_cython(data, labelled, nlabels)
    return label_stats_fallback_cython(data, labelled, nlabels)


@cython.boundscheck(False)
cdef label_stats_fallback_cython(data, labelled, nlabels=None):
    if not nlabels:
        nlabels = np.max(labelled)

    # dtype field names across py2 and py3 are a mess: https://github.com/numpy/numpy/issues/2407
    dtype = [('min', np.float64), ('max', np.float64), ('sum', np.float64), ('count', np.int64)]
    stats = np.zeros((nlabels + 1,), dtype=dtype)
    stats[:]['min'] = float('inf')
    stats[:]['max'] = float('-inf')

    cdef unsigned int r, c
    cdef np.float64_t val
    cdef np.int64_t lbl
    cdef stat_record[:] records = stats
    cdef stat_record record

    for r in range(0, data.shape[0]):
        for c in range(0, data.shape[1]):
            val = data[r, c]
            lbl = labelled[r, c]
            record = records[lbl]
            record.count += 1
            record.sum += val
            if val < record.min:
                record.min = val
            if val > record.max:
                record.max = val
            records[lbl] = record
    return stats

@cython.boundscheck(False)
cdef label_stats_float32_int32_cython(np.float32_t[:,:] data, np.int32_t[:,:] labelled, nlabels=None):
    if not nlabels:
        nlabels = np.max(labelled)

    # dtype field names across py2 and py3 are a mess: https://github.com/numpy/numpy/issues/2407
    dtype = [('min', np.float64), ('max', np.float64), ('sum', np.float64), ('count', np.int64)]
    stats = np.zeros((nlabels + 1,), dtype=dtype)
    stats[:]['min'] = float('inf')
    stats[:]['max'] = float('-inf')

    cdef unsigned int r, c
    cdef np.float32_t val
    cdef np.int32_t lbl
    cdef stat_record[:] records = stats
    cdef stat_record record

    for r in range(0, data.shape[0]):
        for c in range(0, data.shape[1]):
            val = data[r, c]
            lbl = labelled[r, c]
            record = records[lbl]
            record.count += 1
            record.sum += val
            if val < record.min:
                record.min = val
            if val > record.max:
                record.max = val
            records[lbl] = record
    return stats

@cython.boundscheck(False)
cdef label_min_index_float64_int32_cython(np.float64_t[:,:] data, np.int32_t [:,:] labelled, nlabels=None):
    if not nlabels:
        nlabels = np.max(labelled)

    dtype = [('value', np.float64), ('row', np.int32), ('col', np.int32)]
    lmin = np.zeros((nlabels + 1,), dtype=dtype)
    lmin[:]['value'] = float('inf')
    lmin[:]['row'] = -1
    lmin[:]['col'] = -1

    cdef unsigned int r, c
    cdef np.float64_t val
    cdef np.int32_t lbl
    cdef index_record[:] records = lmin
    cdef index_record record
    cdef unsigned int rows, cols
    rows, cols = data.shape[0], data.shape[1]

    for r in range(0, rows):
        for c in range(0, cols):
            val = data[r, c]
            lbl = labelled[r, c]
            record = records[lbl]
            if val < record.value:
                record.value = val
                record.row = r
                record.col = c
            records[lbl] = record
    return lmin

@cython.boundscheck(False)
cdef label_min_index_fallback_cython(data, labelled, nlabels=None):
    if not nlabels:
        nlabels = np.max(labelled)

    dtype = [('value', np.float64), ('row', np.int32), ('col', np.int32)]
    lmin = np.zeros((nlabels + 1,), dtype=dtype)
    lmin[:]['value'] = float('inf')
    lmin[:]['row'] = -1
    lmin[:]['col'] = -1

    cdef unsigned int r, c
    cdef np.float64_t val
    cdef np.int32_t lbl
    cdef index_record[:] records = lmin
    cdef index_record record
    cdef unsigned int rows, cols
    rows, cols = data.shape[0], data.shape[1]

    for r in range(0, rows):
        for c in range(0, cols):
            val = data[r, c]
            lbl = labelled[r, c]
            record = records[lbl]
            if val < record.value:
                record.value = val
                record.row = r
                record.col = c
            records[lbl] = record
    return lmin

def label_min_index(data, labelled, nlabels=None):
    if data.dtype == np.float64 and labelled.dtype == np.int32:
        return label_min_index_float64_int32_cython(data, labelled, nlabels)
    return label_min_index_fallback_cython(data, labelled, nlabels)

def label_data(data, labelled, nlabels=None, background=0):
    # Check types
    if not np.can_cast(background, np.int32, "safe"):
        raise TypeError("background must be integer")

    if nlabels is None:
        nlabels = np.max(labelled)
    elif not np.can_cast(nlabels, np.int32, "safe"):
            raise TypeError("nlabels must be integer")
        
    if data.dtype == np.float64 and labelled.dtype == np.int32:
        result = label_data_float64_int32_cython(data, labelled, nlabels, background)
    elif data.dtype == np.float32 and labelled.dtype == np.int32:
        result = label_data_float32_int32_cython(data, labelled, nlabels, background)
    else:
        result = label_data_fallback_cython(data, labelled, nlabels, background)
    return [np.array(x.get_npy_array()) for x in result]


@cython.boundscheck(False)
cdef label_data_float32_int32_cython(np.float32_t[:,:] data, np.int32_t[:,:] labels, max_label, background):
    cdef FloatArray tmp_cyarray    
    cdef unsigned int r, c
    cdef np.float32_t val
    cdef np.int32_t lbl, background_lbl

    # In cython list of lists: https://stackoverflow.com/questions/33851333/cython-how-do-you-create-an-array-of-cdef-class    
    list_of_cyarrays = list(FloatArray() for i in range(max_label + 1))
    
    # Collect data per label
    for r in range(0, data.shape[0]):
        for c in range(0, data.shape[1]):
            lbl = labels[r,c]
            val = data[r,c]
            if lbl == 0:
                continue
            tmp_cyarray = <FloatArray?>list_of_cyarrays[lbl]
            tmp_cyarray.c_append(val)
    return list_of_cyarrays


@cython.boundscheck(False)
cdef label_data_float64_int32_cython(np.float64_t[:,:] data, np.int32_t[:,:] labels, max_label, background):
    cdef DoubleArray tmp_cyarray    
    cdef unsigned int r, c
    cdef np.float64_t val
    cdef np.int32_t lbl, background_lbl
    
    # In cython list of lists: https://stackoverflow.com/questions/33851333/cython-how-do-you-create-an-array-of-cdef-class    
    list_of_cyarrays = list(DoubleArray() for i in range(max_label + 1))
    
    # Collect data per label
    for r in range(0, data.shape[0]):
        for c in range(0, data.shape[1]):
            lbl = labels[r,c]
            val = data[r,c]
            if lbl == 0:
                continue
            tmp_cyarray = <DoubleArray?>list_of_cyarrays[lbl]
            tmp_cyarray.c_append(val)
    return list_of_cyarrays

@cython.boundscheck(False)
cdef label_data_fallback_cython(data, labels, max_label, background):
    cdef DoubleArray tmp_cyarray    
    cdef unsigned int r, c
    cdef np.float64_t val
    cdef np.int64_t lbl, background_lbl
    
    # In cython list of lists: https://stackoverflow.com/questions/33851333/cython-how-do-you-create-an-array-of-cdef-class    
    list_of_cyarrays = list(DoubleArray() for i in range(max_label + 1))
    
    # Collect data per label
    for r in range(0, data.shape[0]):
        for c in range(0, data.shape[1]):
            lbl = labels[r,c]
            val = data[r,c]
            if lbl == 0:
                continue
            tmp_cyarray = <DoubleArray?>list_of_cyarrays[lbl]
            tmp_cyarray.c_append(val)
    return list_of_cyarrays