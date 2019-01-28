# theflood
## Status
Under dev

## Setup Instructions
- config.py requires the following:

  - pyscopg2 in your python 2.7 environment

  - a database named 'flood' with user 'flood' that has privileges to delete and
create tables

- Running config.py drops existing tables and recreates them with the flood schema

- The main application method lives in floodserver.py and is served over port 8000

## Update 1/26/19:

- Refactoring w/ separation of concerns and adding unit tests in order to make code more
readable and maintainable. This also includes restructuring and deleting obsolete files.
Est finish: 1/28

- Making editor pages dynamic w/ Reactjs interfaces and JavaScript. Est finish: 2/1

- Adding google authentication back. Est finish: 2/4

- Adding basic front end optimization and monitoring (relatively sized images,
  usage stat monitoring, audio support for older browsers, etc...). Est finish: 2/8

- Finish testing and publish. Note to self: I changed app from module to package.
This will have to be updated in apache config. Est finish: 2/11

  - export FLASK_APP=theflood

  - export FLASK_RUN_PORT=8000

  - flask run --host=0.0.0.0
