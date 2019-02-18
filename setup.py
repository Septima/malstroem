import logging
import sys
import os
import re
from codecs import open as codecs_open
from setuptools import setup, find_packages
from distutils.extension import Extension

###################################################################
NAME = "malstroem"
PACKAGES = find_packages(exclude=['ez_setup', 'examples', 'tests'])
META_PATH = os.path.join("malstroem", "__init__.py")
KEYWORDS = "bluespots surface flow"
CLASSIFIERS = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: C',
        'Programming Language :: Cython',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: GIS']
INSTALL_REQUIRES = [
          'numpy',
          'click',
          'gdal',
          'future',
          'scipy',
          'click-log==0.1.8']
EXTRAS_REQUIRE = {
          'test': ['pytest'],
          'speedups': ['cython'],
          'doc': ['sphinx_rtd_theme']
      }
ENTRY_POINTS = """
      [console_scripts]
      malstroem=malstroem.scripts.cli:cli
      """
###################################################################
logging.basicConfig()
log = logging.getLogger()

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs_open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()


META_FILE = read(META_PATH)


def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))



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
with codecs_open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(name='malstroem',
      version=find_meta("version"),
      description=find_meta("description"),
      long_description=long_description,
      classifiers=CLASSIFIERS,
      keywords=KEYWORDS,
      author=find_meta("author"),
      author_email=find_meta("email"),
      url=find_meta("uri"),
      license=find_meta("license"),
      packages=PACKAGES,
      include_package_data=True,
      zip_safe=False,
      install_requires=INSTALL_REQUIRES,
      extras_require=EXTRAS_REQUIRE,
      entry_points=ENTRY_POINTS,
      ext_modules=ext_modules,
      )
