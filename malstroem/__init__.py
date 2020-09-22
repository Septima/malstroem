"""malstroem

malstroem is a package for surface water calculations.

It calculates:

* Depressionless (filled, hydrologically conditioned) terrain models
* Surface flow directions
* Accumulated flow
* Blue spots
* Local watershed for each bluespot
* Pour points (point where water leaves blue spot when it is filled to its maximum capacity)
* Flow paths between blue spots
* Fill volume at specified rain incidents
* Spill over between blue spots at specified rain incidents

Important assumptions:

malstroem assumes that the terrain is an impermeable surface. This may change in a later version.

malstroem does not know the concept of time. This means that the capacity of surface streams is infinite no matter the
width or depth. Streams wont flow over. The end result is the situation after infinite time, when all water has reached
its final destination.

Water flows from one cell to one other cell (the D8 method).

"""

__version__ = "1.0.0"
__description__ = "Calculate terrain bluespots and flow"
__author__ = "Asger Skovbo Petersen"
__email__ = "asger@septima.dk"
__uri__ = "https://github.com/septima/malstroem"
__license__ = "GPL2"
