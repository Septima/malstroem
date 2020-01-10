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
from builtins import *

from .vector import transform_cell_to_world, vectorize_labels_file
from .algorithms import label, flow, fill, speedups
import numpy as np
import logging


def filterbluespots(filterfunction, cell_area, raw_bluespot_stats):
    """Apply filter function to bluespots

    Parameters
    ----------
    filterfunction : function
        Filter function applied to each raw_bluespot_stat. Returns true if bluespot passes the filter.
    cell_area : number
        Area of the cell in sqaure meters
    raw_bluespot_stats : sequence of bluespot_stats
        Each bluespot stat is a dict like object with the properties min, max, sum and count.

    Returns
    -------
    list of bool
        i'th element indicates if bluespot with id=i should be used.
    """
    keepers = []
    for s in raw_bluespot_stats:
        s_w_units = dict(min=s['min'], max=s['max'], sum=s['sum'], count=s['count'])
        s_w_units['volume'] = s['sum'] * cell_area
        s_w_units['area'] = s['count'] * cell_area
        keepers.append(filterfunction(s_w_units))
    return keepers


def assemble_pourpoints(transform, pp_pix, bluespot_stats, watershed_stats):
    """Turn data info a list of pour point objects

    Parameters
    ----------
    transform : list of six numbers
        GDAL style geotransform specifying the affine transformation parameters needed to transform row-col coordinates
        into world coordinates
    pp_pix : list of pair of numbers
        Row-col coordinate of the pourpoints. i'th element belongs to bluespot with id=i
    bluespot_stats : list of raw bluespot stats
        i'th element is a dict like objekt with stats for bluespot with id=i
    watershed_stats : list of watershed stats
        i'th element is a dict like objekt with stats for the watershed belonging to bluespot with id=i

    Returns
    -------
    list

    """
    cell_width = abs(transform[1])
    cell_height = abs(transform[5])
    cell_area = cell_width * cell_height

    pour_points = []
    for ix, stats in enumerate(zip(pp_pix, bluespot_stats, watershed_stats)):
        p = dict(bspot_id=ix)
        p['cell_row'] = int(stats[0]['row'])
        p['cell_col'] = int(stats[0]['col'])
        p['bspot_dmax'] = float(stats[1]['max'])  # Bluespot max depth
        p['bspot_area'] = stats[1]['count'] * cell_area  # Bluespot area
        p['bspot_vol'] = stats[1]['sum'] * cell_area  # Bluespot volume
        p['wshed_area'] = stats[2] * cell_area  # Local bluespot watershed area
        p['bspot_fumm'] = 1000 * p['bspot_vol'] / p['wshed_area']  # mm rain to fill bluespot with water from local wshed

        coord = transform_cell_to_world((stats[0]['row'], stats[0]['col']), transform)
        geom = dict(type='Point', coordinates=list(coord))
        geojson = dict(id=ix, geometry=geom, properties=p, type="Feature")
        pour_points.append(geojson)
    return pour_points


