# Project template for wagtail development

## Purpose

This repository contains a quick start (which I have repeated many times!) for an environment supporting a Django/Wagtail project, specifically the non-code infrastructure to build an environment for development with Wagtail. It is not dependent on any specific version of Django or Wagtail - it defaults to the "latest" release of Wagtail and installs a compatible version of Django.


## Features

* variable data is managed in a generated .env, which then become defaults for the next run
* `docker-compose-services.yml` for building and running all the stuff that’s (almost) always the same: PostgreSQL relational database for the ORM and redis nosql key store for web and session cache
* `docker-compose.yml` for running these with the containerised application

docker-compose.yml by default mounts the application directory on the host into the app container along with media and static folders, which is a suitable configuration for development. No development tools are installed within the container and it assumes that wheels exist for all packages, which is not true for some time after a new Python release.

For production use, volumes need to be modified in `docker-compose.yml`:

* remove the mount to the `${DJANGO_ROOT}` dir - the application code is already copied there in Dockerfile
* replace `${PWD}/${APP_NAME}` with `data-static` and `data-media` respectively to create and use internal docker volumes for data that need persistence. Alternatively these can be mounted anywhere on the host system.
* using a front-end or reverse proxy server (nginx or apache-http) would be required to expose correct ports and serve via https. `/media/` and `/static/` paths can be served directly from the front-end.
* uncomment `./manage.py collectstatic --no-input` in the Dockerfile and rebuild the app container `docker-compose build app`


## Pre-requisites

* git
* python 3.6+
* virtualenv (or python -m venv)
* (optional but recommended) virtualenvwrapper
* bourne compatible shell (bash works)
* svn (recommended only to export this code instead of clone) - see below<br/>_Note: "git svn" has no **export** subcommand_.
* an internet connection
* docker, any recent version should work
* docker-compose, usually comes with the docker package but can be separately installed


## Setup Scripts

This is a three step process detailed in the next section:

1. export or clone this repository
2. run the init.sh script (requires parameters for customisation)
	* installs wagtail code and python dependencies
3. run the initdb.sh script:
	* creates the database, role and user
	* does the initial database migration
	* creates the Django/Wagtail superuser
	* Builds the app container


### Quick Start

Pulling down the git repository is unnecessary (unless you plan on making a pull request). If convenient, use **svn** to *export only the required the files*:
```sh
$ svn export https://github.com/deeprave/wagtail_init/trunk targetdir
```
*targetdir* must be a direct subdirectory of the current directory for everything to work correctly.
If you don’t have svn installed, **git clone** and remove the pointless repository:
```sh
$ git clone https://github.com/deeprave/wagtail_init.git <targetdir>
$ rm -rf <targetdir>/.git
```
Change into your target dir, create or activate your python virtual environment and run the following script.


### init.sh

Initial setup is done using `./init.sh`. Variable data used by the docker-compose is saved in “.env” which caches data from previous runs.

Before starting, a python virtual environment needs to be created and activated - the script will complain if you don’t.

Recommended but not required - create the virtual environment in some convenient place outside of the directory where you have exported or cloned this template. This is a sensible default if using virtualenvwrapper which takes care of this cleanly and makes switching between virtual environments very simple. Also recommended - start with a clean virtual environment. Reusing the same one over multiple projects is almost as bad as installing everything globally.

Run `./init.sh -h` for help (shown below). This must be run from the the current folder. The django/wagtail project is created 1 level below.
```sh
init.sh: [options] [app_name]
General Options:
 -p <name>      set project name     | -S             random SECRET_KEY
 -a <name>      set app name         | -d <directory> set app subdir
 -U <url>       set site base url    | -R             generate passwords
 -h             this help message
PostgreSQL Options:                  | Redis Options:
 -i <hostname>  hostname (use IP)    |  -I <hostname>  hostname (use IP)
 -p <port>      port                 |  -P <port>      port
 -n <db_name>   database             |  -c <n>         cache db [0-15]
 -g <rolename>  app role             |  -s <n>         session db [0-15]
 -u <username>  app username         |
 -w <password>  app password         |  -E <n>         prefix default database
 -G <password>  sa postgres password |                 and redis ports [1-6]
```
The recommended usage is **`./init.sh [options] <app_name>`**. The "app_name" 
 provided is used to create a set of defaults, and otherwise uses reasonable
 defaults for most other values and allowing specific values to be overridden.
 Other options that should be used:

* `-R` generates random database passwords for both postgres and the application user.
* `-S` generates a random SECRET_KEY that is used by django.
* `-U <url>` sets the BASE_URL used by wagtail.
* Use -s <number> and/or -c <number> to offset port numbers by adding a prefix. This avoids port collisions with other docker instances on the same host.

The content of ".env" is displayed. Hit ENTER  to continue.

At this point, the basic structure and requirements are set up and almost ready to run the development server.


### initdb.sh

This is the next step - `./initdb.sh` creates and sets up the PostgreSQL database.

If the script detects that the database is not running it will be started (else all that follows will fail). When these containers are spun up for the first time on a system, images will be downloaded from hub.docker.com.

When run more than once for the same project and the postgres password has changed, the `-r` should be used to reset the previous database instance so that the postgres (system administrator) password can be set. This this can only be done when the database is initialised. This is a destructive option and should not be used if the database contains anything of value. By default, a *password is required for the postgres user* by this docker image (the latest official postgres image is used), although there are workarounds for this by trusting any connection as detailed on the [postgres docker hub page](https://hub.docker.com/_/postgres), but this is not recommended and not compatible with these scripts.


## Notes
### Database Setup

Using a role with all the required privileges and nologin is good practice when it comes to database user setup.

The login user - **NOT postgres**  - used by the application simply inherits all it needs from its parent role.  This role is also given createdb privilege to enable creating and destroying the test database when running unit tests.
