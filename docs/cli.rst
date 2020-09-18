========================
Command Line Users Guide
========================
malstroem's command line is a single program named ``malstroem`` which has a number of subcommands. Each subcommand
exposes a malstroem process.

Available subcommands can be seen by invoking ``malstroem --help``

.. code-block:: console

    $ malstroem --help
    Usage: malstroem [OPTIONS] COMMAND [ARGS]...

      Calculate simple hydrologic models.

      To create rainfall scenarios use either the sub command 'complete' or the
      following sequence of sub command calls: filled, depths, flowdir, [accum],
      bspots, wsheds, pourpts, network, hyps, initvolumes, finalvolumes,
      finallevels and finalbluespots.

      To get help for a sub command use: malstroem subcommand --help

      Examples:
      malstroem complete -mm 20 -filter 'volume > 2.5' -dem dem.tif -outdir ./outdir/ -zresolution 0.1
      malstroem filled -dem dem.tif -out filled.tif

    Options:
      --version            Show the version and exit.
      -v, --verbosity LVL  Either CRITICAL, ERROR, WARNING, INFO or DEBUG
      --version            Show the version and exit.
      --help               Show this message and exit.

    Commands:
      accum           Calculate accumulated flow.
      bspolys         Polygonize bluespots.
      bspots          Label bluespots.
      complete        Quick option to run all processes.
      depths          Calculate bluespot depths.
      filled          Create a filled (depressionless) DEM.
      finalbluespots  Approximate extent and depths of bluespots in the final...
      finallevels     Approximate water levels of bluespots in the final state.
      finalvolumes    Bluespot fill and stream network volumes in the final...
      flowdir         Calculate surface water flow directions.
      hyps            Statistical terrain elevation measures for each bluespot.
      initvolumes     Set up initial water volumes for each watershed.
      network         Calculate stream network between bluespots.
      pourpts         Determine pour points.
      wsheds          Bluespot watersheds.

Help for a given subcommand is available by invoking ``malstroem subcommand --help``. For example:

.. code-block:: console

    $ malstroem accum --help
    Usage: malstroem accum [OPTIONS]

      Calculate accumulated flow.

      The value in an output cell is the total number of cells upstream of that
      cell. To get the upstream area multiply with cell size.

    Options:
      -flowdir PATH        Flow direction file  [required]
      -out PATH            Output file (accumulated flow)  [required]
      -v, --verbosity LVL  Either CRITICAL, ERROR, WARNING, INFO or DEBUG
      --help               Show this message and exit.

General considerations
----------------------
malstroem makes the following assumptions regarding the input

 * DEM horisontal and vertical units are meters.
 * All subsequent processing steps assume input data as output by the former processing step of malstroem.

malstroems generally does not do very much checking that input make sense together.

Vector output options
---------------------
malstroem uses `OGR <http://www.gdal.org>`_ for writing vector data. Output vector data can be tweaked using OGR
specific parameters `format`, `lco`, and `dsco`.

Example writing to `GeoPackage format <http://www.gdal.org/drv_geopackage.html>`_ from ``malstroem pourpts``:

.. code-block:: console

    $ malstroem pourpts -bluespots bluespots.tif -depths depths.tif -watersheds wsheds.tif -dem dem.tif -format gpkg -out dbfile.gpkg -layername pourpoints

For documentation of OGR features see the documentation of
`OGR formats <http://www.gdal.org/ogr_formats.html>`_.

Raster output options
---------------------
malstroem uses `GDAL <http://www.gdal.org>`_ for writing raster data. All raster data are written in
`GeoTiff <http://www.gdal.org/frmt_gtiff.html>`_ format using relevant compression.

malstroem complete
------------------
The ``complete`` subcommand gives you fast-track processing from input DEM to output rain incident including most
intermediate datasets. It basically collects the subcommands ``filled``, ``depths``, ``flowdir``, ``accum``,
``bspots``, ``wsheds``, ``pourpts``, ``network``, ``hyps``, ``initvolumes``, ``finalvolumes``, ``finallevels``
and ``finalbluespots`` into one single subcommand. See these subcommands to learn more about what happens or 
see `Complete chain of processes`_.

