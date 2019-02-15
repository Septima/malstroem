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

from collections import defaultdict, deque


class Network(object):
    """Stream network

    Attributes
    ----------
    nodes : list
        Nodes in the network
    root_nodes : list
        Root nodes. Nodes at the root of the stream tree. Ie nodes that do not have any downstream node
    upstream_tree : dict
        Maps a node id to the ids of nodes one step upstream
    """

    def __init__(self):
        self.nodes = []
        self.nodes_index = {}
        self.root_nodes = []
        self.upstream_tree = defaultdict(list)
        self._node_rain_values = {}

    def add_nodes(self, nodes):
        """Add a sequence of nodes to the stream network

        Parameters
        ----------
        nodes : sequence
            Nodes to add

        Returns
        -------
        None
        """
        for n in nodes:
            self.add_node(n)

    def add_node(self, node):
        """Add a single node to the stream network

        Parameters
        ----------
        node : dict
            Node to add

        Returns
        -------
        None
        """
        self.nodes.append(node)
        node_id = node['nodeid']
        downstream_id = node['dstrnodeid']
        self.nodes_index[node_id] = node
        self.upstream_tree[downstream_id].append(node_id)
        if downstream_id is None:
            self.root_nodes.append(node_id)

    def _calc_node(self, node_id, mmrain):
        node = self.nodes_index[node_id]
        area = float(node['wshed_area'])
        wshed_water_vol = area * mmrain * 0.001
        bspot_capacity = float(node['bspot_vol'])

        # How much is coming from upstream
        upstream_node_ids = self.upstream_tree[node_id]
        upstream_volume = 0.0
        if upstream_node_ids:
            upstream_event_values = [self._node_rain_values[nid] for nid in upstream_node_ids]
            upstream_volume = sum([un['spillv'] for un in upstream_event_values])

        total_water_vol = wshed_water_vol + upstream_volume
        bspot_filled_vol = min(total_water_vol, bspot_capacity)

        spillover = max(0, total_water_vol - bspot_capacity)

        event = dict(nodeid=node['nodeid'])
        event['rainv'] = wshed_water_vol  # Water vol from local catchment
        event['spillv'] = spillover  # Water vol spilled from pourpoint
        event['v'] = bspot_filled_vol  # Water vol in bluespot
        event['pctv'] = None if not bspot_capacity else 100.0 * bspot_filled_vol / bspot_capacity  # Percent filled
        self._node_rain_values[node_id] = event

    def _calc_stream_tree(self, root_node_id, mmrain):
        tree = deque()
        nodes = deque([root_node_id])
        while nodes:
            n = nodes.pop()
            tree.append(n)
            nodes.extend(self.upstream_tree[n])
        # Now tree has root at the beginning and leaves at the end
        # Process from leaves to root
        while tree:
            n = tree.pop()
            self._calc_node(n, mmrain)

    def rain_event(self, mmrain):
        """Calculate rain event

        Parameters
        ----------
        mmrain : float
            Amount of rain in mm

        Returns
        -------
        nodes : list
            All nodes in the network with event specific information added
        """
        self._node_rain_values = {}
        for rn in self.root_nodes:
            self._calc_stream_tree(rn, mmrain)
        return list(self._node_rain_values.values())
