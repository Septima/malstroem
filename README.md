malstroem
=========
Tools for screening of bluespots and water flow between bluespots.

Malstrøm is based on the ideas presented by Balstrøm and Crawford (2018).

Balstrøm, T. & Crawford, D. (2018): Arc-Malstrøm: A 1D hydrologic screening method for stormwater assessments based on geometric networks-. Computers & Geosciences vol. 116, July 2018, pp. 64-73., [doi:10.1016/j.cageo.2018.04.010](https://doi.org/10.1016/j.cageo.2018.04.010)

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
* Rain incident can be specified either as a single scalar value (x mm) or as a raster
* Fill volume at specified rain incident
* Spill over between blue spots at specified rain incident
* Approximate water level and extent of partially filled bluespots

Assumptions
-----------
malstroem makes some assumptions to simplify calculations. The most important ones which you must be aware of:

* malstroem assumes that the terrain is an impermeable surface. This may change in a later version.
* malstroem does not know the concept of time. This means that the capacity of surface streams is infinite no matter the
width or depth. Streams wont flow over. The end result is the situation after infinite time, when all water has reached
its final destination.
* Water flows from one cell to one other cell (the D8 method).
* Partially filled bluespots are assumed to be filled in cell Z order (from lowest to highest cells). No attempt is made 
to model how water actually flows within the bluespots.

Example usage
-------------
Calculate all derived data for 20mm rain incident ignoring bluespots where the maximum water depth is less than 5cm and using 20cm statistics resolution when approximating water level of partially filled bluespots:

```bash
malstroem complete -mm 20 -filter 'maxdepth > 0.05' -dem dem.tif -outdir c:\outputdirectory -zresolution 0.2
malstroem complete -mm 20 -filter 'volume > 2.5' -dem data/merged_008.22.tif -outdir ./outdir/ -zresolution 0.1
```


Installation
------------
It is a bit tricky to get malstroem correctly installed. Use the precompiled Windows binary if you are on Windows, otherwise install using Anaconda.

### Windows
If you are not going to write your own python program using malstroem you can just download the precompiled standalone executable.

Download `malstroem.exe` from [releases](https://github.com/Septima/malstroem/releases).

This file includes everything needed to run malstroem from a command prompt. You don't need to install anything else. Not even python.


### Installing on Windows
1. Install `Microsoft Visual C++ 14.2 standalone: Build Tools for Visual Studio 2019` as described [here](https://wiki.python.org/moin/WindowsCompilers#Microsoft_Visual_C.2B-.2B-_14.2_standalone:_Build_Tools_for_Visual_Studio_2019_.28x86.2C_x64.2C_ARM.2C_ARM64.29).

2. Download and install [miniconda3 64bit](https://docs.conda.io/en/latest/miniconda.html) for you Windows. (If you have other versions of python installed on your system, make sure to untick `Register Anaconda as my default Python`)

3. Download the malstroem dependencies file [environment.yml](https://github.com/Septima/malstroem/raw/master/environment.yml). Note the path to the downloaded file like `C:\Users\asger\Downloads\environment.yml`.

4. From the start menu, search for and open `Anaconda Prompt`.

5. In the Anaconda Prompt run
```
conda env create -f C:\Users\asger\Downloads\environment.yml
```
Where `C:\Users\asger\Downloads\environment.yml` is the path to your downloaded copy of `environment.yml`.

6. In the Anaconda Prompt run
```
conda activate malstroem
```
This activates the `malstroem` environment in the current prompt. Your prompt should show something like
```
(malstroem) C:\Users\asger>
```
Indicating that `malstroem` is the currently active environment.

7. Install `malstroem` into the environment by running
```
pip install https://github.com/Septima/malstroem/archive/master.zip#[speedups]
```
8. Still in the Anaconda Prompt check that malstroem responds to
```
 malstroem --help
 ```
 
### Installing on Linux or Mac OSX
1. Download and install [miniconda3 64bit](https://docs.conda.io/en/latest/miniconda.html).

2. Download the malstroem dependencies file [environment.yml](https://github.com/Septima/malstroem/raw/master/environment.yml).

3. in a terminal run
```
conda env create -f path/to/environment.yml
```
Where `path/to/environment.yml` is the path to your downloaded copy of `environment.yml`.

6. Run
```
conda activate malstroem
```
This activates the `malstroem` environment in the current prompt. Your prompt should show something like
```
(malstroem) ~$
```
Indicating that `malstroem` is the currently active environment.

7. Install `malstroem` into the environment by running
```
pip install https://github.com/Septima/malstroem/archive/master.zip#[speedups]
```
8. Still in the Anaconda Prompt check that malstroem responds to
```
 malstroem --help
 ```

### Install using pip
Theoretically it should be possible to install malstroem using pip:

```bash
pip install cython numpy scipy gdal
pip install https://github.com/Septima/malstroem/archive/master.zip#[speedups]
```

Unfortunately the above doesn't work on all platforms as malstroem uses som third party libraries and has some optimized code which needs to be compiled for each platform.


Bugs and contributions
----------------------
- Please report issues using the issue tracker: https://github.com/Septima/malstroem/issues
- Contributions are welcome at https://github.com/Septima/malstroem

If you are not familiar with GitHub please read this short [guide](https://guides.github.com/activities/contributing-to-open-source/).

License
-------
```
Copyright (c) 2020
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
