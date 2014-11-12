#coding: utf8

from distutils.core import setup

setup(
    name = "noue",
    packages = ["noue"],
	package_data={'noue': ['include/*.*']},
    version = "0.0.0",
    description = "Python C-language Emulator",
    author = "Kenji Ohnishi",
    author_email = "",
    url = "",
    download_url = "",
    keywords = ["encoding", "i18n", "xml"],
    classifiers = [
        "Programming Language :: Python :: 3.4",
        #"Development Status :: 4 - Beta",
        #"Environment :: Other Environment",
        #"Intended Audience :: Developers",
        #"License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        #"Operating System :: OS Independent",
        #"Topic :: Software Development :: Libraries :: Python Modules",
        #"Topic :: Text Processing :: Linguistic",
        ],
    long_description = ""
)