Arguments:
 * ``dem`` is a raster digital elevation model. Both horisontal and vertical units must be meters.
 * ``mm`` Rain incident to calculate. In mm.
 * ``zresolution`` Resolution in [m] when collecting statistics used for estimating water level for partially filled bluespots.
 * If ``accum`` is specified the accumulated flow is calculated. This takes some time and is not strictly required.
 * If ``vector`` is specified the bluespots and watersheds are vectorized. This takes some time and is not required.
 * ``filter`` allows ignoring bluespots based on their area, maximum depth and volume.
   Format: ``area > 20.5 and (maxdepth > 0.05 or volume > 2.5)``.
   Bluespots that do not pass the filter are ignored in all subsequent calculations. For instance their capacity is
   not taken into account.
 * ``outdir`` is the path to the output directory where all output files are written. This directory must exist and be
   empty.

Example:

.. code-block:: console

    $ malstroem complete -mm 20 -filter "volume > 2.5" -dem dem.tif -zresolution 0.1 -outdir ./outdir/

malstroem filled
----------------
The ``filled`` subcommand creates a filled (depressionless) DEM.

In a depressionless terrain model each cell will have at least one non-uphill path to the raster edge. This means that
a depressionless terrain model will have flat areas where it has been filled.

Arguments:
 * ``dem`` is a raster digital elevation model. Both horisontal and vertical units must be meters.

Outputs:
 * The filled DEM to a new raster

Example:

.. code-block:: console

    $ malstroem filled -dem dem.tif -out filled.tif

malstroem depths
----------------
The ``depths`` subcommand calculates bluespot depths.

Depths are calculated by subtracting the original DEM from the filled DEM

Arguments:
 * ``dem`` is the raster digital elevation model.
 * ``filled`` is the filled version of the input DEM.

Outputs:
 * A new raster with the bluespot depth in each cell. Cells not in a bluespot will have the value 0.

Example:

.. code-block:: console

    $ malstroem depths -dem dem.tif -filled filled.tif -out depths.tif

malstroem flowdir
-----------------
The ``flowdir`` subcommand calculates surface water flow directions.

This is a two step process:

Step 1:
    Fill depressions in the DEM in a way which preserves a downward slope along the flow path. This is done by requiring
    a (very) small minimum slope between cells. This results in flow over filled areas being routed to the nearest pour
    point.

Step 2:
    Flow directions for each cell. Uses a D8 flow routing algorithm: At each cell the slope to each of the 8 neighboring
    cells is calculated. The flow is routed to the cell which has the steepest slope. If multiple cells share the same maximum
    slope the algorithm picks one of these cells.

Flow direction from a cell is encoded: `Up=0`, `UpRight=1`, ..., `UpLeft=7`, `NoDirection=8`

Arguments:
 * ``dem`` is the raster digital elevation model.

Outputs:
 * A new raster where the flow direction from each cell is encoded.

Example:

.. code-block:: console

    $ malstroem depths -dem dem.tif -out flowdir.tif

malstroem accum
---------------
The subcommand ``accum`` calculates accumulated flow.

The value in an output cell is the total number of cells upstream of that cell.

Arguments:
 * ``flowdir`` is the flow direction raster.

Outputs:
 * A raster where the value in each cell is the number of cells upstream of that cell.

Example:

.. code-block:: console

    $ malstroem accum -flowdir flowdir.tif -out out.tif

malstroem bspots
----------------
The ``bspots`` subcommand identifies and labels all cells belonging to each bluespot with a unique bluespot ID.

.. note::

    * The unique ID is an integer in the range from 1 to the number of bluespots in the dataset. So bluespot IDs are
      NOT unique across different datasets.
    * IDs are not necessarily assigned the same way between different runs on the same dataset.
    * The ID 0 (zero) is used for cells which do not belong to a bluespot.

Bluespots with certain properties can be ignored by specifying a filter expression. Available properties are

``maxdepth`` which is the maximum depth of the bluespot.
``area`` which is the area of the bluespot in m2.
``volume`` which is the bluespot volume (or water capacity) in m3.

Allowed operators are ``<``, ``>``, ``==``, ``!=``, ``>=``, ``<=``, ``and`` and ``or``. Parenthises can be used to make
the expression more readable.

An example of a valid `filter`:

