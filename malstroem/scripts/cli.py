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

import click
import click_log
import sys

import malstroem
from malstroem.scripts import complete
from malstroem.scripts import dem
from malstroem.scripts import bluespot
from malstroem.scripts import stream
from malstroem.scripts import initvolume
from malstroem.scripts import finalstate
from malstroem.scripts import hyps


@click.group("malstroem")
@click.version_option()
@click_log.simple_verbosity_option()
@click.version_option(
    version=malstroem.__version__
)  # , prog_name="fire", help="Vis versionsnummer")
@click_log.init()
def cli():
    """Calculate simple hydrologic models.

    To create rainfall scenarios use either the sub command 'complete' or the following sequence of sub command calls:
    filled, depths, flowdir, [accum], bspots, wsheds, pourpts, network, hyps, initvolumes, finalvolumes, finallevels
    and finalbluespots.

    To get help for a sub command use: malstroem subcommand --help

    \b
    Examples:
    malstroem complete -mm 20 -filter "volume > 2.5" -dem dem.tif -outdir ./outdir/ -zresolution 0.1
    malstroem filled -dem dem.tif -out filled.tif

    """
    pass


# complete
cli.add_command(complete.process_all)

# dem
cli.add_command(dem.process_filled)
cli.add_command(dem.process_depths)
cli.add_command(dem.process_flowdir)
cli.add_command(dem.process_accum)

# bluespot
cli.add_command(bluespot.process_bspots)
cli.add_command(bluespot.process_wsheds)
cli.add_command(bluespot.process_pourpoints)
cli.add_command(bluespot.process_polys)

# stream
cli.add_command(stream.process_network)

# volume
cli.add_command(initvolume.process_volumes)

# net
cli.add_command(finalstate.process_net)

# hyps
cli.add_command(hyps.process_hypsometry)

# final levels
cli.add_command(finalstate.process_finallevels)

# final state bluespots and depths
cli.add_command(finalstate.process_bluespots)

# If run in pyinstaller
if getattr(sys, "frozen", False):
    cli(sys.argv[1:])
