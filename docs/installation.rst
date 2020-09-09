Installation
============
It is a bit tricky to get malstroem correctly installed. Use the precompiled Windows binary if you are on Windows, otherwise install using Anaconda.

Installing on Linux
-------------------
Use Anaconda installation if possible. Otherwise pip has been shown to work on some distributions.

Windows
-------
If you are not going to write your own python program using malstroem you can just download the precompiled standalone executable.

Download `malstroem.exe` from `releases <https://github.com/Septima/malstroem/releases>`_.

This file includes everything needed to run malstroem from a command prompt. You don't need to install anything else. Not even python.

Installing on Windows
---------------------

These instructions are for Python v2.7 64bit. Change accordingly if you prefer another version of Python.

1. Install `Microsoft Visual C++ 14.2 standalone: Build Tools for Visual Studio 2019` as described `here <https://wiki.python.org/moin/WindowsCompilers#Microsoft_Visual_C.2B-.2B-_14.2_standalone:_Build_Tools_for_Visual_Studio_2019_.28x86.2C_x64.2C_ARM.2C_ARM64.29>`_.

2. Download and install `miniconda3 64bit <https://docs.conda.io/en/latest/miniconda.html>`_ for Windows. (If you have other versions of python installed on your system, make sure to untick \"Register Anaconda as my default Python\")

3. Download the malstroem dependencies file `environment.yml <https://github.com/Septima/malstroem/raw/master/environment.yml>`_. Note the path to the downloaded file like ``C:\\Users\\asger\\Downloads\\environment.yml``.

4. From the start menu, search for and open ``Anaconda Prompt``.

5. In the Anaconda Prompt run

.. code-block:: console

   conda env create -f C:\Users\asger\Downloads\environment.yml

Where ``C:\Users\asger\Downloads\environment.yml`` is the path to your downloaded copy of ``environment.yml``.

6. In the Anaconda Prompt run

.. code-block:: console

   conda activate malstroem

This activates the ``malstroem`` environment in the current prompt. Your prompt should show something like

.. code-block:: console

   (malstroem) C:\Users\asger>

Indicating that ``malstroem`` is the currently active environment.

7. Install ``malstroem`` into the environment by running

.. code-block:: console

   pip install https://github.com/Septima/malstroem/archive/master.zip#[speedups]

8. Still in the Anaconda Prompt check that malstroem responds to

.. code-block:: console

   malstroem --help


Installing on Mac OSX
---------------------
1. Download and install `miniconda3 64bit <https://docs.conda.io/en/latest/miniconda.html>`_ for MacOSX.

2. Download the malstroem dependencies file `environment.yml <https://github.com/Septima/malstroem/raw/master/environment.yml>`_.

3. In a terminal run

.. code-block:: console

   conda env create -f path/to/environment.yml

Where ``path/to/environment.yml`` is the path to your downloaded copy of ``environment.yml``.

4. Run

.. code-block:: console

   conda activate malstroem

This activates the ``malstroem`` environment in the current prompt. Your prompt should show something like

.. code-block:: console

   (malstroem) ~$

Indicating that ``malstroem`` is the currently active environment.

5. Install ``malstroem`` into the environment by running

.. code-block:: console

   pip install https://github.com/Septima/malstroem/archive/master.zip#[speedups]

6. Still in the Anaconda Prompt check that malstroem responds to

.. code-block:: console

   malstroem --help

Install using pip
-----------------
Theoretically it should be possible to install malstroem using pip:

.. code-block:: console

   pip install cython numpy scipy gdal
   pip install git+https://github.com/Kortforsyningen/malstroem.git[speedups]


Unfortunately the above doesn't work on all platforms as malstroem uses som third party libraries and has some
optimized code which needs to be compiled for each platform.