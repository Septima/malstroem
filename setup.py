import logging
import sys
from codecs import open as codecs_open
from setuptools import setup, find_packages
from distutils.extension import Extension
import malstroem

logging.basicConfig()
log = logging.getLogger()

# --------------------------------------------------------------------------------
# Use Cython if available.
include_dirs = []
library_dirs = []
libraries = []
extra_link_args = []
ext_modules = []

try:
    import numpy

    include_dirs.append(numpy.get_include())
except ImportError:
    log.critical("Numpy and its headers are required to run setup(). Exiting.")
    sys.exit(1)

try:
    from Cython.Build import cythonize
except ImportError:
    cythonize = None
    log.warning("Cython not available. Module will work, but will be very very slow")

if cythonize:
    ext_options = dict(
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        libraries=libraries,
        extra_link_args=extra_link_args)

    # Make html annotation
    import Cython.Compiler.Options

    Cython.Compiler.Options.annotate = True

    ext_modules = cythonize([
        Extension('malstroem.algorithms.speedups._fill',
                  ['malstroem/algorithms/speedups/_fill.pyx'], **ext_options),
        Extension('malstroem.algorithms.speedups._flow',
                  ['malstroem/algorithms/speedups/_flow.pyx'], **ext_options),
        Extension('malstroem.algorithms.speedups._label',
                  ['malstroem/algorithms/speedups/_label.pyx'], **ext_options)
    ])
# --------------------------------------------------------------------------------


# Get the long description from the relevant file
with codecs_open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(name='malstroem',
      version=malstroem.__version__,
      description=u"Calculate terrain bluespots and flow",
      long_description=long_description,
      classifiers=[],
      keywords='',
      author=u"Asger Skovbo Petersen",
      author_email='asger@septima.dj',
      url='https://github.com/septima/malstroem',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'numpy',
          'click',
          'gdal',
          'future',
          'scipy',
          'click-log==0.1.8'
      ],
      extras_require={
          'test': ['pytest'],
          'speedups': ['cython'],
          'doc': ['sphinx_rtd_theme']
      },
      entry_points="""
      [console_scripts]
      malstroem=malstroem.scripts.cli:cli
      """,
      ext_modules=ext_modules,
      )
