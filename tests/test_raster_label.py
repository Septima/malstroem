import numpy as np
import pytest

from malstroem.algorithms import label, speedups
from data.fixtures import filleddata, fillednoflatsdata, bspotdata, depthsdata


def test_connected_components(filleddata, fillednoflatsdata):
    diff = fillednoflatsdata - filleddata
    labeled, nlabels = label.connected_components(diff)
    assert labeled.dtype == np.int32
    assert nlabels == 525
    background = labeled == 0
    assert np.sum(background) == 40029
    # This value depend on connected_components to label the same way every time.
    assert np.sum(labeled) == 1561377


def test_label_stats(filleddata, bspotdata):
    speedups.disable()
    assert not speedups.enabled
    stats = label.label_stats(filleddata, bspotdata)
    assert len(stats) == np.max(bspotdata) + 1
    assert np.all(stats[:]['min'] <= stats[:]['max'])
    assert np.sum(stats[:]['count']) == bspotdata.shape[0] * bspotdata.shape[1]
    assert np.min(stats[:]['min']) == np.min(filleddata)
    assert np.max(stats[:]['max']) == np.max(filleddata)

    # Check label with most cells
    lbl = np.argmax(stats[:]['count'])
    lblix = bspotdata == lbl
    assert stats[lbl]['min'] == np.min(filleddata[lblix])
    assert stats[lbl]['max'] == np.max(filleddata[lblix])
    np.testing.assert_almost_equal(stats[lbl]['sum'], np.sum(filleddata.astype(np.float64)[lblix]))
    assert stats[lbl]['count'] == np.sum(lblix)


def test_label_stats_optimized(filleddata, bspotdata):
    speedups.enable()
    assert speedups.enabled
    stats = label.label_stats(filleddata, bspotdata)
    assert len(stats) == np.max(bspotdata) + 1
    assert np.all(stats[:]['min'] <= stats[:]['max'])
    assert np.sum(stats[:]['count']) == bspotdata.shape[0] * bspotdata.shape[1]
    assert np.min(stats[:]['min']) == np.min(filleddata)
    assert np.max(stats[:]['max']) == np.max(filleddata)

    # Check label with most cells
    lbl = np.argmax(stats[:]['count'])
    lblix = bspotdata == lbl
    assert stats[lbl]['min'] == np.min(filleddata[lblix])
    assert stats[lbl]['max'] == np.max(filleddata[lblix])
    np.testing.assert_almost_equal(stats[lbl]['sum'], np.sum(filleddata.astype(np.float64)[lblix]))
    assert stats[lbl]['count'] == np.sum(lblix)

def test_compare_label_stats(filleddata, bspotdata):
    speedups.disable()
    assert not speedups.enabled
    stats = label.label_stats(filleddata, bspotdata)
    speedups.enable()
    assert speedups.enabled
    statsopt = label.label_stats(filleddata, bspotdata)

    for s, so in zip(stats, statsopt):
        assert s == so

def test_label_min_index(fillednoflatsdata, bspotdata):
    speedups.disable()
    assert not speedups.enabled
    min_ix = label.label_min_index(fillednoflatsdata, bspotdata)
    assert len(min_ix) == np.max(bspotdata) + 1

def test_label_min_index_optimized(fillednoflatsdata, bspotdata):
    speedups.enable()
    assert speedups.enabled
    min_ix = label.label_min_index(fillednoflatsdata, bspotdata)
    assert len(min_ix) == np.max(bspotdata) + 1

def test_compare_label_min_index(fillednoflatsdata, bspotdata):
    speedups.disable()
    assert not speedups.enabled
    min_ix = label.label_min_index(fillednoflatsdata, bspotdata)
    speedups.enable()
    assert speedups.enabled
    min_ix_opt = label.label_min_index(fillednoflatsdata, bspotdata)
    assert len(min_ix) == len(min_ix_opt)
    for m, mopt in zip(min_ix, min_ix_opt):
        for v, vopt in zip(m, mopt):
            assert np.isclose(v, vopt)


def test_label_data(bspotdata, depthsdata):
    speedups.disable()
    assert not speedups.enabled
    data_per_label = label.label_data(depthsdata, bspotdata, nlabels=None,background=0)
    assert len(data_per_label) > 0
    assert len(data_per_label) == np.max(bspotdata) + 1
    assert len(data_per_label[0]) == 0, "Background data list should be empty"
    for e, values_list in enumerate(data_per_label[1:]):
        assert len(values_list) > 0, f"label {e+1} has zero data values"
    
    # Sum collected values
    sums = [sum(x) for x in data_per_label]
    global_sum = sum(sums)

    # Make sum in numpy using rasters only
    np_sum = np.sum(depthsdata[ bspotdata != 0 ])
    assert pytest.approx(np_sum) == global_sum, "Returned values do not sum correctly"