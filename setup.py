from distutils.core import setup, Extension
import numpy

shadowmap = Extension('shadowmap',
    include_dirs=[numpy.get_include()],
    sources = ['shadowmap.c'])

setup (name = 'Solsidan',
       version = '0.0',
       description = 'Where\'s the sun?',
       ext_modules = [shadowmap])