class BluespotTool(object):
    """Process bluespot and watersheds.

    Parameters
    ----------
    input_depths : rasterreader
        Bluespot depths
    input_flowdir : rasterreader
        Flow directions encoded like Up=0, UpRight=1, ..., UpLeft=7, NoDirection=8
    input_bluespot_filter_function : function
        Filter function applied to each raw_bluespot_stat. Returns true if bluespot passes the filter.
    output_labeled_raster : rasterwriter
        Writes the resulting bluespot labels
    output_pourpoints : vectorwriter
        Writes the resulting pourpoints
    output_watersheds_raster : rasterwriter
        Writes the resulting watersheds
    input_accum : rasterreader, optional
        Accumulated flow
    input_dem : rasterreader
        DEM [mandatory if input_accum is not present]
    output_labeled_vector : vectorwriter, optional
        Writes the vectorized bluespots
    output_watersheds_vector : vectorwriter, optional
        Writes the vectorized watersheds
    """

    def __init__(self, input_depths, input_flowdir, input_bluespot_filter_function,
                 output_labeled_raster, output_pourpoints, output_watersheds_raster,
                 input_accum=None, input_dem=None,
                 output_labeled_vector=None, output_watersheds_vector=None):
        self.input_depths = input_depths
        self.input_flowdir = input_flowdir
        self.input_bluespot_filter_function = input_bluespot_filter_function
        self.input_accum = input_accum
        self.input_dem = input_dem

        self.output_labeled_raster = output_labeled_raster
        self.output_labeled_vector = output_labeled_vector
        self.output_pourpoints = output_pourpoints
        self.output_watersheds_raster = output_watersheds_raster
        self.output_watersheds_vector = output_watersheds_vector

        assert self.input_accum or self.input_dem, "Either input_dem or input_accum must be specified"

        self.logger = logging.getLogger(__name__)

    def process(self):
        """Process the data

        Returns
        -------
        None

        """
        transform = self.input_depths.transform
        cell_width = abs(transform[1])
        cell_height = abs(transform[5])
        cell_area = cell_width * cell_height

        # Input cells must be square
        assert abs(cell_width - cell_height) < 0.01 * abs(cell_width), "Input cells must be square"

        if not speedups.enabled:
            self.logger.warning('Warning: Speedups are not available. If you have more than toy data you want them to be!')

        self.logger.info("Calculating unfiltered bluespots")
        depths = self.input_depths.read()
        raw_labeled, raw_nlabels = label.connected_components(depths)
        raw_bluespot_stats = label.label_stats(depths, raw_labeled)
        self.logger.info("Number of bluespots found before filtering: {}".format(raw_nlabels))

        self.logger.info("Calculating filtered bluespots")
        # Run filter function and get list of bools indicating which labels to keep
        keepers = filterbluespots(self.input_bluespot_filter_function, cell_area, raw_bluespot_stats)

        new_components = label.keep_labels(raw_labeled, keepers)
        del raw_labeled
        # Filtered bluespots
        labeled, nlabels = label.connected_components(new_components)
        # Recalculate stats on filtered bluespots
        bluespot_stats = label.label_stats(depths, labeled)
        del depths
        self.logger.info("Number of bluespots left after filtering: {}".format(nlabels))
        self.output_labeled_raster.write(labeled)

        if self.output_labeled_vector:
            self.logger.info("Vectorizing bluespots")
            result = vectorize_labels_file(self.output_labeled_raster.filepath)
            self.output_labeled_vector.write_geojson_features(result)

        self.logger.info("Calculating watersheds")
        watersheds = np.copy(labeled)
        flowdir = self.input_flowdir.read()
        flow.watersheds_from_labels(flowdir, watersheds, unassigned=0)
        watershed_stats = label.label_count(watersheds)
        if self.output_watersheds_raster:
            self.output_watersheds_raster.write(watersheds)
            del watersheds
        if self.output_watersheds_vector:
            self.logger.info("Vectorizing watersheds")
            result = vectorize_labels_file(self.output_watersheds_raster.filepath)
            self.output_watersheds_vector.write_geojson_features(result)

        if self.input_accum:
            self.logger.info("Calculating pour points at max accumulated flow")
            accum = self.input_accum.read()
            pp_pix = label.label_max_index(accum, labeled, nlabels)
            del accum
        elif self.input_dem:
            self.logger.info("Calculating pour points at min filled")
            dem = self.input_dem.read()
            short, diag = fill.minimum_safe_short_and_diag(dem)
            filled_no_flats = fill.fill_terrain_no_flats(dem, short, diag)
            pp_pix = label.label_min_index(filled_no_flats, labeled, nlabels)
            del filled_no_flats
        else:
            raise Exception("Either accumulated flow or DEM must be present")

        self.logger.info("Writing {} pour points".format(len(pp_pix)))
        # Put together info about pourpoints
        pour_points = assemble_pourpoints(transform, pp_pix, bluespot_stats, watershed_stats)
        feature_collection = dict(type="FeatureCollection", features=pour_points)
        self.output_pourpoints.write_geojson_features(feature_collection)

        self.logger.info("Done")
