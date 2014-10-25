OFX - OpenFrameworks Addon Manager
===
[![Build Status](https://travis-ci.org/HalfdanJ/ofx.svg)](https://travis-ci.org/HalfdanJ/ofx)
### What is it
This is a tool aimed to help installing and managing addons for openFrameworks. 

### Features
- Install addons
- Automatic install dependency addons based on the addon_config.mk file

### Future features
- Save addon dependencies in projects
- Read addon dependencies and install addons

### Install for development
- Clone the repository and cd to it
- Install python virtualenv `sudo pip install virtualenv`
- Create a virtual enviroment inside the ofx tool `virtualenv venv`
- Activate the virtual enviroment `. venv/bin/activate` (to deactivate write `deactivate`)
- Install the ofx tool `pip install --editable .`
- Run the tool `ofx --help`

