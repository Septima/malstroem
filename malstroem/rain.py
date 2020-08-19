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


class SimpleVolumeTool(object):
    """Calculates water volume for each watershed for a simple rain event of x mm on each cell

    Parameters
    ----------
    input_nodes : vectorreader
        Nodes
    output_volumedata : vectorwriter
        Writes the output volumes data
    output_volume_attribute: str
        Name of attribute which calculated water volume is written to
    rainmm : float
        Rain (in mm).

    Attributes
    ----------
    input_nodes : list
        Nodes
    output_volumedata : vectorwriter
        Writes the output volumes data
    output_volume_attribute: str
        Name of attribute which calculated water volume is written to
    """

    def __init__(self, input_nodes, output_volumedata, output_volume_attribute, rainmm):
        self.input_nodes = input_nodes
        self.output_volumedata = output_volumedata
        self.output_volume_attribute = str(output_volume_attribute)
        self.rainmm = float(rainmm)
        self.logger = logging.getLogger(__name__)

    def process(self):
        """Process

        Returns
        -------
        None
        """

        self.logger.info("Reading input nodes")
        all_nodes = self.input_nodes.read_geojson_features()
        
        self.logger.info("Calculating rain volumes")

        self.logger.info("  {}mm".format(self.rainmm))
        for node in all_nodes:
            props = node["properties"]
            area = float(props['wshed_area'])
            wshed_water_vol = area * self.rainmm * 0.001
            props[self.output_volume_attribute] = wshed_water_vol  # Water vol from local catchment

        self.logger.info("Writing output")
        self.output_volumedata.write_geojson_features(all_nodes)

        self.logger.info("Done")
