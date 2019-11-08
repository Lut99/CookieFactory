import setuptools
from distutils.extension import Extension
from Cython.Build import cythonize

if __name__ == '__main__':
    extensions = [
        Extension("PyMessage", ["src/Cython/PyMessage.pyx"],
                  include_dirs=["src/Cython"],
                  libraries=["Message.so"],
                  library_dirs=["src/C"])
    ]

    setuptools.setup(
        name="PyMessage",
        version="0.3.0",
        ext_modules=cythonize(extensions, annotate=True)
    )
