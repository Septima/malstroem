from __future__ import (absolute_import, division, print_function) #, unicode_literals)

from collections import deque

import numpy as np
import pytest
from builtins import *
from malstroem.algorithms import flow, label, speedups
from data.fixtures import fillednoflatsdata, flowdirdata, bspotdata


def test_flowdir_noflats(fillednoflatsdata, flowdirdata):
    speedups.disable()
    assert not speedups.enabled
    flowdir = flow.terrain_flowdirection(fillednoflatsdata)
    assert np.all(flowdir >= 0)
    assert np.all(flowdir <= 8)
    assert np.all(flowdir == flowdirdata)

def test_flowdir_noflats_optimized(fillednoflatsdata, flowdirdata):
    speedups.enable()
    assert speedups.enabled
    flowdir = flow.terrain_flowdirection(fillednoflatsdata)
    assert np.all(flowdir >= 0)
    assert np.all(flowdir <= 8)
    assert np.all(flowdir == flowdirdata)

def test_flow_trace(flowdirdata):
    source_cell = (100, 100)
    trace = list(flow.trace_downstream(flowdirdata, source_cell))
    assert len(trace) == 100
    assert trace[-1] == (187, 83)


def test_flow_upstream(flowdirdata):
    # Calculate watershed to massage upstream code
    def trace_watershed(flowraster, cell):
        upstream = np.zeros(flowraster.shape, dtype=bool)
        stack = deque([cell])
        while stack:
            current_cell = stack.pop()
            upstream[current_cell[0], current_cell[1]] = True
            stack.extend(flow.upstream_cells(flowraster, current_cell))
        return upstream
    up = trace_watershed(flowdirdata, (186, 82))
    assert np.sum(up) == 5267


def test_accumulated_flow(flowdirdata):
    from malstroem.algorithms import speedups
    if speedups.enabled:
        speedups.disable()
    assert not speedups.enabled
    accum = flow.accumulated_flow(flowdirdata)
    assert np.min(accum) >= 1  # All cells MUST be >= 1
    assert np.max(accum) == 11158
    assert np.sum(accum) == 3578615



def test_accumulated_flow_optimized(flowdirdata):
    from malstroem.algorithms import speedups
    assert speedups.available
    speedups.enable()
    assert speedups.enabled

    accum = flow.accumulated_flow(flowdirdata)
    assert np.min(accum) >= 1  # All cells MUST be >= 1
    assert np.max(accum) == 11158
    assert np.sum(accum) == 3578615


def test_watersheds(flowdirdata, bspotdata):
    speedups.disable()
    assert not speedups.enabled
    watersheds = np.copy(bspotdata)
    flow.watersheds_from_labels(flowdirdata, watersheds, unassigned=0)

    labelled_indexes = bspotdata > 0
    assert np.all(watersheds[labelled_indexes] == bspotdata[labelled_indexes])
    assert np.max(watersheds) == np.max(bspotdata)
    assert np.sum(watersheds) == 2337891

    # Check that all watersheds are a connected component
    for lbl in range(1, np.max(watersheds) + 1):
        labeled, nlabels = label.connected_components(watersheds == lbl)
        assert nlabels == 1, "Watershed {} is not a connected component".format(lbl)

def test_watersheds_optimized32(flowdirdata, bspotdata):
    speedups.enable()
    assert speedups.enabled
    watersheds = np.copy(bspotdata)
    assert watersheds.dtype == np.int32
    flow.watersheds_from_labels(flowdirdata, watersheds, unassigned=0)

    labelled_indexes = bspotdata > 0
    assert np.all(watersheds[labelled_indexes] == bspotdata[labelled_indexes])
    assert np.max(watersheds) == np.max(bspotdata)
    assert np.sum(watersheds) == 2337891

    # Check that all watersheds are a connected component
    for lbl in range(1, np.max(watersheds) + 1):
        labeled, nlabels = label.connected_components(watersheds == lbl)
        assert nlabels == 1, "Watershed {} is not a connected component".format(lbl)

def test_watersheds_optimized64(flowdirdata, bspotdata):
    speedups.enable()
    assert speedups.enabled
    watersheds = np.copy(bspotdata)
    watersheds = watersheds.astype(np.int64)
    assert watersheds.dtype == np.int64
    flow.watersheds_from_labels(flowdirdata, watersheds, unassigned=0)

    labelled_indexes = bspotdata > 0
    assert np.all(watersheds[labelled_indexes] == bspotdata[labelled_indexes])
    assert np.max(watersheds) == np.max(bspotdata)
    assert np.sum(watersheds) == 2337891

    # Check that all watersheds are a connected component
    for lbl in range(1, np.max(watersheds) + 1):
        labeled, nlabels = label.connected_components(watersheds == lbl)
        assert nlabels == 1, "Watershed {} is not a connected component".format(lbl)

def test_watersheds_optimizedfallback(flowdirdata, bspotdata):
    speedups.enable()
    assert speedups.enabled
    watersheds = np.copy(bspotdata)
    watersheds = watersheds.astype(np.uint32)
    assert watersheds.dtype == np.uint32
    flow.watersheds_from_labels(flowdirdata, watersheds, unassigned=0)

    labelled_indexes = bspotdata > 0
    assert np.all(watersheds[labelled_indexes] == bspotdata[labelled_indexes])
    assert np.max(watersheds) == np.max(bspotdata)
    assert np.sum(watersheds) == 2337891

    # Check that all watersheds are a connected component
    for lbl in range(1, np.max(watersheds) + 1):
        labeled, nlabels = label.connected_components(watersheds == lbl)
        assert nlabels == 1, "Watershed {} is not a connected component".format(lbl)