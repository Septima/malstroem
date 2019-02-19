malstroem
=========
Tools for screening of bluespots and water flow between bluespots.

Malstrøm is based on the ideas presented by Balstrøm and Crawford (2018).

Balstrøm, T., Crawford, D., 2018, Arc-Malstrøm: A 1D hydrologic screening method for stormwater assessments based on geometric networks, Computers & Geosciences, vol. 116, pp 64-73, [doi:10.1016/j.cageo.2018.04.010](https://doi.org/10.1016/j.cageo.2018.04.010)

[![Build status](https://ci.appveyor.com/api/projects/status/hhnnd65moi0fl71w/branch/master?svg=true)](https://ci.appveyor.com/project/Septima/malstroem/branch/master)

### Note:
This is a fork of the original [malstroem repository](https://github.com/Kortforsyningen/malstroem). It seems like the original malstroem repo is not maintained anymore. This repo is intended to be a maintained version of malstroem.

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
* Fill volume at specified rain incidents
* Spill over between blue spots at specified rain incidents

Assumptions
-----------
malstroem makes some assumptions to simplify calculations. The most important ones which you must be aware of:

* malstroem assumes that the terrain is an impermeable surface. This may change in a later version.
* malstroem does not know the concept of time. This means that the capacity of surface streams is infinite no matter the
width or depth. Streams wont flow over. The end result is the situation after infinite time, when all water has reached
its final destination.
* Water flows from one cell to one other cell (the D8 method).

Example usage
-------------
Calculate all derived data for 10mm and 30mm rain incidents ignoring bluespots where the maximum water depth is less than 5cm:

```bash
malstroem complete -r 10 -r 30 -filter 'maxdepth > 0.5' -dem dem.tif -outdir c:\outputdirectory
```


Installation
------------

Theoretically:

```bash
pip install cython numpy scipy gdal
pip install https://github.com/Septima/malstroem/archive/master.zip#[speedups]
```

Unfortunately the above doesn't work on all platforms as malstroem uses som third party libraries and has some optimized code which needs to be compiled for each platform. This method should work on most linux distributions.

### Windows
If you are not going to write your own python program using malstroem you can just download the precompiled standalone executable.

Download `malstroem.exe` from [releases](https://github.com/Septima/malstroem/releases).

This file includes everything needed to run malstroem from a command prompt. You don't need to install anything else. Not even python.

### Installing on Windows for programming
If you want to use malstroem in your own python program you have to install it.

These instructions are for Python v3.7 64bit. Change accordingly if you prefer another version of Python.

 1. [Download](https://www.python.org/downloads/windows/) and install latest Python 3.7 "Windows x86-64 installer" 
 2. [Download](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2017) and install "Microsoft Build Tools for Visual Studio 2017"
 3. Go to [Christoph Gohlke](http://www.lfd.uci.edu/~gohlke/pythonlibs/) and download `numpy`, `gdal`, `cython` and `scipy` wheels matching your python. For Python 3.7 64 bit it should be files ending in `cp37‑cp37m‑win_amd64.whl`
 4. Open windows command prompt and go to the scripts folder in your Python installation. In a defaut install it should be something like
  ```
  cd c:\Python37\scripts
  ```
 5. For each of the 4 wheel files downloaded from Gholke (starting with `numpy`) install it with pip like this:
 ```
 pip install c:\downloads\numpy‑1.15.4+mkl‑cp37‑cp37m‑win_amd64.whl
 ```
 6. Install malstroem
 ```
 pip install https://github.com/Septima/malstroem/archive/master.zip#[speedups]
 ```
 7. Still in the scripts folder of your Python (c:\python37\scripts) check that malstroem responds to
 ```
 malstroem --help
 ```
 
### Installing on Mac OSX
 The biggest problem on OSX is getting GDAL to work. One known solution is via [homebrew](http://brew.sh/)
 1. Make sure homebrew is installed and you know how to use its Python (See for instance [this guide](http://docs.python-guide.org/en/latest/starting/install/osx/))
 2. Install GDAL and its Python bindings
 
  ```
  brew install gdal
  ```
 3. Make sure you use the homebrew Python and install malstroem and its dependencies (If you are using a virtualenv create       it using `--system-site-packages`) 
 
  ```
  pip install cython numpy scipy
  pip install git+https://github.com/Kortforsyningen/malstroem.git[speedups]
  ```

Bugs and contributions
----------------------
- Please report issues using the issue tracker: github.com/Kortforsyningen/malstroem/issues
- Contributions are welcome at github.com/Kortforsyningen/malstroem/

If you are not familiar with GitHub please read this short [guide](https://guides.github.com/activities/contributing-to-open-source/).

License
-------
```
Copyright (c) 2019
Developed by Septima.dk and Thomas Balstrøm (University of Copenhagen) for the Danish Agency for
Data Supply and Efficiency. This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by the Free Software Foundation,
either version 2 of the License, or (at you option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Gene-
ral Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not,
see http://www.gnu.org/licenses/.
```