.. code-block:: python

    maxdepth > 0.05 and (area > 20 or volume > 0.5)

.. note::

    * Bluespots that do not pass the filter are ignored in all subsequent calculations. For instance their capacity is
      not taken into account.


Arguments:
 * ``depths`` is a raster with bluespot depths
 * ``filter`` allows ignoring bluespots based on their area, maximum depth and volume.
   Format: ``area > 20.5 and (maxdepth > 0.05 or volume > 2.5)``.
   Bluespots that do not pass the filter are ignored in all subsequent calculations. For instance their capacity is
   not taken into account.

Outputs:
 * A raster with bluespot IDs. The ID 0 (zero) is used for cells which do not belong to a bluespot.

Example:

.. code-block:: console

    $ malstroem bspots -depths depths.tif -filter "maxdepth > 0.05 and (area > 20 or volume > 0.5)" -out bluespots.tif

malstroem wsheds
----------------
The subcommand ``wsheds`` determines the local watershed of each bluespot.

All cells in the local watershed is assigned the bluespot ID.

Arguments:
 * ``bluespots`` is the bluespot ID raster.
 * ``flowdir`` is the flow direction raster.

Outputs:
 * A raster with bluespot watersheds identified by bluespot ID.

Example:

.. code-block:: console

    $ malstroem wshed -bluespots bluespots.tif -flowdir flowdir.tif -out wsheds.tif

malstroem pourpts
-----------------
The ``pourpts`` subcommand determines a pour point for each bluespot.

A pour point is the point where water leaves the blue spot when it is filled to its maximum capacity.

Pour point are determined using one of two methods:

 * Random candidate. Requires DEM only
 * Maximum accumulated flow candidate. Requires accumulated flow

The output of the two methods only differ when there are more than one pour point candidate (ie multiple threshold
cells with identical Z for a given bluespot).

Arguments:
 * ``bluespots`` is the bluespot ID raster.
 * ``depths`` is a raster with bluespot depths.
 * ``watersheds`` is a raster with local bluespot watershed identified by bluespot IDs.
 * ``dem`` the DEM. Only required if ``accum`` is not used.
 * ``accum`` accumulated flow raster. Required if ``dem`` is not used.
 * ``out`` output OGR datasource.
 * ``layername`` name of output vector layer within the output datasource.

Outputs:
 * Vector Point layer with pour points.

.. list-table:: **Pour point attributes**
   :header-rows: 1

   * - Attribute Name
     - Description
   * - bspot_id
     - Bluespot ID
   * - bspot_area
     - Bluespot area in m2
   * - bspot_vol
     - Bluespot volume (or capacity) in m3
   * - bspot_dmax
     - Maximum depth of the bluespot
   * - bspot_fumm
     - Rain needed to fill up this bluespot with water from local watershed only. In mm.
   * - wshed_area
     - Area of local bluespot watershed. In m2.
   * - cell_row
     - Raster row index of pour point location
   * - cell_col
     - Raster column index of pour point location


Example:

.. code-block:: console

    $ malstroem pourpts -bluespots bluespots.tif -depths depths.tif -watersheds wsheds.tif -dem dem.tif -out results.gpkg -layername pourpoints -format gpkg

malstroem network
-----------------
The subcommand ``network`` calculates the stream network between bluespots.

Streams are traced from the pour point of each bluespot using the flow directions raster.

A stream ends:
 * when it first enters the next downstream bluespot.
 * when it merges with another stream

When two or more streams merge a new node of type ``junction`` is inserted and a new stream is traced downstream
from the node.

Streams stop at the border of the bluespot because routing within the bluespot will otherwise happen on a synthetic
surface sloping towards the pour point. This has nothing to do with the real flow of the water.

Arguments:
 * ``bluespots`` bluespots ID raster.
 * ``flowdir`` flow direction raster.
 * ``pourpoints`` OGR vector datasource with pour points.
 * ``pourpoints_layer`` layer name within `pourpoints` datasource. Needed when datasource can have multiple layers (eg.
   a database).
 * ``out`` output OGR datasource.
 * ``out_nodes_layer`` layer name for output `nodes` layer within the output datasource.
 * ``out_streams_layer`` layer name for output `streams` layer within the output datasource

