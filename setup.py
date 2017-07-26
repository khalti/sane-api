from setuptools import setup, find_packages
import sys, os
import json

# https://docs.python.org/2/distutils/setupscript.html

def read_file(filename):
	f = open(filename)
	data = f.read()
	f.close
	return data

kwargs =  {
  "name": "sane-api",
  "version": "0.1.0",
  "description": "Secure and scalable REST API.",
  "long_description": read_file("readme.md"),
  "author": "ludbek",
  "author_email": "sth.srn@gmail.com",
  "url": "https://github.com/janakitech/sane-api",
  "license": read_file("license.txt"),
  "keywords": "api rest django drf safe scalable",
  "packages": find_packages(exclude=["tests"]),
  "install_requires": json.loads(read_file("project.json"))["dependencies"],
}

setup(**kwargs)
