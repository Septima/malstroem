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

from .network import Network
import logging


class RainTool(object):
    """Calculate rain events

    Parameters
    ----------
    input_nodes : list
        Nodes
    output_eventdata : vectorwriter
        Writes the output event data
    events_rainmm : list of float
        Rain events (in mm) to process.

    Attributes
    ----------
    input_nodes : list
        Nodes
    output_eventdata : vectorwriter


    """

    def __init__(self, input_nodes, output_eventdata, events_rainmm):
        self.input_nodes = input_nodes
        self.output_eventdata = output_eventdata
        self.events_rainmm = list(events_rainmm)
        self.logger = logging.getLogger(__name__)

    def process(self):
        """Process

        Returns
        -------
        None
        """

        self.logger.info("Reading input nodes")
        geojsonnodes_index = {gjn['properties']['nodeid']: gjn for gjn in self.input_nodes.read_geojson_features()}

        # Only use 'properties'
        nodes = [gjn['properties'] for gjn in geojsonnodes_index.values()]

        self.logger.info("Creating stream network")
        network = Network()
        network.add_nodes(nodes)

        # event properties to copy to geojson output
        copy_props = ['rainv', 'spillv', 'v', 'pctv']

        self.logger.info("Calculating rain events")
        for mmrain in self.events_rainmm:
            self.logger.info("  {}mm".format(mmrain))
            eventvalues = network.rain_event(mmrain)
            to_props = [self._output_property(s, mmrain) for s in copy_props]
            from_to_props = list(zip(copy_props, to_props))
            for e in eventvalues:
                node_id = e['nodeid']
                gjn = geojsonnodes_index[node_id]
                for fromprop, toprop in from_to_props:
                    gjn['properties'][toprop] = e[fromprop]

        self.logger.info("Writing output")
        self.output_eventdata.write_geojson_features(geojsonnodes_index.values())

        self.logger.info("Done")

    def _output_property(self, string, mmrain):
        return "{}_{:g}".format(string, mmrain)