Outputs:
 * Nodes vector Point layer establishing a network
 * Streams vector LineString layer

.. list-table:: **Nodes attributes**
   :header-rows: 1

   * - Attribute Name
     - Description
   * - nodeid
     - Integer ID for each node.
   * - nodetype
     - ``pourpoint`` or ``junction``.
   * - dstrnodeid
     - ``nodeid`` of the next downstream node.
   * - bspot_id
     - Bluespot ID. NULL for nodes of type ``junction``.
   * - bspot_area
     - Bluespot area in m2. 0 (zero) for nodes of type ``junction``.
   * - bspot_vol
     - Bluespot volume (or capacity) in m3. 0 (zero) for nodes of type ``junction``.
   * - wshed_area
     - Area of local bluespot watershed. In m2. 0 (zero) for nodes of type ``junction``.
   * - cell_row
     - Raster row index of pour point location
   * - cell_col
     - Raster column index of pour point location

.. list-table:: **Streams attributes**
   :header-rows: 1

   * - Attribute Name
     - Description
   * - nodeid
     - Integer ID for starting node of the stream.
   * - dstrnodeid
     - ``nodeid`` of the next downstream node.

.. note::

    * As streams end at the border of the downstream bluespot they do not form a complete geometric network.
    * The network can be established by using the ``nodeid`` and ``dstrnodeid`` attributes.

Example:

.. code-block:: console

    $ malstroem network -bluespots bluespots.tif -flowdir flowdir.tif -pourpoints results.gpkg -pourpoints_layer pourpoints -out results.gpkg -out_nodes_layer nodes -out_streams_layer streams -format gpkg

malstroem initvolumes
---------------------
The subsommcand ``initvolumes`` sets up model input volumes for each watershed.

Water volumes are based on one of two methods:
 1. A spatially homogenuous rain incident of X mm added at all cells.
 2. A raster which specifies the amount of water added into the model at each cell. This raster may specify the amount in either mm, litres or m3.

Note:  The output from this process can be used as input for the ``finalvolumes`` process.

Arguments:
 * ``nodes`` OGR datasource containing nodes layer.
 * ``nodes_layer`` layer name within `nodes` datasource. Needed when datasource can have multiple layers (eg. a database).
 * ``mm`` Calculate volumes from a homogenuous rain incident in [mm]. Mutually exclusive with ``pr``
 * ``pr`` Raster specifying input water. Mutually exclusive with ``mm``
 * ``pr_unit`` Unit of cell values in -pr raster.
 * ``bluespots`` bluespots ID raster.
 * ``out`` output OGR datasource.
 * ``out_layer`` layer name for output layer within the output datasource.

Outputs:
 * Initvolumes Point layer which is a copy of the input ``nodes`` layer supplied with summed volume of water on each watershed in the ``inputv`` attribute.  

.. list-table:: **Initvolumes attributes**
   :header-rows: 1

   * - Attribute Name
     - Description
   * - nodeid
     - Integer ID for each node.
   * - nodetype
     - ``pourpoint`` or ``junction``.
   * - dstrnodeid
     - ``nodeid`` of the next downstream node.
   * - bspot_id
     - Bluespot ID. NULL for nodes of type ``junction``.
   * - bspot_area
     - Bluespot area in m2. 0 (zero) for nodes of type ``junction``.
   * - bspot_vol
     - Bluespot volume (or capacity) in m3. 0 (zero) for nodes of type ``junction``.
   * - wshed_area
     - Area of local bluespot watershed. In m2. 0 (zero) for nodes of type ``junction``.
   * - cell_row
     - Raster row index of pour point location
   * - cell_col
     - Raster column index of pour point location
   * - inputv
     - Calculated model input water volume of local watershed. 0 (zero) for nodes of type ``junction``. In m3.

Examples:

.. code-block:: console

    $ malstroem initvolumes -mm 20 -nodes results.gpkg -nodes_layer nodes -out results.gpkg -out_layer initvolumes -format gpkg
    $ malstroem initvolumes -pr precip_raster.tif -bluespots bluespots.tif -nodes results.gpkg -out results.gpkg -format gpkg

malstroem finalvolumes
----------------------
Calculate final bluespot fill volumes and spill volumes after infinite time.

