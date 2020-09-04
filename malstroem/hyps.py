# coding=utf-8
# -------------------------------------------------------------------------------------------------
# Copyright (c) 2020
# Developed by Septima.dk. This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free Software Foundation,
# either version 2 of the License, or (at you option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PORPOSE. See the GNU Gene-
# ral Public License for more details.
# You should have received a copy of the GNU General Public License along with this program. If not,
# see http://www.gnu.org/licenses/.
# -------------------------------------------------------------------------------------------------
import numpy as np
import logging
from collections import namedtuple

from malstroem.algorithms import speedups
from malstroem.algorithms.label import label_stats, label_data

logger = logging.getLogger(__name__)

HistogramBinsInfo = namedtuple("HistogramBinsInfo", ["num_bins", "lower_bound", "upper_bound", "resolution"])
Histogram = namedtuple("Histogram", ["counts", "bins"])
HypsometryStats = namedtuple("HypsometryStats", ["zhistogram", "zmin", "zmax"])

def bluespot_hypsometry_io(bluespots_reader, dem_reader, pourpoints_reader, resolution, hyps_writer):
    resolution = float(resolution)
    assert resolution > 0, "Resolution must be greater than zero"

    assert bluespots_reader.shape == dem_reader.shape, "Dimension mismatch between dem and bluespot rasters"
    for r0, r1 in zip(bluespots_reader.resolution, dem_reader.resolution):
        np.testing.assert_almost_equal(r0, r1, err_msg= "Resolution mismatch between dem and bluespot rasters")
    
    cell_area = bluespots_reader.resolution[0] * bluespots_reader.resolution[1]

    logger.debug("Reading input data")
    bluespotlabels = bluespots_reader.read()
    dem = dem_reader.read()
    pourpoints_index = {gjn['properties']['bspot_id']: gjn for gjn in pourpoints_reader.read_geojson_features()}

    labels_max = np.max(bluespotlabels)
    vector_labels_max = max([x["properties"]["bspot_id"] for x in pourpoints_index.values()])
    assert labels_max == vector_labels_max, f"Number of labels in bluespot raster and pourpoints vector layer does not match {labels_max} vs {vector_labels_max}"

    for bs_id, stats in bluespot_hypsometry_stats(bluespotlabels, dem, resolution, labels_max, background=0):
        pp = pourpoints_index[bs_id]
        add_props = _hypsometrystats_to_flatdict(stats)
        pp["properties"].update(add_props)
        pp["properties"]["cell_area"] = cell_area

    logger.debug("Writing features")
    hyps_writer.write_geojson_features(pourpoints_index.values())    

def bluespot_hypsometry_stats(bluespotlabels, dem, resolution, labels_max = None, background=0):
    if not speedups.enabled:
        logger.warning('Warning: Speedups are not available. If you have more than toy data you want them to be!')

    if labels_max is None:
        labels_max = np.max(bluespotlabels)

    logger.debug("Calculate z stats for each bluespot")
    label_z_stats = label_stats(dem, bluespotlabels, labels_max)

    logger.debug("Collecting label data values")
    label_data_values = label_data(dem, bluespotlabels, labels_max, background=background)

    logger.debug("Calculating histograms")
    for label, data in enumerate(label_data_values):
        bins = histogram_bins(label_z_stats[label]["min"], label_z_stats[label]["max"], resolution)
        counts, _ = np.histogram(data, bins.num_bins, (bins.lower_bound, bins.upper_bound))
        yield label, HypsometryStats(Histogram(counts, bins), label_z_stats[label]["min"], label_z_stats[label]["max"])

    
def cumulative_volume(h : Histogram, cell_area : float):
    """Calculates the bluespot volume below each bin in the z histogram"""
    cumulative = np.cumsum(h.counts, dtype=np.float64)
    step_volumes = cell_area * h.bins.resolution * cumulative
    # First bin is bluespot floor
    volumes = step_volumes - step_volumes[0]
    # Cumulative volumes per bin
    cum_volumes = np.cumsum(volumes)
    return cum_volumes


def histogram_bins(zmin, zmax, resolution):
    scale = 1 / resolution
    min_scaled = int(zmin * scale)
    max_scaled = int(zmax * scale)
    num_bins = max_scaled - min_scaled + 1
    lower_bound = min_scaled * resolution
    upper_bound = lower_bound + num_bins * resolution
    bins = HistogramBinsInfo(num_bins, lower_bound, upper_bound, resolution)
    return bins


def _hypsometrystats_to_flatdict(hyps):
    return {
        "hist_counts": "|".join([str(x) for x in hyps.zhistogram.counts]),
        "hist_num_bins" : hyps.zhistogram.bins.num_bins,
        "hist_lower_bound" : hyps.zhistogram.bins.lower_bound, 
        "hist_upper_bound" : hyps.zhistogram.bins.upper_bound, 
        "hist_resolution" :  hyps.zhistogram.bins.resolution,
        "zmin": hyps.zmin,
        "zmax": hyps.zmax,
    }
    

def hypsometrystats_from_flatdict(d):
    bins = HistogramBinsInfo(int(d["hist_num_bins"]), float(d["hist_lower_bound"]), float(d["hist_upper_bound"]), float(d["hist_resolution"]))
    counts = [int(x) for x in d["hist_counts"].split("|")]
    h = Histogram(counts, bins)
    zmin = float(d["zmin"])
    zmax = float(d["zmax"])
    return HypsometryStats(h, zmin, zmax)


def assert_hypsometrystats_valid(h):
    assert len(h.zhistogram.counts) == h.zhistogram.bins.num_bins, "Mismatch between num_bins and actual counts"
    assert h.zhistogram.bins.upper_bound >= h.zhistogram.bins.lower_bound, "Upper bound less than lower bound"
    num_bins = (h.zhistogram.bins.upper_bound - h.zhistogram.bins.lower_bound) / h.zhistogram.bins.resolution
    np.testing.assert_almost_equal(h.zhistogram.bins.num_bins, num_bins, err_msg="Mismatch between num_bins and bounds/resolution")