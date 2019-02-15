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
import numpy as np
from collections import defaultdict
from .flow import trace_downstream


def _pourpoint_enumerator(pour_points):
    """

    Parameters
    ----------
    pour_points : iterable
        Either json formatted pourpoints or iterable of cell indexes

    Yields
    -------
    pourpoint_id : int
    cell : pair of ints

    """
    for pid, pp in enumerate(pour_points):
        # json type pourpoint
        if 'properties' in pp:
            pid = pp['properties']['bspot_id']
            pp = (pp['properties']['cell_row'], pp['properties']['cell_col'])
        yield pid, pp


def _split_into_common_flow_groups(nodes, min_common_cells=2):
    """Return list of lists where all nodes in each sublist have common flow for at least 'min_common_cells'
    at the end."""
    if len(nodes) <= 1:
        return [nodes]
    reverse_index = -1 * min_common_cells
    groups = []
    unhandled_nodes = list(nodes)
    while unhandled_nodes:
        this_n = unhandled_nodes[0]
        this_geom = this_n['geometry']
        this_group = [this_n]
        unhandled_nodes.remove(this_n)
        if len(this_geom) > min_common_cells:
            for other_n in list(unhandled_nodes):
                other_geom = other_n['geometry']
                if len(other_geom) > min_common_cells and this_geom[reverse_index] == other_geom[reverse_index]:
                    this_group.append(other_n)
                    unhandled_nodes.remove(other_n)
        groups.append(this_group)
    # print ("Split {} nodes into {} groups with common flow".format(len(nodes), len(groups)))
    return groups


def _prune_common_flow(nodes, new_label_id):
    """Insert new node at flow junction and make existing nodes flow to new node.

    Nodes MUST have common flow.

    Parameters
    ----------
    nodes
    new_label_id

    Returns
    -------

    """
    # print("Pruning: {}".format(nodes))
    downstream_id = nodes[0]['downstream_id']
    # Easy access to copy of geoms
    geoms = [list(n['geometry']) for n in nodes]
    # All nodes must flow to the same downstream node
    assert all([downstream_id == n['downstream_id'] for n in nodes]), "ERROR: diff downstream ids: {}".format(nodes)
    # All flows must share at least the two last coordinates
    assert all([geoms[0][-2] == g[-2] for g in geoms])

    new_node = dict(id=new_label_id, downstream_id=downstream_id, nodetype='junction', pix=None, geometry=None)
    shared_path = []

    # As long as the last coordinate is shared between all geoms
    while all([geoms[0][-1] == g[-1] for g in geoms]):
        # Add to shared path
        shared_path.append(geoms[0][-1])
        # Remove from all geoms
        for g in geoms:
            del g[-1]

    # Reverse path to make it flow correctly
    shared_path.reverse()
    new_node['geometry'] = shared_path
    new_node['pix'] = tuple(shared_path[0])

    # Copy edited geom to nodes and set new downstream node
    for i, n in enumerate(nodes):
        n['downstream_id'] = new_node['id']
        n['geometry'] = geoms[i] + [new_node['pix']]

    # print("New node with id {}".format(new_node['id']))
    # print("New node with id {} inserted at {}: {}".format(new_node['id'], new_node['pix'], new_node))
    # print("Pruned nodes: {}".format(nodes))
    return nodes, new_node


def _untangle(nodes, next_available_label):
    """Correct network for nodes by checking for common flow and inserting junction nodes.

    Parameters
    ----------
    nodes
    new_label_id

    Returns
    -------

    """
    for group in _split_into_common_flow_groups(nodes, 2):
        if len(group) > 1:
            # Group of nodes with common flow
            untangled_nodes, new_node = _prune_common_flow(group, next_available_label)
            next_available_label = next_available_label + 1
            yield new_node, next_available_label
            for n, next_available_label in _untangle(untangled_nodes, next_available_label):
                yield n, next_available_label
        else:
            # This node doesnt have common flow with other nodes
            yield group[0], next_available_label


def next_downstream_label(flowdir, labeled, cell, background_label=None, geometry=False):
    """Find next label downstream from cell

    Parameters
    ----------
    flowdir
    labeled : 2D array
        Either labeled blue spots or labeled local watersheds of bluespots
    cell
    background_label : int
        Value of background (non-labeled) cells
    geometry : bool
        Return Path of pixel indexes from pour point to next label

    Returns
    -------

    """
    src_label = labeled[cell[0], cell[1]]
    geom = []
    for c in trace_downstream(flowdir, cell):
        lbl = labeled[c[0], c[1]]
        if geometry:
            geom.append(c)
        if not lbl == src_label:
            if background_label is None or not lbl == background_label:
                return int(lbl), geom
    return None, geom


def pourpoint_network(flowdir, labeled, pour_points, background_label=None):
    """Build pour point network relations.

    Parameters
    ----------
    flowdir
    labeled
    pour_points : list-like
        List-like structure where pour_point[n] is the pour_point of blue spot with label n
    background_label

    Returns
    -------

    """
    net = []
    for id, pp in _pourpoint_enumerator(pour_points):
        down_lbl, _ = next_downstream_label(flowdir, labeled, pp, background_label, geometry=False)
        node = dict(id=id, downstream_id=down_lbl, nodetype='pourpoint', pix=tuple(pp))
        net.append(node)
    return net


def geometric_pourpoint_network(flowdir, labeled_bluespots, pour_points, background_label=None):
    """Build pour point network including stream junctions between pour points.

    Parameters
    ----------
    flowdir
    labeled_bluespots : 2D array
        2D array of labeled bluespots
    pour_points : list-like
        List-like structure where pour_point[n] is the pour_point of blue spot with label n
    background_label

    Returns
    -------

    """
    upstream_nodes = defaultdict(list)
    for pid, pp in _pourpoint_enumerator(pour_points):
        down_lbl, geom = next_downstream_label(flowdir, labeled_bluespots, pp, background_label, geometry=True)
        node = dict(id=pid, downstream_id=down_lbl, nodetype='pourpoint', pix=tuple(pp), geometry=geom)
        upstream_nodes[down_lbl].append(node)

    # Untangle upstream nodes of each pp seperately
    next_available_label = int(np.max(labeled_bluespots) + 1)
    final_nodes = []
    for lbl, upstream in upstream_nodes.items():
        for untangled_node, next_available_label in _untangle(upstream, next_available_label):
            # print("Next label {}".format(next_available_label))
            final_nodes.append(untangled_node)
    return final_nodes