The initial volumes of water released in the model are defined per ``node``. Initial volumes may be calculated using `malstroem initvolumes`_.
Output from `malstroem initvolumes`_ may be edited (water may be added or subtracted) before being input to this process.

Arguments:
 * ``inputvolumes`` OGR datasource containing with model input water volume per node in m3
 * ``inputvolumes_layer`` Layer name of inputvolumes layer
 * ``out`` output OGR datasource.
 * ``out_layer`` layer name for output layer within the output datasource.

Outputs:
 * Finalvolumes Point layer which is a copy of the input ``inputvolumes`` layer supplied with the calculated final state volumes.  

.. list-table:: **Finalvolumes attributes**
   :header-rows: 1

   * - Attribute Name
     - Description
   * - nodeid
     - Integer ID for each node.
   * - nodetype
     - ``pourpoint`` or ``junction``.
   * - dstrnodeid
     - ``nodeid`` of the next downstream node.
   * - bspot_id
     - Bluespot ID. NULL for nodes of type ``junction``.
   * - bspot_area
     - Bluespot area in m2. 0 (zero) for nodes of type ``junction``.
   * - bspot_vol
     - Bluespot volume (or capacity) in m3. 0 (zero) for nodes of type ``junction``.
   * - wshed_area
     - Area of local bluespot watershed. In m2. 0 (zero) for nodes of type ``junction``.
   * - cell_row
     - Raster row index of pour point location
   * - cell_col
     - Raster column index of pour point location
   * - inputv
     - Used model input water volume in m3
   * - v
     - Volume of water in the bluespot. (Sum of water input from local watershed and water flowing in from upstream).
       In m3.
   * - pctv
     - Percentage of bluespot volume (capacity) filled.
   * - spillv
     - Volume of water spilled downstream from the bluespot. In m3.

Example:

.. code-block:: console

    $ malstroem finalvolumes -inputvolumes results.gpkg -inputvolumes_layer my_scenario_input -out results.gpkg -out_layer my_scenario_final -format gpkg

malstroem hyps
--------------
Collect hypsometric (terrain elevation) statistics for each bluespot.

The output from this process is used for approximating water level and extents of partially filled bluespots.

For each bluespot these values describing the terrain within the bluespot are returned:      
 - A DEM Z value histogram with user definable bin width (resolution)     
 - Number of bins, effective upper and lower bounds of the histogram     
 - Actual minimum and maximum Z values

The ID 0 (zero) must be used for cells which do not belong to a bluespot. Statistics are not collected for this ID.

The values of the histogram are formatted as a single string using pipe ``|`` as seperator. Like: ``2|1|0|3``.

Arguments:
 * ``bluespots`` Bluespots ID raster.
 * ``dem`` The raster digital elevation model.
 * ``pourpoints`` OGR vector datasource with pour points.
 * ``pourpoints_layer`` layer name within `pourpoints` datasource. Needed when datasource can have multiple layers (eg.
   a database).
 * ``zresolution`` Resolution (or bin width) in [m] of output Z histogram. This affects the precision of the approximated values.
 * ``out`` output OGR datasource. Output is non-geometric.
 * ``out_hyps_layer`` layer name for output layer within the output datasource.

Outputs:
 * Non-geometric, tabular hypsometry layer which is a copy of the input ``pourpoints`` layer supplied with the calculated stats.

.. list-table:: **Hyps attributes**
   :header-rows: 1

   * - Attribute Name
     - Description
   * - nodeid
     - Integer ID for each node.
   * - nodetype
     - ``pourpoint`` or ``junction``.
   * - dstrnodeid
     - ``nodeid`` of the next downstream node.
   * - bspot_id
     - Bluespot ID. NULL for nodes of type ``junction``.
   * - bspot_area
     - Bluespot area in m2. 0 (zero) for nodes of type ``junction``.
   * - bspot_vol
     - Bluespot volume (or capacity) in m3. 0 (zero) for nodes of type ``junction``.
   * - wshed_area
     - Area of local bluespot watershed. In m2. 0 (zero) for nodes of type ``junction``.
   * - cell_row
     - Raster row index of pour point location
   * - cell_col
     - Raster column index of pour point location
   * - hist_counts
     - Histogram counts formatted as a single string using pipe ``|`` as seperator. Like: ``2|1|0|3``.
   * - hist_num_bins
     - Number of bins in the histogram.
   * - hist_lower_bound
     - Lower bound of the histogram in m.
   * - hist_upper_bound
     - Upper bound of the histogram in m.
   * - hist_resolution
     - Bin width in m.
   * - z_min
     - Actual minimum Z value in m.
   * - z_max
     - Actual maximum Z value in m.
   * - cell_area
     - DEM cell area in m2.

