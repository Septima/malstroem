malstroem
=========



Quick start
-------------------------

To use malstroem, do the following in an Anaconda console.

```bash
git clone https://github.com/septima/malstroem
cd malstroem
conda env create -f environment-dev.yml
conda activate malstroem
```

Then install in locally editable (``-e``) mode and run the tests.

```bash
pip install -e .[test]
py.test
```

If you want to run the speedups they need to be compiled at installation time.

```bash
    pip install -e .[test,speedups]
    py.test
```

Development
-----------
sphinx-apidoc --full -a -H malstroem -A "Asger Skovbo Petersen, Septima" -V 0.0.1 -o docs malstroem
cd docs
make html
open _build/html/index.html

Documentation
-------------

Written in restructuredText and compiled using sphinx.

After changes to `malstroem` code recreate apidoc

```bash
sphinx-apidoc --full -a -H malstroem -A "Asger Skovbo Petersen, Septima" -V 0.0.1 -o docs malstroem
```


Make html documentation:

```bash
cd docs
make html
open _build/html/index.html
```

Make pdf documentation

```bash
cd docs
make latex
cd _build/latex/
tectonic *.tex
open malstroem.pdf
```