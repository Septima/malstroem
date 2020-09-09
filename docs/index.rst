.. malstroem documentation master file, created by
   sphinx-quickstart on Wed Jan  4 13:07:28 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

============================================================================
malstroem
============================================================================
Tools for screening of bluespots and water flow between bluespots

Features
--------
malstroem provides command line tools and a python api to calculate:

* Depressionless (filled, hydrologically conditioned) terrain models
* Surface flow directions
* Accumulated flow
* Blue spots
* Local watershed for each bluespot
* Pour points (point where water leaves blue spot when it is filled to its maximum capacity)
* Flow paths between blue spots
* Rain incident can be specified either as a single scalar value (x mm) or as a raster
* Fill volume at specified rain incident
* Spill over between blue spots at specified rain incident
* Approximate water level and extent of partially filled bluespots

Assumptions
-----------
malstroem makes some assumptions to simplify calculations. The most important ones which you must be aware of:

.. note::

    * malstroem assumes that the terrain is an impermeable surface.
    * malstroem does not know the concept of time. This means that the capacity of surface streams is infinite no matter
      the width or depth. Streams won´t flow over along their sides. The end result is the situation after infinite time,
      when all water has reached its final destination.
    * Water flows from one cell to one other neighbour cell (the D8 method).
    * The DEM used must cover an entire drainage basin (or more basins) in order to estimate correct stream flows from
      all upstream sub-watersheds within the basins.
    * Partially filled bluespots are assumed to be filled in cell Z order (from lowest to highest cells). No attempt is made 
      to model how water actually flows within the bluespots.

Example usage
-------------
Calculate all derived data for 20mm rain incident ignoring bluespots where the maximum water depth is less than 5cm and using 
20cm statistics resolution when approximating water level of partially filled bluespots:

.. code-block:: console

   malstroem complete -r 10 -r 30 -filter "maxdepth > 0.5" -vector -dem dem.tif -outdir c:\outputdirectory -zresolution 0.2

The project
-----------
.. toctree::
   :maxdepth: 2

   about


Installation
------------
.. toctree::
   :maxdepth: 2

   installation

Command line interface
----------------------
.. toctree::
   :maxdepth: 2

   cli

API documentation
-----------------
.. toctree::
   :maxdepth: 2

   api/malstroem




Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