Example:

.. code-block:: console

    $ malstroem hyps -bluespots bluespots.tif -dem dem.tif -pourpoints results.gpkg -pourpoints_layer pourpoints -zresolution 0.03 -out results.gpkg -out_layer hyps

malstroem finallevels
---------------------
Approximate water levels of partially filled bluespots in the final state.

Uses statistics collected with `malstroem hyps`_ to approximate the water levels.

Note: This proces assumes that a given bluespot is filled in cell Z order (from
lowest to highest cells). No attempt is made to model how water actually
flows within the bluespot.

Arguments:
 * ``finalvols`` OGR datasource containing final state water volumes
 * ``finalvols_layer`` Layer name within `finalvols` datasource. Needed when datasource can have multiple layers.
 * ``hyps`` OGR datasource containing hypsometric stats for each bluespot as output by `malstroem hyps`_.
 * ``hyps_layer`` Layer name within `hyps` datasource.
 * ``out`` Output OGR datasource. Output is non-geometric.
 * ``out_layer`` Layer name of output.

Outputs:
 * Non-geometric, tabular layer which is a copy of the input ``finalvols`` layer supplied with the approximated water level.

.. list-table:: **Finalvolumes attributes**
   :header-rows: 1

   * - Attribute Name
     - Description
   * - nodeid
     - Integer ID for each node.
   * - nodetype
     - ``pourpoint`` or ``junction``.
   * - dstrnodeid
     - ``nodeid`` of the next downstream node.
   * - bspot_id
     - Bluespot ID. NULL for nodes of type ``junction``.
   * - bspot_area
     - Bluespot area in m2. 0 (zero) for nodes of type ``junction``.
   * - bspot_vol
     - Bluespot volume (or capacity) in m3. 0 (zero) for nodes of type ``junction``.
   * - wshed_area
     - Area of local bluespot watershed. In m2. 0 (zero) for nodes of type ``junction``.
   * - cell_row
     - Raster row index of pour point location
   * - cell_col
     - Raster column index of pour point location
   * - inputv
     - Used model input water volume in m3
   * - v
     - Volume of water in the bluespot. (Sum of water input from local watershed and water flowing in from upstream).
       In m3.
   * - pctv
     - Percentage of bluespot volume (capacity) filled.
   * - spillv
     - Volume of water spilled downstream from the bluespot. In m3.
   * - approx_z
     - Approximated water level Z in m.
   * - approx_dmax
     - Approximated maximum water depth in m.

Example:

.. code-block:: console

    $ malstroem finallevels -finalvols results.gpkg -finalvols_layer my_scenario_final -hyps results.gpkg -out results.gpkg -out_layer my_scenario_final_levels

malstroem finalbluespots
------------------------
Create rasters showing approximated bluespot extent and approximated bluespot depths in the final state.

Arguments:
 * ``bluespots`` Bluespots ID raster (Must be bluespots in the maximum extent)
 * ``dem`` The raster digital elevation model.
 * ``finallevels`` OGR datasource containing final state water Z levels as output from `malstroem finallevels`_.
 * ``finallevels_layer`` Layer name within `finallevels` datasource.
 * ``out_depths`` Output file for approximate depths raster. Optional.
 * ``out_bluespots`` Output file for approximated bluespots id raster. Optional.

Output:
 * Optionally a raster with bluespot IDs of approximated extents. The ID 0 (zero) is used for cells which do not belong to a bluespot.
 * Optionally a raster with approximated bluespot depths in m.

Example:

.. code-block:: console

  $ malstroem finalbluespots -bluespots bluespots.tif -dem dem.tif -finallevels results.gpkg -finallevels_layer my_scenario_final_levels -out_depths my_scenario_depths.tif -out_bluespots my_scenario_bspot_ids.tif

