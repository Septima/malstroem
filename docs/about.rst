===============
About malstroem
===============

History
-------
The malstroem Project was initiated in November 2015 by SDFE who sponsored the development of a
cloudburst screening method to be carried out by Assoc. Prof. Thomas Balstrøm, Section of Geography &
Geoinformatics, Institute of Geosciences and Natural Resources, University of Copenhagen. The method
was implemented as models in ModelBuilder for ArcGIS Desktop 10.4 and documented in Balstrøm (2016,
submitted). In August 2016 SDFE asked Septima to implement Thomas’ method in a pure Python
environment based on open source technology, only, and by the end of December a first test version
programmed by Asger was available. It is this version, which is presented here.

The major difference in functionality is that the ArcGIS version was based on a transfer of derived
bluespots, watersheds and streams to ArcGIS’ geometric network environment, where the final outputs
describing the spill over in between bluespots was carried out by a custom script written in .Net and C#.
In Asger’s implementation the geometric network component was omitted.

References
----------
Balstrøm, T. & Crawford, D. (2018): Arc-Malstrøm: A 1D hydrologic screening method for stormwater assessments based on geometric networks-. Computers & Geosciences vol. 116, July 2018, pp. 64-73 (`https://doi.org/10.1016/j.cageo.2018.04.010 <https://doi.org/10.1016/j.cageo.2018.04.010>`_).

Bugs and contributions
----------------------
- Please report issues using the `issue tracker <https://github.com/Septima/malstroem/issues>`_.
- Contributions are welcome at the `project home <https://github.com/Septima/malstroem>`_.

If you are not familiar with GitHub please read this short `guide <https://guides.github.com/activities/contributing-to-open-source/>`_.


License
-------

.. code-block:: text

   Copyright (c) 2020
   Developed by Septima.dk and Thomas Balstrøm (University of Copenhagen) for the Danish Agency for
   Data Supply and Efficiency. This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by the Free Software Foundation,
   either version 2 of the License, or (at you option) any later version.
   This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
   even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PORPOSE. See the GNU Gene-
   ral Public License for more details.
   You should have received a copy of the GNU General Public License along with this program. If not,
   see http://www.gnu.org/licenses/.