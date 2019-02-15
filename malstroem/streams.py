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

from malstroem.vector import transform_cell_to_world
from malstroem.algorithms import net

import logging


class StreamTool(object):
    """Determine upstream/downstream relationship between pourpoints

    Parameters
    ----------
    input_pourpoints : vectorreader
        Pour points
    input_bluespots : rasterreader
        Bluespot ids raster
    input_flowdir : rasterreader
        Flow direction raster
    output_nodes : vectorwriter
        Writes resulting nodes
    output_streams : vectorwriter, optional
        Writes streams
    """

    def __init__(self, input_pourpoints, input_bluespots, input_flowdir,
                 output_nodes, output_streams=None):
        self.input_pourpoints = input_pourpoints
        self.input_bluespots = input_bluespots
        self.input_flowdir = input_flowdir

        self.output_nodes = output_nodes
        self.output_streams = output_streams

        self.logger = logging.getLogger(__name__)

    def process(self):
        """Process

        Returns
        -------
        None
        """

        self.logger.info("Read input data")
        transform = self.input_flowdir.transform
        cell_width = abs(transform[1])
        cell_height = abs(transform[5])
        cell_area = cell_width * cell_height
        flowdir = self.input_flowdir.read()
        labeled_bluespots = self.input_bluespots.read()
        pourpoints = self.input_pourpoints.read_geojson_features()

        pourpoints_pix = [(pp['properties']['cell_row'], pp['properties']['cell_col']) for pp in pourpoints]

        self.logger.info("Processing stream network")
        if self.output_streams is not None:
            nodes = net.geometric_pourpoint_network(flowdir, labeled_bluespots, pourpoints_pix, 0)
        else:
            nodes = net.pourpoint_network(flowdir, labeled_bluespots, pourpoints_pix, 0)

        self.logger.info("Writing {} nodes".format(len(nodes)))
        pp_index = {pp['properties']['bspot_id']: pp for pp in pourpoints}

        # Create geojson point nodes and copy info from pourpoints where node is a pourpoint
        geojson_nodes = []
        for n in nodes:
            props = dict()
            props['nodeid'] = n['id']
            props['dstrnodeid'] = n['downstream_id']
            props['nodetype'] = n['nodetype']
            props['cell_row'] = n['pix'][0]
            props['cell_col'] = n['pix'][1]
            # Default properties for junction nodes
            props['bspot_id'] = None
            props['bspot_area'] = 0.0
            props['bspot_vol'] = 0.0
            props['wshed_area'] = 0.0

            # Copy info from pourpoint if present
            ppoint = pp_index.get(n['id'], None)
            if ppoint:
                props['bspot_id'] = ppoint['properties']['bspot_id']
                props['bspot_area'] = ppoint['properties']['bspot_area']
                props['bspot_vol'] = ppoint['properties']['bspot_vol']
                props['wshed_area'] = ppoint['properties']['wshed_area']

            # Geometry
            coord = transform_cell_to_world(n['pix'], transform)
            geom = dict(type='Point', coordinates=list(coord))
            geojson = dict(id=n['id'], geometry=geom, properties=props)
            geojson_nodes.append(geojson)

        self.output_nodes.write_geojson_features(geojson_nodes)

        if self.output_streams:
            geojson_streams = []
            for n in nodes:
                if n['geometry']:
                    props = dict()
                    props['nodeid'] = n['id']
                    props['dstrnodeid'] = n['downstream_id']

                    # Transform coords
                    world_coords = [transform_cell_to_world(c, transform) for c in n['geometry']]
                    geom = dict(type='LineString', coordinates=list(world_coords))
                    geojson = dict(id=n['id'], geometry=geom, properties=props)
                    geojson_streams.append(geojson)
            self.output_streams.write_geojson_features(geojson_streams)