malstroem polys
---------------
Polygonize ID raster.

Create vector polygons for all connected regions of cells in the raster sharing a common ID.
    
Note that partially filled bluespots may have disconnected regions and hence there may be more than one polygon
with the same bluespot ID.

Arguments:
 * ``raster`` Raster file with IDs (bluespots or watersheds).
 * ``out`` Output OGR datasource.
 * ``layername`` Layer name within the `out` datasource.

 Outputs:
  * Polygon vector layer with one polygon for each connected region of cells in the raster sharing a common ID.

Complete chain of processes
---------------------------
The complete process from DEM to fill and spill volumes for a rain event can be calculated with the
``malstroem complete`` subcommand (see `malstroem complete`_). If you need greater control than offered by this command, you need to do the
processing in steps using the other subcommands.

The below series of process calls will produce the same results as ``malstroem complete``:

.. code-block:: console

    # Input
    DEMFILE=dem.tif

    # Raster outputs
    LABELSFILE=bluespots.tif
    FILLEDFILE=filled.tif
    DEPTHSFILE=depths.tif
    FLOWDIRFILE=flowdir.tif
    ACCUMFILE=accum.tif
    WSHEDSFILE=wsheds.tif
    FINALBLUESPOTSFILE=final_bluespots.tif
    FINALDEPTHSFILE=final_depths.tif

    # Vector outputs
    OUTVECTOR=results.gpkg
    PPTS=pourpoints
    NODES=nodes
    INITVOL=initvolumes
    FINALVOLS=finalvolumes
    HYPS=hyps
    FINALLEVELS=finallevels
    FINALPOLYGONS=finalpolygons

    # Process
    malstroem filled -dem $DEMFILE -out $FILLEDFILE

    malstroem depths -dem $DEMFILE -filled $FILLEDFILE -out $DEPTHSFILE
    
    malstroem flowdir -dem $DEMFILE -out $FLOWDIRFILE
    
    malstroem accum -flowdir $FLOWDIRFILE -out $ACCUMFILE
    
    malstroem bspots -filter "maxdepth > 0.05 and (area > 20 or volume > 0.5)" -depths $DEPTHSFILE -out $LABELSFILE
    
    malstroem wsheds -bluespots $LABELSFILE -flowdir $FLOWDIRFILE -out $WSHEDSFILE
    
    malstroem pourpts -bluespots $LABELSFILE -depths $DEPTHSFILE -watersheds $WSHEDSFILE -dem $DEMFILE -out $OUTVECTOR -layername $PPTS -format gpkg
    
    malstroem hyps -bluespots $LABELSFILE -dem $DEMFILE -pourpoints $OUTVECTOR -pourpoints_layer $PPTS -zresolution 0.1 -out $OUTVECTOR -out_hyps_layer $HYPS
    
    malstroem network -bluespots $LABELSFILE -flowdir $FLOWDIRFILE -pourpoints $OUTVECTOR -pourpoints_layer $PPTS -out $OUTVECTOR -out_nodes_layer $NODES
    
    malstroem initvolumes -nodes $OUTVECTOR -nodes_layer $NODES -mm 20 -out $OUTVECTOR -out_layer $INITVOL
    
    malstroem finalvolumes -inputvolumes $OUTVECTOR -inputvolumes_layer $INITVOL -out $OUTVECTOR -out_layer $FINALVOLS
    
    malstroem finallevels -finalvols $OUTVECTOR -finalvols_layer $FINALVOLS -hyps $OUTVECTOR -hyps_layer $HYPS -out $OUTVECTOR -out_layer $FINALLEVELS
    
    malstroem finalbluespots -bluespots $LABELSFILE -dem $DEMFILE -finallevels $OUTVECTOR -finallevels_layer $FINALLEVELS -out_depths $FINALDEPTHSFILE -out_bluespots $FINALBLUESPOTSFILE
    
    malstroem polys -raster $FINALBLUESPOTSFILE -out $OUTVECTOR -layername $FINALPOLYGONS

Accumulated flow takes time to calculate and is not always needed.

Multiple scenarios can be quickly calculated by repeating the steps ``initvolumes``, ``finalvolumes``, ``finallevels``, ``finalbluespots`` and ``polys`` for each scenario. Layer names need to be unique for each run.