OFX - OpenFrameworks Addon Manager
===
[![Build Status](https://travis-ci.org/HalfdanJ/ofx.svg)](https://travis-ci.org/HalfdanJ/ofx)

### What is it
This is a tool aimed to help installing and managing addons for openFrameworks. 

### Features
- Install addons easily from the commandline
- Automatic install dependency addons based on the addon_config.mk file
- Read addon dependencies from your project, and install the required addons

### Future features
- Save addon dependencies in projects

## Install
```
pip install ofx
ofx --help
``

### Install for development
- Clone the repository 

```
clone https://github.com/HalfdanJ/ofx.git
```

- Go to the new folder

```
cd ofx
```

- Install python virtualenv (a virtual python enviroment, recomended, but not required)

```
sudo pip install virtualenv
```

- Create a virtual enviroment inside the ofx tool 

```
virtualenv venv
```

- Activate the virtual enviroment  (to deactivate write `deactivate`)

```
. venv/bin/activate
``` 

- Install the ofx tool 

```
pip install --editable .
```

- Run the tool 

```
ofx --help
```

